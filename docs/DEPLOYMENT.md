# Deployment Guide — Zero Cost Stack

## 1. MongoDB Atlas (Free M0 Cluster)
1. https://cloud.mongodb.com → Create free M0 cluster
2. Create DB user, allow all IPs
3. Copy connection string to .env
4. Create Vector Search Index named `legal_vector_index`:
   - path: embedding, numDimensions: 384, similarity: cosine

## 2. Groq API (Free LLM)
1. https://console.groq.com → Sign up → Create API key
2. Add GROQ_API_KEY to .env
3. Free tier: ~14,400 requests/day

## 3. Backend on Render.com (Free)
1. Push code to GitHub
2. https://render.com → New Web Service → Connect repo
3. Root dir: backend | Build: pip install -r requirements.txt
4. Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
5. Add all env vars → Deploy

## 4. Frontend on Vercel (Free)
1. https://vercel.com → Import frontend folder
2. Add VITE_API_URL = your Render backend URL
3. Deploy — live instantly

## 5. Ingest Legal Documents
```
mkdir -p backend/data/benin backend/data/madagascar
# Drop PDFs/TXTs in those folders, then:
python scripts/ingest.py --country benin --path ./data/benin/
python scripts/ingest.py --country madagascar --path ./data/madagascar/
```

## Cost at 1k-10k users: $0/month
