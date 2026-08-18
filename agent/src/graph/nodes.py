from graph.state import AgentState
from retrieval.retriever import Retriever
from generation.chain import retriever, chain
from generation.prompt import prompt_inputs
from generation.citations import extract_citations
from config import configs

def retrieve_node(state: AgentState) -> dict :
    chunks = retriever.retrieve_chunks(state.question, top_k=configs.top_k_m)
    return {"chunks" : chunks, "route_taken" : "rag"}

def generate_node(state: AgentState) -> dict : 
    inputs = prompt_inputs(state.question, state.chunks)
    answer = chain.invoke(inputs)
    return {"answer": answer}

def validate_citations_node(state: AgentState) -> dict :
    response = extract_citations(state.answer,state.chunks)
    return {"citations": response.citations, "invalid_citations": response.invalid_citations, "citation_warning": response.citation_warning}