import os
import time
import json
import logging
from typing import Dict, Any

import google.generativeai as genai
from sentence_transformers import CrossEncoder

# Import previous pipeline modules
from embedding import EmbeddingModel
from vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    RAG Pipeline with reranking, observability, structured logging, and deduplication.
    """

    def __init__(self):
        """
        Initializes the pipeline with embedding, reranking, vector store, and LLM.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
             
        genai.configure(api_key=api_key)
        
        self.embedding_model = EmbeddingModel()
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.vector_store = VectorStore()
        self.llm_model = genai.GenerativeModel('gemini-2.5-flash')

    def retrieve(self, query: str, top_k: int = 3) -> list[str]:
        """
        Retrieves top_k chunks after deduplication and reranking.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_query(query)
            
            # Retrieve top 10 chunks
            results = self.vector_store.similarity_search(query_embedding=query_embedding, top_k=10)
            
            # Remove duplicates
            unique_chunks = list(dict.fromkeys(results))
            
            if not unique_chunks:
                return []
                
            # Rerank chunks
            pairs = [[query, chunk] for chunk in unique_chunks]
            scores = self.reranker.predict(pairs)
            
            # Sort by score
            chunk_scores = list(zip(unique_chunks, scores))
            chunk_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top_k
            top_chunks = [chunk for chunk, score in chunk_scores[:top_k]]
            
            return top_chunks
        except Exception as e:
            logger.error(json.dumps({"event": "retrieval_error", "error": str(e)}))
            raise e

    def generate_answer(self, query: str, chunks: list[str]) -> str:
        """
        Generates an answer from the LLM based on the query and context chunks.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")

        if not chunks:
            return "I don't have enough context to answer this."

        context = "\n\n".join(chunks)

        prompt = f"""You are a helpful assistant.
Answer using only the context.

Context:
{context}

Question:
{query}

Answer:"""

        try:
            response = self.llm_model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(json.dumps({"event": "api_error", "error": str(e)}))
            raise e

    def query(self, query: str) -> dict:
        """
        Executes query pipeline with full latency tracking and structured logging.
        """
        if not query or not query.strip():
            raise ValueError("Query must not be empty.")
            
        logger.info(json.dumps({"event": "query_received", "query": query}))

        try:
            total_start = time.time()
            
            # Ensure proper separation for latency tracking while adhering to logic
            # embedding_time
            embed_start = time.time()
            query_embedding = self.embedding_model.embed_query(query)
            embedding_time = time.time() - embed_start
            logger.info(json.dumps({"event": "embedding_completed"}))
            
            # retrieval_time
            retrieval_start = time.time()
            results = self.vector_store.similarity_search(query_embedding=query_embedding, top_k=10)
            retrieval_time = time.time() - retrieval_start
            logger.info(json.dumps({"event": "retrieval_completed"}))
            
            unique_chunks = list(dict.fromkeys(results))
            
            # reranking_time
            rerank_start = time.time()
            if unique_chunks:
                pairs = [[query, chunk] for chunk in unique_chunks]
                scores = self.reranker.predict(pairs)
                chunk_scores = list(zip(unique_chunks, scores))
                chunk_scores.sort(key=lambda x: x[1], reverse=True)
                top_chunks = [chunk for chunk, score in chunk_scores[:3]]
            else:
                top_chunks = []
            reranking_time = time.time() - rerank_start
            logger.info(json.dumps({"event": "reranking_completed"}))
            
            # generation_time
            gen_start = time.time()
            answer = self.generate_answer(query=query, chunks=top_chunks)
            generation_time = time.time() - gen_start
            logger.info(json.dumps({"event": "generation_completed"}))
            
            total_time = time.time() - total_start
            
            return {
                "answer": answer,
                "retrieved_chunks": top_chunks,
                "metrics": {
                    "embedding_time": embedding_time,
                    "retrieval_time": retrieval_time,
                    "reranking_time": reranking_time,
                    "generation_time": generation_time,
                    "total_time": total_time
                }
            }
            
        except Exception as e:
            logger.error(json.dumps({"event": "query_failed", "error": str(e)}))
            raise e

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    rag = RAGPipeline()
    response = rag.query("What is leave policy?")
    print(json.dumps(response, indent=2))
