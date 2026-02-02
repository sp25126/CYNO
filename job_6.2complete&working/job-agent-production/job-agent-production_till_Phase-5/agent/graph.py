from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    parse_resume_node,
    job_search_node,
    job_matching_node,
    routing_node,
    response_node
)

def build_agent_graph():
    """
    Builds the StateGraph for the Job Agent.
    """
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("router", routing_node)
    workflow.add_node("parse_resume", parse_resume_node)
    workflow.add_node("search_jobs", job_search_node)
    workflow.add_node("match_jobs", job_matching_node)
    workflow.add_node("respond", response_node)


    # 2. Define Entry Point
    workflow.set_entry_point("router")

    # 3. Define Conditional Edges from the Router
    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("next_step"),
        {
            "parse_resume": "parse_resume",
            "search": "search_jobs",
            "respond": "respond"
        }
    )

    # 4. Define the Main Flow
    workflow.add_edge("parse_resume", "search_jobs")
    workflow.add_conditional_edges(
        "search_jobs",
        lambda state: "match_jobs" if state.get("jobs_found") else "respond",
        {
            "match_jobs": "match_jobs",
            "respond": "respond"
        }
    )
    
    workflow.add_conditional_edges(
        "match_jobs",
        lambda state: "respond" if state.get("matched_jobs") else "respond",
         {
            "respond": "respond"
        }
    )

    workflow.add_edge("respond", END)

    return workflow.compile()
