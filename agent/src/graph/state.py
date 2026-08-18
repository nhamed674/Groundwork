from pydantic import (BaseModel, Field )
from typing import Any
from generation.models import Chunk, Citation

class AgentState (BaseModel) : 
    question : str
    chunks : list[Chunk] = Field(default_factory=list)
    answer : str =""
    citations : list[Citation] = Field(default_factory=list)
    citation_warning : str | None = None
    invalid_citations : set[int] | list[int] = Field(default_factory=set )
    route_taken : str | None = None


