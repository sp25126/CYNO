from typing import Dict, Any, List, Optional
import structlog
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage
import traceback

from agent.state import AgentState, RouterDecision, MAX_SEARCH_RETRIES, MAX_EXPAND_RETRIES, safe_append_message
from agent.config import AgentConfig, default_ollama_config
from agent.logging import get_logger, log_event

# Tool Imports
from tools.resume_parser import ResumeParserTool
from tools.job_search import JobSearchTool
from tools.job_matcher import JobMatchingTool
from models import Resume, Job

# Logger
logger = get_logger("agent.nodes")

# --- Routing Logic ---

# --- Helper Functions for Routing ---
def derive_search_query(resume: Resume, user_message: str) -> str:
    """Extract search query from resume skills + user message."""
    if not resume:
        # If no resume, trust the user's message but clean it slightly
        forbidden = ["find", "search", "looking", "for", "me", "show", "jobs"]
        parts = user_message.lower().split()
        clean_parts = [p for p in parts if p not in forbidden]
        return " ".join(clean_parts) if clean_parts else user_message
        
    skills = ", ".join(resume.parsed_skills[:3]) if resume.parsed_skills else "developer"
    location = resume.location if resume.location else ""
    
    # Check if user mentioned remote
    if "remote" in user_message.lower():
        return f"{skills} remote"
    elif location:
        return f"{skills} {location}"
    else:
        return skills

def broaden_search_query(query: str) -> str:
    """Make query less specific (e.g., remove location)."""
    location_keywords = ["bangalore", "mumbai", "delhi", "remote", "india", "usa", "uk"]
    parts = query.split()
    filtered = [p for p in parts if p.lower() not in location_keywords]
    return " ".join(filtered) if filtered else query

