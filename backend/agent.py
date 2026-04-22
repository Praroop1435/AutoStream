from langgraph.graph import StateGraph, START, END
from backend.core import AgentState
from backend.nodes import (
    classify_intent, 
    retrieve_context, 
    generate_response, 
    execute_lead_capture
)

def route_after_classification(state: AgentState):
    intent = state.get("intent", "unknown")
    if intent == "inquiry":
        return "retrieve_context"
    return "generate_response"

def route_after_generation(state: AgentState):
    lead_info = state.get("lead_info", {})
    captured = state.get("lead_captured", False)
    
    has_all_info = all([
        lead_info.get("name"),
        lead_info.get("email"),
        lead_info.get("platform")
    ])
    
    if has_all_info and not captured:
        return "execute_lead_capture"
    return END

workflow = StateGraph(AgentState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("generate_response", generate_response)
workflow.add_node("execute_lead_capture", execute_lead_capture)

workflow.add_edge(START, "classify_intent")

workflow.add_conditional_edges(
    "classify_intent",
    route_after_classification,
    {
        "retrieve_context": "retrieve_context",
        "generate_response": "generate_response"
    }
)

workflow.add_edge("retrieve_context", "generate_response")

workflow.add_conditional_edges(
    "generate_response",
    route_after_generation,
    {
        "execute_lead_capture": "execute_lead_capture",
        END: END
    }
)

workflow.add_edge("execute_lead_capture", END)

compiled_graph = workflow.compile()
