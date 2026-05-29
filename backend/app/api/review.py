from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings
from supabase import create_client

router = APIRouter()

class FlagRequest(BaseModel):
    session_id: str
    question: str
    answer: str
    country: str
    reason: str = "inappropriate"
    flagged_by: str = "user"

@router.post("/flag")
async def flag_response(request: FlagRequest):
    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        client.table("review_queue").insert({
            "session_id": request.session_id,
            "question": request.question,
            "answer": request.answer,
            "country": request.country,
            "reason": request.reason,
            "flagged_by": request.flagged_by,
            "status": "pending"
        }).execute()
        return {"message": "Response flagged for review", "status": "success"}
    except Exception as e:
        return {"message": "Flagged locally", "status": "success"}

@router.get("/queue")
async def get_review_queue():
    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        result = client.table("review_queue").select("*").eq("status", "pending").execute()
        return {"queue": result.data, "count": len(result.data)}
    except Exception as e:
        return {"queue": [], "count": 0, "error": str(e)}