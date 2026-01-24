from typing import Dict, Any, Optional
import traceback
from agent.state import AgentState, ensure_state_defaults
from agent.config import AgentConfig
from agent.nodes import (
    routing_node, 
    parse_resume_node, 
    job_search_node, 
    matching_node, 
    response_node
)
from agent.logging import get_logger, log_event

logger = get_logger("agent.orchestrator")

class JobAgentOrchestrator:
    def __init__(
        self, 
        resume_tool: Any = None, 
        search_tool: Any = None, 
        match_tool: Any = None, 
        llm_local: Any = None, 
        llm_gemini: Any = None, 
        config: AgentConfig = AgentConfig()
    ):
        """
        Initializes the orchestrator (Pure Python Version).
        Args:
           resume_tool, search_tool, match_tool: Tool instances (dependency injection placeholder).
           llm_local, llm_gemini: LLM instances.
           config: Agent configuration.
        """
        self.config = config
        self.resume_tool = resume_tool
        self.search_tool = search_tool
        self.match_tool = match_tool
        
    async def run(
        self, 
        user_message: str, 
        session_id: str, 
        resume_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the agent workflow using a State Machine Loop.
        """
        log_event(logger, "run_start", session_id=session_id)
        
        # 1. Init State
        state = ensure_state_defaults({})
        state["messages"].append({"role": "user", "content": user_message})
        
        if resume_text:
             state["messages"][-1]["content"] += f"\n\nRESUME CONTENT:\n{resume_text}"

        # 2. State Machine Loop
        MAX_STEPS = 15
        
        try:
            while state["step_count"] < MAX_STEPS:
                # A. Decide Next Step
                decision = await routing_node(state)
                next_action = decision.get("next_step", "respond")
                state.update(decision) # Merge decision fields (e.g. search_query)
                
                log_event(logger, "step_decision", step=state["step_count"], action=next_action)
                
                # B. Execute Action
                if next_action == "parse_resume":
                    update = await parse_resume_node(state)
                    state.update(update)
                    
                elif next_action == "search":
                    update = await job_search_node(state)
                    state.update(update)
                    
                elif next_action == "match":
                    update = await matching_node(state)
                    state.update(update)
                    
                elif next_action == "respond":
                    update = await response_node(state)
                    state.update(update)
                    state["step_count"] += 1
                    break # End of turn
                
                elif next_action == "end":
                    break
                    
                else:
                    logger.warning(f"Unknown next_action: {next_action}. Defaulting to respond.")
                    update = await response_node(state)
                    state.update(update)
                    break 
                
                # C. Increment Step & Loop back for Routing (unless we broke out)
                state["step_count"] += 1
            
            log_event(logger, "run_success", session_id=session_id)
            return state
        
        except Exception as e:
            log_event(logger, "run_error", session_id=session_id, error=str(e))
            traceback.print_exc()
            return {"error": str(e), "messages": state["messages"]}
