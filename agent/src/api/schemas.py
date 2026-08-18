from pydantic import BaseModel, Field
from generation.models import AgentResponse, Citation

class ChatRequest(BaseModel):
    question: str = Field(min_length=1)

__all__ = ["ChatRequest", "AgentResponse", "Citation"]
