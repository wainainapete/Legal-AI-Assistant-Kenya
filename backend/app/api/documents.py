from fastapi import APIRouter
from app.core.config import settings
from supabase import create_client

router = APIRouter()

@router.get("/stats")
async def get_corpus_stats():
    try:
        client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        
        madagascar_count = client.table("langchain_pg_embedding").select("id", count="exact").eq("cmetadata->>country", "madagascar").execute()
        benin_count = client.table("langchain_pg_embedding").select("id", count="exact").eq("cmetadata->>country", "benin").execute()

        return {
            "madagascar": madagascar_count.count or 0,
            "benin": benin_count.count or 0,
            "total": (madagascar_count.count or 0) + (benin_count.count or 0)
        }
    except Exception as e:
        return {"madagascar": 0, "benin": 0, "total": 0, "error": str(e)}