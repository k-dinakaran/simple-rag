import os
import time
import json
import logging
import asyncio
from typing import Dict, Any

import google.generativeai as genai

# Import pipeline modules
from embedding import EmbeddingModel
from vector_store import VectorStore
from cache import RedisCache

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

TOP_K = 3


class RAGPipeline:
    """
    RAG Pipeline with reranking, observability, structured logging,
    deduplication, and Redis caching.
    """

    def __init__(self):
        """
        Initializes embedding model, reranker, vector store, LLM, and Redis cache.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        genai.configure(api_key=api_key)

        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore()
        self.llm_model = genai.GenerativeModel('gemini-2.5-flash')

        try:
            self.cache = RedisCache()
            logger.info(json.dumps({"event": "cache_initialized", "status": "enabled"}))
        except Exception as e:
            logger.warning(json.dumps({"event": "cache_init_failed", "error": str(e)}))
            self.cache = None

    def generate_answer(self, query: str, chunks: list[str]):
        """
        Generates an LLM answer from provided context chunks.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        if not chunks:
            yield "I don't have enough context to answer this."
            return

        context = "\n\n".join(chunks)

        prompt = f"""
You are an enterprise assistant.

Answer in a detailed and structured format.

Context:
{context}

Question:
{query}

Instructions:
- Provide detailed explanation
- Use bullet points
- Minimum 5 lines response
"""

        try:
            logger.info(json.dumps({
                "event": "streaming_started",
                "query": query
            }))
            
            generation_start = time.perf_counter()

            response = self.llm_model.generate_content(
                prompt,
                stream=True,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            response_text = ""

            for chunk in response:
                if chunk.candidates:
                    parts = chunk.candidates[0].content.parts
                    
                    for part in parts:
                        if hasattr(part, "text"):
                            token = part.text
                            response_text += token
        
                            logger.info(json.dumps({
                                "event": "token_streamed",
                                "token_length": len(token)
                            }))
        
                            yield token

            logger.info(json.dumps({
                "event": "streaming_complete",
                "total_length": len(response_text)
            }))
            
            generation_time = time.perf_counter() - generation_start
            
            logger.info(json.dumps({
                "event": "generation_complete",
                "time": generation_time
            }))

        except Exception as e:
            logger.error(json.dumps({"event": "api_error", "error": str(e)}))
            raise e

    async def embed_async(self, query):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.embedding_model.embed_query,
            query
        )

    async def retrieve_async(self, query_embedding):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.vector_store.similarity_search,
            query_embedding,
            TOP_K
        )

    async def query(self, query: str) -> dict:
        """
        Executes the full RAG query pipeline with caching, latency tracking,
        and structured logging.

        Flow:
          1. Check Redis cache → return cached response on hit
          2. Embed query
          3. Retrieve top-10 chunks from vector store
          4. Deduplicate
          5. Rerank → top 3
          6. Generate answer via Gemini
          7. Store response in cache
          8. Return response with metrics
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        logger.info(json.dumps({"event": "query_received", "query": query}))

        # ── 1. Cache lookup ───────────────────────────────────────────────────
        if self.cache:
            try:
                logger.info(json.dumps({"event": "cache_lookup_started", "query": query}))
                key = self.cache.generate_key(query)
                logger.info(json.dumps({"event": "cache_key_generated", "key": key}))
                cached = self.cache.get(key)

                if cached:
                    logger.info(json.dumps({"event": "cache_hit", "query": query}))
                    cached["cache_hit"] = True
                    return cached

                logger.info(json.dumps({"event": "cache_miss", "query": query}))

            except Exception as e:
                logger.warning(json.dumps({"event": "redis_lookup_error", "error": str(e)}))
                key = None
        else:
            key = None

        # ── 2. Full pipeline ──────────────────────────────────────────────────
        try:
            total_start = time.perf_counter()

            # Embedding
            embedding_start = time.perf_counter()
            query_embedding = await self.embed_async(query)
            embedding_time = time.perf_counter() - embedding_start
            logger.info(json.dumps({"event": "embedding_complete", "time": embedding_time}))

            # Retrieval
            retrieval_start = time.perf_counter()
            results = await self.retrieve_async(query_embedding)
            retrieval_time = time.perf_counter() - retrieval_start
            logger.info(json.dumps({"event": "retrieval_complete", "time": retrieval_time}))

            # Deduplication
            unique_chunks = list(dict.fromkeys(results))

            # Reranking logic removed to reduce latency
            reranked_chunks = unique_chunks[:3] if unique_chunks else []
            reranking_time = 0

            # Generation
            g_start = time.perf_counter()
            answer = "".join(self.generate_answer(query=query, chunks=reranked_chunks))
            generation_time = time.perf_counter() - g_start

            total_time = time.perf_counter() - total_start

            # ── 3. Build response ─────────────────────────────────────────────
            response = {
                "answer": answer,
                "retrieved_chunks": reranked_chunks,
                "metrics": {
                    "embedding_time": embedding_time,
                    "retrieval_time": retrieval_time,
                    "reranking_time": reranking_time,
                    "generation_time": generation_time,
                    "total_time": total_time
                },
                "cache_hit": False
            }

            # ── 4. Store in cache BEFORE returning ────────────────────────────
            if self.cache and key:
                try:
                    logger.info(json.dumps({"event": "cache_store_started", "key": key}))
                    self.cache.set(key, response)
                    logger.info(json.dumps({"event": "cache_store_complete", "key": key}))
                except Exception as e:
                    logger.warning(json.dumps({"event": "redis_set_error", "error": str(e)}))

            return response

        except Exception as e:
            logger.error(json.dumps({"event": "query_failed", "error": str(e)}))
            raise e

    async def stream_query(self, query: str):
        if not query or not query.strip():
            yield json.dumps({"type": "error", "message": "Query must not be empty."}) + "\n"
            return
            
        start_time = time.perf_counter()

        yield json.dumps({
            "type": "event",
            "event": "query_started"
        }) + "\n"

        # Cache lookup
        key = None
        if self.cache:
            key = self.cache.generate_key(query)
            cache_result = self.cache.get(key)
            if cache_result:
                yield json.dumps({
                    "type": "cache",
                    "cache_hit": True
                }) + "\n"
                
                # simulate metric output for cache hits
                yield json.dumps({"type": "retrieved_chunks", "chunks": cache_result.get("retrieved_chunks", [])}) + "\n"
                yield json.dumps({"type": "metric", "metric": "embedding_time", "value": "Skipped (Cache Hit)"}) + "\n"
                yield json.dumps({"type": "metric", "metric": "retrieval_time", "value": "Skipped (Cache Hit)"}) + "\n"
                yield json.dumps({"type": "metric", "metric": "generation_time", "value": "Skipped (Cache Hit)"}) + "\n"
                
                total_time = time.perf_counter() - start_time
                yield json.dumps({"type": "metric", "metric": "total_time", "value": total_time}) + "\n"

                yield json.dumps({
                    "type": "final",
                    "answer": cache_result.get("answer", "")
                }) + "\n"
                return

        yield json.dumps({
            "type": "cache",
            "cache_hit": False
        }) + "\n"

        # Embedding
        embed_start = time.perf_counter()
        query_embedding = await self.embed_async(query)
        embedding_time = time.perf_counter() - embed_start

        yield json.dumps({
            "type": "metric",
            "metric": "embedding_time",
            "value": embedding_time
        }) + "\n"

        # Retrieval
        retrieval_start = time.perf_counter()
        results = await self.retrieve_async(query_embedding)
        unique_chunks = list(dict.fromkeys(results))
        reranked_chunks = unique_chunks[:3] if unique_chunks else []
        retrieval_time = time.perf_counter() - retrieval_start

        yield json.dumps({
            "type": "retrieved_chunks",
            "chunks": reranked_chunks
        }) + "\n"

        yield json.dumps({
            "type": "metric",
            "metric": "retrieval_time",
            "value": retrieval_time
        }) + "\n"

        # Generation streaming
        generation_start = time.perf_counter()

        context = "\n\n".join(reranked_chunks)
        prompt = f"""
