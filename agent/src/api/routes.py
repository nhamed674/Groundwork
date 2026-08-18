from fastapi import APIRouter, HTTPException
from api.schemas import AgentResponse, ChatRequest
from graph.graph import run_agent

router = APIRouter(tags=["chat"])

@router.post("/chat",response_model=AgentResponse)
def chat(request: ChatRequest) -> AgentResponse :
    try:
        return run_agent(request.question)
    except Exception as e:
        raise HTTPException(status_code=500,detail="Agent failed to answer") from e
    
    

