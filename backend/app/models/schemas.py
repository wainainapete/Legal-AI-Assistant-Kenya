from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Country(str, Enum):
    benin = "benin"
    madagascar = "madagascar"

class Language(str, Enum):
    fr = "fr"
    mg = "mg"

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=1000)
    country: Country
    language: Language = Language.fr
    session_id: Optional[str] = None  # Anonymous by default

class ChatResponse(BaseModel):
    answer: str
    sources: list[str]
    confidence: float
    needs_review: bool
    session_id: Optional[str] = None

class ReviewFlag(BaseModel):
    session_id: str
    question: str
    answer: str
    country: Country
    reason: Optional[str] = None
    flagged_by: str = "user"  # "user" | "system" | "expert"
