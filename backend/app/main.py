from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import connect_db, close_db
from app.api import chat, documents, health, review
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(
    title="AI Legal Assistant — Africa",
    description="Equitable access to legal information for Benin & Madagascar",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(review.router, prefix="/api/review", tags=["review"])


@app.get("/")
async def root():
    return {"message": "Legal AI Africa API — v1.0", "docs": "/docs"}
