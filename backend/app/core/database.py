from supabase import create_client, Client
from app.core.config import settings

supabase_client: Client = None

async def connect_db():
    global supabase_client
    supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    print("✅ Connected to Supabase")

async def close_db():
    print("🔌 Supabase connection closed")

def get_supabase() -> Client:
    return supabase_client