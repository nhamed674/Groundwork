from pydantic import (BaseModel, Field )
from typing import Any


class Chunk(BaseModel):
    text: str
    source_path: str
    source : str
    score: float | None = None
    metadata: dict[str,Any] = Field(default_factory = dict)

class Citation(BaseModel):
    source_path: str
    source: str
    snippet: str
    page_number: int | str | None = None

class AgentResponse(BaseModel):
    answer: str
    citations: list[Citation] = Field(default_factory = list)
    route_taken: str | None = None
    invalid_citations: set[int] = Field(default_factory= set)
    citation_warning: str | None = None

class ConversationTurn(BaseModel):
    role: str
    content: str