from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.core.rag_pipeline import LegalRAGPipeline
import uuid

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        pipeline = LegalRAGPipeline(country=request.country.value)
        result = await pipeline.query(request.question)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            needs_review=result["needs_review"],
            session_id=request.session_id or str(uuid.uuid4()),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
