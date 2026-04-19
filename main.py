import os
from dotenv import load_dotenv
load_dotenv()

import time
import shutil
import logging
from typing import Dict, Any

import asyncio
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import internal modular system layers
from document import DocumentLoader
from chunk import SemanticChunker
from embedding import EmbeddingModel
from vector_store import VectorStore
from rag_pipeline import RAGPipeline

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Boot FastAPI app
app = FastAPI(
    title="Simple RAG API",
    description="API executing ingestion and LLM execution workflows.",
    version="1.0.0"
)

# Register Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Upload directory
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize RAGPipeline once at startup (fixes metrics always 0 and cache always miss)
rag = RAGPipeline()

class QueryRequest(BaseModel):
    query: str = Field(..., description="Plain-text query to execute against the vector store.")


def ingest_document(file_path: str):
    """
    Background task: loads, chunks, embeds and stores document into vector store.
    """
    logger.info(f'{{"event": "ingestion_started", "file": "{file_path}"}}')
    try:
        loader = DocumentLoader()
        chunker = SemanticChunker()
        embedder = EmbeddingModel()
        vector_store = VectorStore()

        text = loader.load_document(file_path)

        chunks = chunker.split_text(text)
        if not chunks:
            logger.warning(f'{{"event": "ingestion_empty", "file": "{file_path}"}}')
            return

        embeddings = embedder.embed_documents(chunks)
        vector_store.add_embeddings(texts=chunks, embeddings=embeddings)

        logger.info(f'{{"event": "ingestion_complete", "file": "{file_path}"}}')
    except Exception as e:
        logger.error(f'{{"event": "ingestion_failed", "file": "{file_path}", "error": "{e}"}}')


@app.post("/upload")
@limiter.limit("10/minute")
async def upload_document(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload a PDF or TXT document. Ingestion runs as a background task.
    """
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only '.pdf' and '.txt' are supported.")

    logger.info(f'{{"event": "upload_received", "file": "{file.filename}"}}')

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f'{{"event": "upload_failed", "file": "{file.filename}", "error": "{e}"}}')
        raise HTTPException(status_code=500, detail="File write failed.")

    background_tasks.add_task(ingest_document, file_path)

    return {"message": f"Document '{file.filename}' uploaded. Background ingestion started."}


@app.post("/query")
@limiter.limit("10/minute")
async def query_document(request: Request, body: QueryRequest):
    """
    Submit a query and receive an answer with retrieved chunks, metrics, and cache status.
    """
    if not body.query or not body.query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty.")

    logger.info(f'{{"event": "query_received", "query": "{body.query}"}}')

    # We shift execution logging inside the generator to keep true timings.
    # Return a StreamingResponse utilizing jsonlines directly.
    generator = rag.stream_query(body.query)
    
    return StreamingResponse(
        generator,
        media_type="application/x-ndjson"
    )


@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """
    Health check endpoint.
    """
    return {"status": "ok"}