You are an enterprise assistant.

Answer in a detailed and structured format.

Context:
{context}

Question:
{query}

Instructions:
- Provide detailed explanation
- Use bullet points
- Minimum 5 lines response
"""

        logger.info(json.dumps({
            "event": "streaming_started",
            "query": query
        }))
        answer = ""

        try:
            response = self.llm_model.generate_content(
                prompt,
                stream=True,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 512,
                },
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            for chunk in response:
                if chunk.candidates:
                    parts = chunk.candidates[0].content.parts
                    
                    for part in parts:
                        if hasattr(part, "text"):
                            token = part.text
                            answer += token
                            
                            logger.info(json.dumps({
                                "event": "token_streamed",
                                "token_length": len(token)
                            }))
        
                            yield json.dumps({
                                "type": "token",
                                "token": token
                            }) + "\n"
                    
                # Yield control to event loop since this is a blocking generator
                await asyncio.sleep(0)

            logger.info(json.dumps({
                "event": "streaming_complete",
                "total_length": len(answer)
            }))
        except Exception as e:
            logger.error(json.dumps({"event": "api_error", "error": str(e)}))
            yield json.dumps({"type": "error", "message": "Pipeline generation failed."}) + "\n"
            return

        generation_time = time.perf_counter() - generation_start

        yield json.dumps({
            "type": "metric",
            "metric": "generation_time",
            "value": generation_time
        }) + "\n"

        total_time = time.perf_counter() - start_time

        yield json.dumps({
            "type": "metric",
            "metric": "total_time",
            "value": total_time
        }) + "\n"

        yield json.dumps({
            "type": "final",
            "answer": answer
        }) + "\n"
        
        # Save cache
        if self.cache and key:
            try:
                response_dict = {
                    "answer": answer,
                    "retrieved_chunks": reranked_chunks,
                    "metrics": {
                        "embedding_time": embedding_time,
                        "retrieval_time": retrieval_time,
                        "reranking_time": 0,
                        "generation_time": generation_time,
                        "total_time": total_time
                    },
                    "cache_hit": False
                }
                self.cache.set(key, response_dict)
            except Exception as e:
                logger.warning(json.dumps({"event": "redis_set_error", "error": str(e)}))


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    rag = RAGPipeline()

    print("\n── First query (expect: cache_miss → cache_store) ──")
    r1 = asyncio.run(rag.query("What is leave policy?"))
    print(json.dumps(r1, indent=2))

    print("\n── Second query (expect: cache_hit) ──")
    r2 = asyncio.run(rag.query("What is leave policy?"))
    print(json.dumps(r2, indent=2))