async def routing_node(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decides the next action using LLM with strict logic guards.
    This fulfills Roadmap Phase 2D requirements.
    """
    # Unpack state
    parsed_resume = state.get("parsed_resume")
    jobs_found = state.get("jobs_found", [])
    matched_jobs = state.get("matched_jobs", [])
    messages = state.get("messages", [])
    
    # Get last message
    last_user_message = ""
    for msg in reversed(messages):
        if isinstance(msg, dict) and msg.get("role") == "user":
            last_user_message = msg.get("content", "").strip()
            break
        elif hasattr(msg, "type") and msg.type == "human":
             last_user_message = msg.content.strip()
             break

    log_event(logger, "routing_node_start", task="decide_next_step")

    # --- 1. LOGIC GUARDS (Safety First) ---
    
    # Guard A: Resume Parsing Loop Prevention
    # If we already have a resume, do not trigger parsing on keywords unless EXPLICITLY requested.
    resume_keywords = ["resume", "cv", "bio", "file"]
    is_resume_mention = any(k in last_user_message.lower() for k in resume_keywords)
    
    if is_resume_mention and not parsed_resume:
        # User mentioned resume and we don't have one -> Parse it.
        return {"next_step": "parse_resume"}
        
    # Guard B: Explicit Search Command
    # If user says "find/search", bypass interview logic.
    search_keywords = ["find", "search", "looking for", "jobs"]
    if any(k in last_user_message.lower() for k in search_keywords):
        derived = derive_search_query(parsed_resume, last_user_message)
        # Check if we just searched to avoid loops? 
        # For now, let's allow re-search if user asks.
        return {"next_step": "search", "search_query": derived}

    # --- 2. LLM DECISION (Intelligence) ---
    try:
        # Use helper instead of circular import
        from langchain_core.messages import SystemMessage, HumanMessage
        llm = _get_llm() 

        system_prompt = """You are the Job Agent Brain. Decide the next step.
        OPTIONS: 'parse_resume', 'search_jobs', 'match_jobs', 'respond'.
        
        RULES:
        1. 'parse_resume': User sent resume text/file AND we haven't parsed it.
        2. 'search_jobs': We have requirements (or resume) and need jobs.
        3. 'match_jobs': We have found jobs but haven't ranked them.
        4. 'respond': We have matches or need to ask questions.
        
        Output ONLY the option string.
        """
        
        user_prompt = f"""
        Has Resume: {parsed_resume is not None}
        Jobs Found: {len(jobs_found)}
        Jobs Matched: {len(matched_jobs)}
        Last Message: {last_user_message[:200]}
        """
        
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # Clean Markdown
        decision = response.content.strip().replace("'", "").replace('"', "")
        if "```" in decision:
            decision = decision.split("```")[1].replace("tool_code", "").strip()
            
        log_event(logger, "router_llm_decision", decision=decision)

        # Map decisions
        if "parse" in decision and not parsed_resume: return {"next_step": "parse_resume"}
        if "search" in decision: 
             q = derive_search_query(parsed_resume, last_user_message)
             return {"next_step": "search", "search_query": q}
        if "match" in decision: return {"next_step": "match"}
        
        return {"next_step": "respond"}

    except Exception as e:
        # Fallback to Heuristics if LLM fails
        log_event(logger, "router_llm_failed", error=str(e))
        
        # Fallback Logic
        if parsed_resume and not jobs_found: return {"next_step": "search", "search_query": derive_search_query(parsed_resume, last_user_message)}
        if jobs_found and not matched_jobs: return {"next_step": "match"}
        return {"next_step": "respond"}

# --- Functional Nodes ---

async def parse_resume_node(state: AgentState) -> Dict[str, Any]:
    log_event(logger, "parse_resume_node_start")
    try:
        messages = state.get("messages", [])
        resume_text = messages[-1]["content"] if messages else ""
        
        # Tool call
        resume = ResumeParserTool().execute(resume_text)
        print(f"DEBUG: parse_resume_node Got resume: {resume}")
        
        log_event(logger, "parse_resume_node_success")
        return {"parsed_resume": resume}
        
    except Exception as e:
        print(f"DEBUG: EXCEPTION in parse_resume: {type(e)} {e}")
        log_event(logger, "parse_resume_node_error", error=str(e))
        # Don't crash, just let the router handle missing resume or respond node explain
        return {"error": str(e)}

async def job_search_node(state: AgentState) -> Dict[str, Any]:
    log_event(logger, "job_search_node_start", query=state.get("search_query"))
    try:
        query = state.get("search_query")
        if not query:
            raise ValueError("No search query provided")

        # Tool call
        jobs = await JobSearchTool().execute(query=query, source="all")
        
        log_event(logger, "job_search_node_success", count=len(jobs))
        return {"jobs_found": jobs}
        
    except Exception as e:
        log_event(logger, "job_search_node_error", error=str(e))
        return {"jobs_found": []} # Return empty list so router sees failure

async def matching_node(state: AgentState) -> Dict[str, Any]:
    log_event(logger, "matching_node_start")
    try:
        resume = state.get("parsed_resume")
        jobs = state.get("jobs_found", [])
        
        if not resume or not jobs:
             log_event(logger, "matching_node_skipped", reason="Missing resume or jobs")
             return {"matched_jobs": []}

        # Tool call
        matches = await JobMatchingTool().execute(resume=resume, jobs=jobs)
        
        log_event(logger, "matching_node_success", match_count=len(matches))
        return {"matched_jobs": matches}

    except Exception as e:
        log_event(logger, "matching_node_error", error=str(e))
        return {"matched_jobs": []}

async def response_node(state: AgentState) -> Dict[str, Any]:
    log_event(logger, "response_node_start")
    try:
        # Construct summary using LLM or structured string
        messages = state.get("messages", [])
        matched_jobs = state.get("matched_jobs", [])
        parsed_resume = state.get("parsed_resume")
        
        if not parsed_resume:
            response_text = "I need your resume to proceed. Please paste it or describe your background."
        elif not matched_jobs:
            if state.get("jobs_found"):
                 response_text = "I found some jobs but none matched your profile well. Would you like to adjust the search?"
            else:
                 response_text = f"I couldn't find any jobs for '{state.get('search_query')}'. Please try a different query."
        else:
            # Top 3 matches
            top_matches = matched_jobs[:3]
            response_text = "Here are the top matches I found:\n\n"
            for job, score, reason in top_matches:
                response_text += f"- **{job.title}** at {job.company} (Score: {score:.1f})\n  *{reason}*\n  [Apply]({job.apply_url})\n\n"
            response_text += "Shall I draft emails for these?"

        # Update state with response
        new_messages = list(messages)
        new_messages.append({"role": "assistant", "content": response_text})
        
        log_event(logger, "response_node_success")
        return {"messages": new_messages, "next_step": "end"}

    except Exception as e:
        log_event(logger, "response_node_error", error=str(e))
        new_messages = list(state.get("messages", []))
        new_messages.append({"role": "assistant", "content": "I encountered an error generating a response."})
        return {"messages": new_messages, "next_step": "end"}

# --- Private Helpers ---

async def _generate_search_query(resume: Any, user_msg: str) -> str:
    """
    Generates a search query using Ollama.
    """
    try:
        llm = _get_llm()
        prompt = f"""
        Based on these skills: {resume.parsed_skills if resume else 'General'}
        And user request: {user_msg}
        
        Generate a concise job search query (max 5 words).
        Return ONLY the query string.
        """
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip().replace('"', '')
    except Exception:
        return f"{resume.parsed_skills[0]} developer" if resume and resume.parsed_skills else "software engineer"

async def _refine_search_query(current_query: str, instruction: str) -> str:
    """
    Refines a query using Ollama.
    """
    try:
        llm = _get_llm()
        prompt = f"Current query: {current_query}. Instruction: {instruction}. Return ONLY the new query string, max 5 words."
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        return response.content.strip().replace('"', '')
    except Exception:
        return current_query + " remote" # Fallback primitive expansion

def _get_llm():
    # Helper to get ChatOllama instance
    # In production, check config for base_url
    return ChatOllama(
        model=default_ollama_config.model,
        base_url=default_ollama_config.base_url
    )
