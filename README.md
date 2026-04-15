# RAG Document Question Answering API

A production-style Retrieval-Augmented Generation (RAG) system built using FastAPI that allows users to upload documents and ask questions based on those documents.

---

# Overview

This project implements a complete end-to-end RAG pipeline:

Upload Documents → Chunk → Embed → Store → Retrieve → Rerank → Generate Answer

The system supports:

* PDF and TXT document ingestion
* Semantic chunking
* Vector similarity search
* Reranking for improved retrieval
* LLM-based answer generation
* Observability and latency tracking
* FastAPI API endpoints

---

# Architecture

System Flow:

User Upload Document
↓
Document Loader
↓
Semantic Chunking
↓
Embedding Model
↓
Vector Store (ChromaDB)
↓
User Query
↓
Query Embedding
↓
Similarity Search (Top 10)
↓
Reranking (Top 3)
↓
LLM (Gemini 2.5 Flash)
↓
Final Answer + Metrics

---

# Models Used

## Embedding Model

Model: sentence-transformers/all-MiniLM-L6-v2

Purpose:

* Convert document chunks into embeddings
* Convert query into embeddings

Why Chosen:

* Lightweight
* Fast
* Good retrieval quality

---

## Reranking Model

Model: cross-encoder/ms-marco-MiniLM-L-6-v2

Purpose:

* Improve retrieval quality
* Rank most relevant chunks

Why Chosen:

* Lightweight
* High accuracy
* Fast inference

---

## LLM Model

Model: Gemini 2.5 Flash

Purpose:

* Generate answers from retrieved context

Why Chosen:

* Fast latency
* Low cost
* Strong reasoning

---

# Vector Database

ChromaDB

Purpose:

* Store embeddings
* Perform similarity search

Why Chosen:

* Lightweight
* Persistent storage
* Easy integration

---

# Chunking Strategy

We used semantic chunking.

Chunk Size Strategy:

* FAQs → 128–256 tokens
* Technical docs → 256–512 tokens
* Legal docs → 512–1024 tokens

Chosen for this project:

* Chunk Size: 400
* Overlap: 50

Reason:

* Balance between retrieval accuracy and context preservation

---

# Retrieval Pipeline

Query
↓
Embedding
↓
Similarity Search (Top 10)
↓
Deduplication
↓
Reranking
↓
Top 3 chunks
↓
LLM Generation

---

# Observability

We implemented structured logging and latency tracking.

Tracked Metrics:

* embedding_time
* retrieval_time
* reranking_time
* generation_time
* total_time

Example Response:

{
"answer": "...",
"retrieved_chunks": [...],
"metrics": {
"embedding_time": 0.02,
"retrieval_time": 0.01,
"reranking_time": 0.04,
"generation_time": 0.80,
"total_time": 0.87
}
}

---

# API Endpoints

## Upload Document

POST /upload

Upload PDF or TXT file

Example:

curl -X POST "http://127.0.0.1:8000/upload" 
-F "file=@document.pdf"

---

## Query

POST /query

Request:

{
"query": "What is the company leave policy?"
}

Response:

{
"answer": "...",
"retrieved_chunks": [...],
"metrics": {...}
}

---

## Health Check

GET /health

Response:

{
"status": "ok"
}

---

# Background Ingestion

We implemented background ingestion using FastAPI BackgroundTasks.

Steps:

* Load document
* Chunk document
* Generate embeddings
* Store embeddings

This prevents blocking API requests.

---

# Rate Limiting

Basic rate limiting implemented:

* 10 requests per minute
* Prevents API abuse

---

# Project Structure

project/

document.py
chunk.py
embedding.py
vector_store.py
rag_pipeline.py
main.py
requirements.txt
.env
README.md

---

# Setup Instructions

## Clone Repository

git clone <repo_url>

cd project

---

## Create Virtual Environment

python -m venv venv

Activate:

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

---

## Install Dependencies

pip install -r requirements.txt

---

## Create .env file

Create `.env`

Add:

GEMINI_API_KEY=your_api_key

---

# Run Application

uvicorn main:app --reload

Server runs at:

http://127.0.0.1:8000

Swagger UI:

http://127.0.0.1:8000/docs

---

## API Endpoints

* **POST `/upload`**
  Upload document
* **POST `/query`**
  Ask question
* **GET `/health`**
  Health check


# Example Workflow

1. Upload Document

POST /upload

2. Ask Question

POST /query

3. Get Answer

System retrieves relevant chunks and generates answer

---

# Evaluation Criteria Coverage

Chunking Strategy

* Semantic chunking implemented
* Chunk size justification provided

Retrieval Quality

* Vector search implemented
* Reranking added

API Design

* Clean FastAPI endpoints
* Background ingestion

Metrics Awareness

* Latency tracking added

System Explanation Clarity

* Clear architecture provided

---

# Retrieval Failure Case

Example:

Query:
"What is salary structure?"

Failure Reason:

Document did not contain salary information.

System retrieved irrelevant chunks.

Solution:

* Improve chunking
* Improve reranking
* Add more documents

---

# Performance

Typical Latency:

Embedding: 0.02s
Retrieval: 0.01s
Reranking: 0.03s
Generation: 1–3s

Total: ~1.2s

---

# Future Improvements

* Add hybrid search (BM25 + Vector)
* Add caching
* Add multi-document support
* Add UI

---

# Tech Stack

FastAPI
ChromaDB
Sentence Transformers
Gemini 2.5 Flash
Python

---

# Author

-K.Dinakaran

RAG Document Question Answering System Built for Technical Evaluation.
---