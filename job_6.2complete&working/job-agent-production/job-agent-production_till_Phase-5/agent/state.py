from typing import TypedDict, List, Literal, Tuple, Dict, Optional, Any
from pydantic import BaseModel, Field
from models import Resume, Job, EmailDraft

# --- Constants ---
MAX_SEARCH_RETRIES = 2
MAX_EXPAND_RETRIES = 1

# --- State Definitions ---

class AgentState(TypedDict):
    """
    TypedDict representing the state of the agent as per Phase 2D roadmap.
    """
    messages: List[Dict[str, Any]]  # {role, content}
    parsed_resume: Optional[Resume]
    search_query: Optional[str]
    jobs_found: List[Job]
    matched_jobs: List[Tuple[Job, float, str]]
    email_drafts: List[EmailDraft]
    search_retry_count: int
    expand_retry_count: int
    step_count: int

class RouterDecision(BaseModel):
    """
    Pydantic model for the router's decision on the next step.
    """
    next_step: Literal["parse_resume", "search", "match", "respond", "end"]
    reason: str
    updated_search_query: Optional[str] = None
    retry_count_delta: int = Field(default=0, ge=0, le=1)

# --- Helper Functions ---

def ensure_state_defaults(state: Dict[str, Any]) -> AgentState:
    """
    Ensures that the state dictionary has all the required keys with default values.
    Useful when initializing the graph or recovering from partial state.
    """
    defaults: AgentState = {
        "messages": [],
        "parsed_resume": None,
        "search_query": None,
        "jobs_found": [],
        "matched_jobs": [],
        "email_drafts": [],
        "search_retry_count": 0,
        "expand_retry_count": 0,
        "step_count": 0
    }
    
    # Merge defaults with existing state, preserving existing values
    for key, value in defaults.items():
        if key not in state:
            state[key] = value # type: ignore
            
    return state # type: ignore

def safe_append_message(state: AgentState, role: str, content: str) -> AgentState:
    """
    Safely appends a message to the state's message list.
    Returns the updated state.
    """
    if "messages" not in state:
        state["messages"] = []
    
    state["messages"].append({"role": role, "content": content})
    return state
