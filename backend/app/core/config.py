from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    DATABASE_URL: str = ""
    ENVIRONMENT: str = "development"
    ALLOWED_ORIGINS: str = "http://localhost:5173"
    SECRET_KEY: str = "legal-ai-africa-secret-key-2024"
    CONFIDENCE_THRESHOLD: float = 0.75
    MAX_TOKENS_RESPONSE: int = 1024
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

settings = Settings()