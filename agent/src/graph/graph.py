from langgraph.graph import StateGraph, START, END
from generation.models import AgentResponse
from graph.nodes import retrieve_node, generate_node, validate_citations_node
from graph.state import AgentState

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("generate",generate_node)
    graph.add_node("validate",validate_citations_node)

    graph.add_edge(START,"retrieve")
    graph.add_edge("retrieve","generate")
    graph.add_edge("generate","validate")
    graph.add_edge("validate",END)
    
    return graph.compile()

app = build_graph()

def run_agent (question : str) -> AgentResponse :
    result = app.invoke({"question": question})
    return AgentResponse(
        answer=result.get("answer"),
        citations=result.get("citations"),
        citation_warning=result.get("citation_warning"),
        invalid_citations=result.get("invalid_citations", set()),
        route_taken=result.get("route_taken")
    )

