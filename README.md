# Role-Based-Access-Control-RBAC-RAG-System

## Overview
Advanced Role-Based Access Control (RBAC) RAG System - A document-based question answering system with role-based access control that restricts information access based on department roles.

## Architecture

### Components
- **Backend**: FastAPI application (`backend/main.py`)
- **Generation Pipeline**: LLM-based response generation (`src/GenerationPipeline.py`)
- **Retriever Pipeline**: Hybrid FAISS + BM25 retrieval (`src/RetrieverPipeline.py`)
- **Ingestion Pipeline**: Document processing and vector storage (`src/IngestionPipeline.py`)

### Key Technologies
- **LLM**: Groq (ChatGroq) with configurable model
- **Embeddings**: HuggingFace (sentence-transformers/all-MiniLM-L6-v2)
- **Vector Store**: FAISS
- **Retrieval**: Ensemble of FAISS vector retriever (60%) + BM25 retriever (40%)
- **API Framework**: FastAPI

## Configuration (`utils/config.py`)
| Setting | Value |
|---------|-------|
| LLM_MODEL | openai/gpt-oss-20b |
| EMBEDDING_MODEL | sentence-transformers/all-MiniLM-L6-v2 |
| CHUNK_SIZE | 1100 |
| CHUNK_OVERLAP | 450 |
| TOP_K | 6 |
| DATADIR | data |
| FAISS_INDEX | Faiss-Vectors |

## Data Structure
Documents are organized by department in `data/` directory:

| Department | Documents |
|------------|-----------|
| engineering | engineering_master_doc.md |
| finance | financial_summary.md, quarterly_financial_report.md |
| general | employee_handbook.md |
| hr | hr_data.csv |
| marketing | marketing_report_2024.md, q1-q4 2024 reports |

## API Endpoints

### GET /
Returns "RBAC RAG Application Running....."

### POST /chat
Request body:
```json
{
  "role": "department_name",
  "question": "user question"
}
```
Response: Generated answer based on role-restricted context

## Pipeline Flow
1. **Ingestion**: Load documents from `data/{department}/` → Split into chunks → Create FAISS index per department
2. **Retrieval**: For a given role, load FAISS index + raw documents → Create hybrid retriever
3. **Generation**: Format retrieved docs → Prompt LLM with role-specific context → Return response

## Dependencies (`requirements.txt`)
- langchain==0.3.0
- langchain-community
- langchain-core
- langchain-groq
- faiss-cpu
- pypdf
- langchain-huggingface
- sentence-transformers
- markdown
- fastapi
- uvicorn
- unstructured
- rank_bm25

## Role-Based Access Control Logic
- Documents are tagged with `allowed_roles` metadata during ingestion
- Retrieval pipeline enforces that only documents from the requested role's department are accessible
- LLM prompt enforces strict context-only responses with access denial for out-of-scope queries

## Environment Variables (.env)
- GROQ_API_KEY: Required for ChatGroq LLM
- LLM_MODEL: Optional, defaults to "openai/gpt-oss-20b"
- EMBEDDING_MODEL: Optional, defaults to "sentence-transformers/all-MiniLM-L6-v2"

## Setup & Execution
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
GROQ_API_KEY=your_api_key

# Run ingestion (creates FAISS indices)
python src/IngestionPipeline.py

# Start API server
uvicorn backend.main:app --reload
```

## Directory Structure
```
├── backend/
│   └── main.py           # FastAPI application
├── src/
│   ├── GenerationPipeline.py
│   ├── RetrieverPipeline.py
│   └── IngestionPipeline.py
├── utils/
│   └── config.py
├── data/
│   ├── engineering/
│   ├── finance/
│   ├── general/
│   ├── hr/
│   └── marketing/
├── Faiss-Vectors/          # Generated vector indices
├── requirements.txt
└── reme.md
```