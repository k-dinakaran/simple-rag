# Enterprise RAG Document Question Answering System

A production‑grade Retrieval Augmented Generation (RAG) system built using FastAPI, Streamlit, Redis, and ChromaDB. This system allows users to upload documents and ask questions with real‑time streaming responses, observability, caching, and latency tracking.

---

# Overview

This project implements a complete enterprise‑level RAG pipeline:

Upload Documents → Chunk → Embed → Store → Retrieve → Generate → Stream Response → Cache

Key Features:

• PDF and TXT ingestion
• Semantic chunking
• Vector similarity search
• Real‑time streaming responses
• Redis caching layer
• Observability dashboard
• Latency telemetry
• Parallel pipeline execution
• Production‑ready FastAPI backend
• Streamlit observability dashboard

---

# System Architecture

## High Level Flow

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
Cache Lookup (Redis)
↓
Query Embedding
↓
Similarity Search (Top‑K)
↓
LLM (Gemini 2.5 Flash Streaming)
↓
Streaming Response
↓
Cache Store
↓
Final Answer + Metrics

---

# Models Used

## Embedding Model

Model: sentence-transformers/all-MiniLM-L6-v2

Purpose:

• Convert document chunks into embeddings
• Convert queries into embeddings

Why Chosen:

• Lightweight
• Fast inference
• Good retrieval performance

---

## LLM Model

Model: Gemini 2.5 Flash

Purpose:

• Generate answers from retrieved context
• Streaming token responses

Why Chosen:

• Low latency
• Cost efficient
• Streaming support
• Strong reasoning

---

# Vector Database

ChromaDB

Purpose:

• Store embeddings
• Perform similarity search

Why Chosen:

• Lightweight
• Persistent storage
• Easy integration

---

# Cache Layer

Redis Cache

Purpose:

• Reduce repeated queries
• Improve latency
• Production scalability

Cache Strategy:

• Query hash key
• TTL: 1 hour
• Cache hit bypasses full pipeline

Example:

Cache Hit Flow:

Query → Cache Hit → Return Response

Cache Miss Flow:

Query → Full Pipeline → Store Cache → Return Response

---

# Chunking Strategy

Semantic Chunking

Configuration:

• Chunk Size: 400
• Overlap: 50

Reason:

• Better context preservation
• Improved retrieval accuracy

---

# Retrieval Pipeline

Query
↓
Cache Lookup
↓
Embedding
↓
Similarity Search (Top‑3)
↓
LLM Generation
↓
Streaming Response

---

# Streaming Architecture

Real‑time streaming implemented using:

• FastAPI StreamingResponse
• NDJSON streaming
• Streamlit live rendering

Streaming Flow:

User Query
↓
Streaming Start
↓
Token Streaming
↓
Streaming Complete

---

# Observability

Structured Logging Implemented

Tracked Metrics:

• embedding_time
• retrieval_time
• generation_time
• total_time
• cache_hit

Example Response:

{
"answer": "...",
"retrieved_chunks": [...],
"metrics": {
"embedding_time": 0.02,
"retrieval_time": 0.01,
"generation_time": 1.2,
"total_time": 1.23
}
}

---

# Observability Dashboard

Streamlit Dashboard Includes:

• Real‑time streaming answer
• Retrieved chunks visualization
• Metrics telemetry
• Cache hit indicator
• JSON logs viewer

---

# API Endpoints

## Upload Document

POST /upload

Upload PDF or TXT file

Example:

curl -X POST "[http://127.0.0.1:8000/upload](http://127.0.0.1:8000/upload)" 
-F "file=@document.pdf"

---

## Query

POST /query

Request:

{
"query": "What is the company leave policy?"
}

Streaming Response:

• Real‑time token streaming
• Final metrics returned

---

## Health Check

GET /health

Response:

{
"status": "ok"
}

---

# Background Ingestion

Implemented using FastAPI BackgroundTasks

Steps:

• Load document
• Chunk document
• Generate embeddings
• Store embeddings

---

# Performance Optimization

Implemented Optimizations:

• Redis caching
• Reduced retrieval chunks
• Streaming responses
• Parallel pipeline execution

---

# Project Structure

project/

main.py
rag_pipeline.py
vector_store.py
embedding.py
chunk.py
document.py
cache.py
streamlit_app.py
requirements.txt
.env
README.md

---

# Setup Instructions

## Clone Repository

```
git clone https://github.com/k-dinakaran/simple-rag.git
cd simple-rag
```

---

## Create Virtual Environment

```
python -m venv venv
```

Activate:

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

---

## Install Dependencies

```
pip install -r requirements.txt
```

---

## Create .env File

Create `.env`

Add:

```
GEMINI_API_KEY=your_api_key
```

---

# Run Application

Backend:

```
uvicorn main:app --reload
```

Streamlit Dashboard:

```
streamlit run streamlit_app.py
```

---

# Example Workflow

1. Upload Document
2. Ask Question
3. View Streaming Answer
4. Inspect Metrics

---

# Performance

Typical Latency:

Embedding: 0.2s
Retrieval: 0.1s
Generation: 2‑4s

Cache Hit Latency:

~50‑150ms

---

# Future Improvements

• Hybrid search (BM25 + Vector)
• Multi‑document retrieval
• Multi‑tenant architecture
• Distributed vector store
• Authentication

---

# Tech Stack

• FastAPI
• Streamlit
• ChromaDB
• Redis
• Sentence Transformers
• Gemini 2.5 Flash
• Python

---

# Production Features Implemented

• Redis caching
• Streaming responses
• Observability logs
• Latency tracking
• Background ingestion
• Clean API design

---

# License

MIT License

---

# Author

-K.Dinakaran

Enterprise RAG System
