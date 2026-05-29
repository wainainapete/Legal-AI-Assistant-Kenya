# ⚖️ Legal AI Kenya

> An AI-powered legal assistant providing equitable access to justice for citizens of **Kenya**



## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Architecture](#-architecture)
3. [Tech Stack & Costs](#-tech-stack--costs)
4. [External Services Setup](#-external-services-setup)
   - [Groq (LLM API)](#1-groq-llm-api)
   - [Supabase (Vector Database)](#2-supabase-vector-database)
   - [Railway (Backend Hosting)](#3-railway-backend-hosting)
   - [Vercel (Frontend Hosting)](#4-vercel-frontend-hosting)
5. [Local Development Setup](#-local-development-setup)
6. [Environment Variables](#-environment-variables)
7. [Running the Server](#-running-the-server)
8. [Ingesting Legal Documents](#-ingesting-legal-documents)
9. [API Reference](#-api-reference)
10. [Deployment](#-deployment)
11. [Project Structure](#-project-structure)



## 🌍 Project Overview

Legal AI Kenya is a RAG (Retrieval-Augmented Generation) chatbot that helps citizens understand their legal rights in their own language (English). It searches a vectorized corpus of national legal documents and generates clear, accessible answers using a large language model.

**Pilot countries:** Kenya**

**Impact goal:** Reach 2 million users in 12 months, serving people who currently have no access to legal assistance.



## 🏗️ Architecture

```
User (Web / Mobile / WhatsApp)
        │
        ▼
  React Frontend (Vercel)
        │
        ▼ HTTPS API calls
  FastAPI Backend (Railway)
        │
        ├── LangChain RAG Pipeline
        │       ├── HuggingFace Embeddings (local, multilingual)
        │       ├── Supabase pgvector (vector search)
        │       └── Groq LLM (llama-3.3-70b-versatile)
        │
        └── Supabase PostgreSQL
                ├── langchain_pg_embedding (vector store)
                ├── langchain_pg_collection (collections)
                └── review_queue (flagged responses)
```

**RAG Flow:**
1. User sends a legal question
2. Question is embedded using `paraphrase-multilingual-MiniLM-L12-v2`
3. Top 5 most relevant legal document chunks are retrieved from Supabase pgvector
4. Groq LLM generates an answer grounded in those documents
5. Safety filters check the question and answer
6. Response returned with sources and confidence score



## 💰 Tech Stack & Costs

| Service | Purpose | Cost |
|---------|---------|------|
| **Groq** | LLM inference (Llama 3.3 70B) | Free tier |
| **Supabase** | PostgreSQL + pgvector database | Free (500MB) |
| **Railway** | Backend hosting | ~$5/month (Hobby) |
| **Vercel** | Frontend hosting | Free |
| **HuggingFace** | Embeddings model (local) | Free |
| **GitHub** | Code repository | Free |
| **Total** | | ~$5/month |



## 🔧 External Services Setup

### 1. Groq (LLM API)

**Website:** https://console.groq.com

**Steps:**
1. Go to https://console.groq.com and sign up
2. Click **"API Keys"** in the left sidebar
3. Click **"Create API Key"**
4. Give it a name: `legal-ai-africa`
5. Copy the key (starts with `gsk_...`) — you only see it once!
6. Save it as `GROQ_API_KEY` in your `.env` file

**Model used:** `llama-3.3-70b-versatile`  
**Free tier limits:** 6,000 tokens/minute, 500,000 tokens/day — sufficient for pilot



### 2. Supabase (Vector Database)

**Website:** https://supabase.com

**Steps:**

#### A. Create Project
1. Go to https://supabase.com → Sign up with GitHub
2. Click **"New Project"**
3. Fill in:
   - **Name:** `legal-ai-africa`
   - **Database Password:** create a strong password and save it!
   - **Region:** West EU (Ireland) — closest to Madagascar/Benin
4. Click **"Create new project"** — wait ~2 minutes

#### B. Enable pgvector & Create Tables
1. In your project, click **"SQL Editor"** in the left sidebar
2. Paste and run this SQL:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create legal documents table
CREATE TABLE legal_docs (
  id bigserial PRIMARY KEY,
  content text,
  embedding vector(384),
  source text,
  country text,
  page integer,
  metadata jsonb
);

-- Create vector search index
CREATE INDEX ON legal_docs 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

#### C. Get API Keys
1. Click **"Connect"** button at the top of the dashboard
2. Go to **"API Keys"** tab
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Anon Key** → `SUPABASE_ANON_KEY`
4. Click **"Legacy anon, service_role API keys"** tab
   - Copy **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`

#### D. Get Database Connection String
1. Click **"Connect"** → **"Connection String"** tab
2. Set **Method** to **"Transaction pooler"** (port 6543, IPv4 compatible)
3. Copy the URI and replace `[YOUR-PASSWORD]` with your database password
4. Save as `DATABASE_URL` in your `.env`

**Free tier limits:** 500MB database, unlimited API requests

---

### 3. Railway (Backend Hosting)

**Website:** https://railway.app

**Steps:**

#### A. Create Account & Project
1. Go to https://railway.app → Sign up with GitHub
2. Select **Hobby plan** ($5/month) — needed for enough RAM to load the embeddings model
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select your `Legal-AI-Africa` repository
5. Click **"Add service"**

#### B. Configure Service
1. Click on your service → **"Settings"** tab
2. Set **Root Directory** to `/backend`
3. Set **Region** to `EU West (Amsterdam)`
4. Railway will auto-detect the `Procfile` and use:
   ```
   web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

#### C. Set Environment Variables
1. Click **"Variables"** tab
2. Add all variables from the [Environment Variables](#-environment-variables) section below
3. Make sure to remove any old MongoDB variables

#### D. Get Your Backend URL
After successful deployment, Railway provides a URL like:
```
https://legal-ai-africa-production.up.railway.app
```
Use this as `VITE_API_URL` in your Vercel frontend deployment.

#### E. Monitor Deployments
- Go to **"Deployments"** tab to see build logs
- Click on a deployment to see runtime logs
- If status is **"CRASHED"**, check logs for the error



### 4. Vercel (Frontend Hosting)

**Website:** https://vercel.com

**Steps:**

#### A. Create Account & Deploy
1. Go to https://vercel.com → Sign up with GitHub
2. Click **"Add New Project"**
3. Select your `Legal-AI-Africa` repository
4. Set **Root Directory** to `frontend`
5. Click **"Deploy"**

#### B. Set Environment Variables
1. After deployment, go to **Project Settings** → **Environment Variables**
2. Add:
   - **Key:** `VITE_API_URL`
   - **Value:** `https://legal-ai-africa-production.up.railway.app`
3. Click **"Save"**
4. Redeploy for the variable to take effect

#### C. Your Frontend URL
```
https://legal-ai-africa.vercel.app
```

**Free tier:** Unlimited deployments, 100GB bandwidth/month



## 💻 Local Development Setup

### Prerequisites
- Python 3.11+ (3.13 works with our fixed dependencies)
- Node.js 18+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Fitahiana4/Legal-AI-Africa.git
cd Legal-AI-Africa
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
# Copy example env file
copy .env.example .env   # Windows
cp .env.example .env     # Mac/Linux

# Edit .env with your real credentials
```

See [Environment Variables](#-environment-variables) section for all required values.

### 4. Frontend Setup

```bash
cd frontend
npm install
```



## 🔑 Environment Variables

Create `backend/.env` with these values:

```env
# === LLM (Groq) ===
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# === Database (Supabase) ===
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...your_anon_key
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...your_service_role_key

# Transaction pooler URL (port 6543) — use this, NOT the direct connection
DATABASE_URL=postgresql://postgres.your-project-id:YOUR-PASSWORD@aws-1-eu-west-1.pooler.supabase.com:6543/postgres

# === App Config ===
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173
SECRET_KEY=your-secret-key-change-in-production
CONFIDENCE_THRESHOLD=0.75
MAX_TOKENS_RESPONSE=1024

# === WhatsApp (optional) ===
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_VERIFY_TOKEN=
```

> ⚠️ **Important:** Always use the **Transaction pooler** connection string (port `6543`), not the Session pooler (port `5432`) or Direct connection. The Transaction pooler supports more concurrent connections and is IPv4 compatible.

---

## 🚀 Running the Server

### Backend

```bash
cd backend

# Activate venv first
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# Development mode (auto-reload on file changes)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend runs at: http://127.0.0.1:8000  
Swagger API docs: http://127.0.0.1:8000/docs  
Health check: http://127.0.0.1:8000/api/health

### Frontend

```bash
cd frontend

# Development mode
npm run dev

# Build for production
npm run build
```

Frontend runs at: http://localhost:5173 (or 5174 if 5173 is busy)



## 📥 Ingesting Legal Documents

Legal documents must be ingested into Supabase before the chatbot can answer questions.

### Supported Formats
- `.pdf` — PDFs (most legal texts)
- `.docx` — Word documents
- `.txt` / `.md` — Plain text

> ⚠️ `.doc` files (old Word format) are **not supported**. Convert them to `.docx` first using Microsoft Word or LibreOffice.

### Organize Your Documents

```
data/
├── madagascar/
│   ├── Constitution-2010.pdf
│   ├── Code-du-Travail-2024.pdf
│   └── ...
└── benin/
    ├── Constitution-1990.pdf
    ├── Code-du-Travail.pdf
    └── ...
```

### Run Ingestion

```bash
cd backend

# Activate venv
venv\Scripts\activate

# Ingest Madagascar documents
python scripts/ingest.py --country madagascar --path ..\..\data\madagascar\

# Ingest Benin documents
python scripts/ingest.py --country benin --path ..\..\data\benin\
```

**What happens during ingestion:**
1. Each document is loaded and split into ~800-character chunks with 100-character overlap
2. Each chunk is embedded using the multilingual MiniLM model (384 dimensions)
3. Chunks are uploaded to Supabase in batches of 25 with a 2-second pause between batches
4. Embeddings are stored in `langchain_pg_embedding` table with country metadata

**Current corpus:**
- Madagascar: 60 documents, 8,454 chunks
- Benin: pending ingestion

### Verify in Supabase
Go to Supabase → **Table Editor** → `langchain_pg_embedding` to confirm your data is there.



## 📡 API Reference

Base URL: `https://legal-ai-africa-production.up.railway.app`  
Local URL: `http://127.0.0.1:8000`

### POST `/api/chat/`
Ask a legal question.

**Request:**
```json
{
  "question": "Comment faire pour démissionner?",
  "country": "madagascar",
  "language": "fr",
  "session_id": "user-session-123"
}
```

**Response:**
```json
{
  "answer": "Pour démissionner, vous devez...",
  "sources": ["Loi-n°-2024-014-Code-de-travail.doc.pdf"],
  "confidence": 1.0,
  "needs_review": false,
  "session_id": "user-session-123"
}
```

**Country options:** `madagascar`, `benin`  
**Language options:** `fr` (French), `mg` (Malagasy)



### GET `/api/health`
Check if the backend is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```



### POST `/api/review/flag`
Flag a response for human review.

**Request:**
```json
{
  "session_id": "user-session-123",
  "question": "...",
  "answer": "...",
  "country": "madagascar",
  "reason": "inappropriate",
  "flagged_by": "user"
}
```



### GET `/api/documents/stats`
Get corpus statistics.

**Response:**
```json
{
  "madagascar": 8454,
  "benin": 0,
  "total": 8454
}
```



## 🚢 Deployment

### Deploy Backend to Railway

```bash
# 1. Make sure all changes are saved locally
# 2. Commit and push to GitHub
git add -A
git commit -m "Your commit message"
git push origin main

# Railway automatically redeploys on every push to main
```

**Railway checklist:**
- ✅ Root Directory set to `/backend`
- ✅ `Procfile` exists in `/backend` with: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ All environment variables set in Railway Variables tab
- ✅ Region: EU West (Amsterdam)

### Deploy Frontend to Vercel

Vercel automatically redeploys on every push to `main`.

**Vercel checklist:**
- ✅ Root Directory set to `frontend`
- ✅ `VITE_API_URL` environment variable set to Railway backend URL



## 📁 Project Structure

```
Legal-AI-Africa/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py          # Chat endpoint
│   │   │   ├── documents.py     # Document stats endpoint
│   │   │   ├── health.py        # Health check endpoint
│   │   │   └── review.py        # Review/flag endpoint
│   │   ├── core/
│   │   │   ├── config.py        # Settings & env vars
│   │   │   ├── database.py      # Supabase connection
│   │   │   └── rag_pipeline.py  # RAG logic (embeddings + LLM)
│   │   ├── utils/
│   │   │   └── safety.py        # Content safety filters
│   │   └── main.py              # FastAPI app entry point
│   ├── scripts/
│   │   └── ingest.py            # Document ingestion script
│   ├── Procfile                 # Railway start command
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Local environment variables (not committed)
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   └── App.jsx              # Main app
│   ├── .env                     # Frontend env vars (VITE_API_URL)
│   └── package.json
│
├── data/
│   ├── madagascar/              # Madagascar legal PDFs
│   └── benin/                   # Benin legal PDFs
│
└── README.md
```



## 🛠️ Troubleshooting

### Backend won't start
- Make sure venv is activated: `venv\Scripts\activate`
- Check `.env` file exists and has all required variables
- Run `pip install -r requirements.txt` again

### `MaxClientsInSessionMode` error during ingestion
- Switch to Transaction pooler (port `6543`) in your `DATABASE_URL`
- Do NOT use Session pooler (port `5432`) or Direct connection

### Railway deployment crashes
- Check Variables tab has all env variables
- Check Deployments → click deployment → view logs
- Most common cause: missing or wrong `MONGODB_URI` / `DATABASE_URL`

### Empty or wrong answers from chatbot
- Make sure documents are ingested: check Supabase Table Editor
- Verify `DATABASE_URL` uses Transaction pooler URL
- Check `GROQ_API_KEY` is valid

### Frontend can't reach backend
- Check `VITE_API_URL` in Vercel environment variables
- Make sure it points to Railway URL (no trailing slash)
- Check Railway service is "Online" (green dot)



## 📄 License

MIT License — see [LICENSE](LICENSE) for details.



## 🤝 Contributing

This project is part of ACFAI's mission to democratize access to justice in Africa. Contributions welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request


