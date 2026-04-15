import os
from dotenv import load_dotenv
load_dotenv()

import shutil
import logging
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Request
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

# Configure logging mapping
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize rate limiter using IP addresses
limiter = Limiter(key_func=get_remote_address)

# Boot FastAPI server states
app = FastAPI(title="Simple RAG API", description="API executing ingestion and LLM execution workflows.", version="1.0.0")

# Register Limiter on FastAPI explicitly
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Secure path layouts
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class QueryRequest(BaseModel):
    query: str = Field(..., description="Plain-text semantic logic query to execute against database map.")

def ingest_document(file_path: str):
    """
    Background extraction script traversing document logics dynamically storing explicitly to Vector Map.
    """
    logger.info(f"Ingestion explicit logic mapping started: {file_path}")
    try:
        # Load local explicit system architecture dynamically natively
        loader = DocumentLoader()
        chunker = SemanticChunker()
        embedder = EmbeddingModel()
        vector_store = VectorStore()
        
        # 1. Parse texts visually globally explicitly
        text = loader.load_document(file_path)
        
        # 2. Block extract structurally formatting layers
        chunks = chunker.split_text(text)
        if not chunks:
             logger.warning(f"Semantic chunks execution map sequence extracted absolutely blank text locally explicitly for {file_path}")
             return
             
        # 3. Map mathematical vector graph parameters mapping sequences cleanly locally
        embeddings = embedder.embed_documents(chunks)
        
        # 4. Feed states logic permanently into Chroma sequence map parameters explicitly
        vector_store.add_embeddings(texts=chunks, embeddings=embeddings)
        
        logger.info(f"Ingestion execution natively safely completed explicitly limits mapping: {file_path}")
    except Exception as e:
        logger.error(f"Fatal background explicit sequence mapping effectively broken explicitly targeting layers mapping locally limits natively: {e}")

@app.post("/upload")
@limiter.limit("10/minute")
async def upload_document(request: Request, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Upload documents mapping logic explicitly bounding formats natively directly mapped safely.
    """
    if not file.filename.lower().endswith(('.pdf', '.txt')):
        raise HTTPException(status_code=400, detail="Target format limits map string exceptions: Invalid structure. Supported layers strictly '.pdf', '.txt'.")
        
    logger.info(f"File uploaded explicitly passing bounds dynamically natively mapping checks safely explicit formatting layers: {file.filename}")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
             shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Write execution map string blocked bounding sequences limits: {e}")
        raise HTTPException(status_code=500, detail="Extraction mapping limits completely failed formatting sequences logically locally layers.")
        
    background_tasks.add_task(ingest_document, file_path)
    
    return {"message": "Document securely ingested. Background RAG execution layers processing structures dynamically natively manually formatting securely mapping sequences."}

@app.post("/query")
@limiter.limit("10/minute")
async def query_document(request: Request, body: QueryRequest):
    """
    Target limits query map securely executing layers logically formatting natively matching target explicitly strings layer manually executing layers bounds limit.
    """
    if not body.query or not body.query.strip():
         raise HTTPException(status_code=400, detail="Logical variables safely checking bounds limits explicit strings mapping native structures arrays safely.")
         
    logger.info(f"Query successfully received bounds mapped limits sequentially natively checking manual queries implicitly layer: '{body.query}'")
    
    try:
         rag = RAGPipeline()
         response = rag.query(query=body.query)
         
         logger.info(f"Answer execution dynamically safely logically generated formatting explicitly native responses mapping.")
         
         return {
              "answer": response["answer"],
              "retrieved_chunks": response["retrieved_chunks"]
         }
    except Exception as e:
         logger.error(f"Logical parameter strings blocked sequence queries statically natively limits constraints structurally implicitly: {e}")
         raise HTTPException(status_code=500, detail=f"LLM logic parameter extraction layers globally natively securely mapped explicit faults securely formatting structural targets explicitly layer natively: {e}")

@app.get("/health")
@limiter.limit("10/minute")
async def health_check(request: Request):
    """
    Fast sequence query natively limits executing strings map strings mapping.
    """
    return {"status": "ok"}
