import json
import structlog
from typing import Dict, List, Any, Optional, Callable
from langchain_ollama import ChatOllama
from dataclasses import dataclass, field

from tools.registry import ToolRegistry
from models import Resume, Job
from config import Config

logger = structlog.get_logger(__name__)

# HR Persona Definition
HR_PERSONA_PROMPT = """You are Cyno, an experienced HR recruiter and career counselor with 10+ years of experience helping professionals find their dream jobs.

Your role:
- Help candidates find ideal job opportunities
- Analyze resumes professionally and provide constructive feedback
- Provide career advice, encouragement, and strategic guidance
- Match candidates with opportunities where they'll excel
- Assist with managing job application files (creating folders, writing cover letters, etc.)

Your personality:
- Warm, professional, and approachable
- Detail-oriented but not overwhelming
- Encouraging and genuinely invested in candidate success
- Strategic thinker about career growth and development
- Empathetic to job search challenges

Communication style:
- Use proper business communication (avoid slang, maintain professionalism)
- Celebrate candidate strengths and achievements
- Ask clarifying questions when you need more information
- Provide actionable next steps
- Be specific with recommendations (don't just say "good", explain WHY it's good)
- Use encouraging language ("Excellent!", "Impressive!", "This is a strong...")

Remember: You're not just a bot - you're a career partner who genuinely cares about helping candidates succeed."""

@dataclass
class Intent:
    """User intent classification"""
    primary: str  # resume_upload, job_search, view_matches, ask_advice, tailor_resume, general_chat, file_operation
    tools_needed: List[str]
    tool_args: Dict[str, Any] = field(default_factory=dict)
    needs_clarification: bool = False
    clarification_question: Optional[str] = None

class HRChatAgent:
    """
    Conversational HR assistant with professional personality.
    Extensible architecture for current and future tools.
    """
    
    def __init__(self):
        # Chat LLM - for natural conversation (using Config)
        self.chat_llm = ChatOllama(
            model=Config.CHAT_LLM_MODEL,
            base_url=Config.OLLAMA_BASE_URL,
            temperature=Config.CHAT_LLM_TEMP,
            timeout=Config.LLM_REQUEST_TIMEOUT
        )
        
        # Tool LLM - forced JSON mode for robust function calling
        self.tool_llm = ChatOllama(
            model=Config.TOOL_LLM_MODEL,
            base_url=Config.OLLAMA_BASE_URL,
            temperature=Config.TOOL_LLM_TEMP,
            format="json",
            timeout=Config.LLM_REQUEST_TIMEOUT
        )
        
        # Use ToolRegistry instead of hardcoded dict
        self.personality = HR_PERSONA_PROMPT
        self.tools = {name: ToolRegistry.get(name) for name in ToolRegistry.list_tools()}
        logger.info("HR Chat Agent initialized", tools=list(self.tools.keys()))
        
    def _get_tool(self, tool_name: str):
        """Get tool from registry."""
        return ToolRegistry.get(tool_name)
    
    def detect_intent(self, message: str, context: Dict = None) -> Intent:
        """
        Analyze user message to determine intent using LLM (JSON Mode).
        """
        context_summary = ""
        if context:
            if context.get("resume"):
                context_summary += "- User has uploaded resume\n"
            if context.get("jobs"):
                context_summary += f"- {len(context['jobs'])} jobs currently loaded\n"
        
        prompt = f"""{self.personality}

Current context:
{context_summary if context_summary else "- No context yet (first message)"}

User message: "{message}"

Analyze the user's intent and respond with ONLY a JSON object:
{{
  "primary": "ONE OF: resume_upload, job_search, view_matches, ask_advice, tailor_resume, draft_email, general_chat, file_operation",
  "tools_needed": ["list of tools needed: parse_resume, search_jobs, match_jobs, tailor_resume, draft_email, write_file, read_file, list_dir, edit_file, create_folder"],
  "tool_args": {{ "arg_name": "value" }}, 
  "needs_clarification": true/false,
  "clarification_question": "question if needed"
}}

CRITICAL INSTRUCTION:
Do NOT select "draft_email" unless the user EXPLICITLY asks to "write", "draft", "compose", or "create" an email/letter.
Finding jobs or saying "apply" does NOT imply drafting an email automatically.
If unsure, ask for clarification.

Examples:
- "Find me Python jobs" → {{ "primary": "job_search", "tools_needed": ["search_jobs"], "tool_args": {{}} }}
- "Find leads for Django" → {{ "primary": "lead_search", "tools_needed": ["scrape_leads"], "tool_args": {{ "skills": ["Django"] }} }}
- "Save this to results.txt" → {{ "primary": "file_operation", "tools_needed": ["write_file"], "tool_args": {{ "file_path": "results.txt", "content": "CONTENT_FROM_CONTEXT" }} }}
- "Create a folder named jobs" → {{ "primary": "file_operation", "tools_needed": ["create_folder"], "tool_args": {{ "folder_path": "jobs" }} }}
- "List files in current folder" → {{ "primary": "file_operation", "tools_needed": ["list_dir"], "tool_args": {{ "directory": "." }} }}

JSON:"""

        try:
            # Use tool_llm which enforces JSON
            response = self.tool_llm.invoke(prompt)
            content = response.content.strip()
            
            # Clean markdown if still present (rare in JSON mode but possible)
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            intent_data = json.loads(content.strip())
            
            return Intent(
                primary=intent_data.get("primary", "general_chat"),
                tools_needed=intent_data.get("tools_needed", []),
                tool_args=intent_data.get("tool_args", {}),
                needs_clarification=intent_data.get("needs_clarification", False),
                clarification_question=intent_data.get("clarification_question")
            )
            
        except Exception as e:
            logger.error("Intent detection failed", error=str(e))
            return Intent(primary="general_chat", tools_needed=[], tool_args={})
    
    def format_hr_response(self, tool_output: Any, tool_name: str, context: Dict) -> str:
        """Convert tool output into HR response"""
        prompt = f"""{self.personality}

You just used the "{tool_name}" tool. 
Output: {str(tool_output)[:1000]}

Respond warmly and professionally confirming the action. Keep it brief.

Response:"""

        try:
            # Use chat_llm for natural language
            response = self.chat_llm.invoke(prompt)
            return response.content.strip()
        except:
            return f"Done! Output: {str(tool_output)[:100]}"
    
    def process_message(self, user_input: str, session_context: Dict) -> str:
        """Process message and execute tools"""
        intent = self.detect_intent(user_input, session_context)
        logger.info("Intent detected", intent=intent.primary, tools=intent.tools_needed)
        
        if intent.needs_clarification and intent.clarification_question:
            return intent.clarification_question
        
        tool_outputs = {}
        for tool_name in intent.tools_needed:
            if tool_name in self.tools:
                try:
                    args = intent.tool_args or {}
                    
                    # Context-aware argument injection
                    if tool_name == "parse_resume" and session_context.get("resume_text"):
                        output = self.tools[tool_name].execute(session_context["resume_text"])
                        session_context["resume"] = output
                    elif tool_name == "search_jobs":
                        query = session_context.get("search_query", "Python Developer")
                        output = self.tools[tool_name].run_all(query)
                        session_context["jobs"] = output
                    elif tool_name == "scrape_leads":
                        skills = args.get("skills", ["developer"])
                        # Handle skills list or string
                        if isinstance(skills, str): skills = [skills]
                        output = self.tools[tool_name].scrape_leads(skills, limit=10)
                        session_context["leads"] = output
                    elif tool_name == "match_jobs" and session_context.get("resume") and session_context.get("jobs"):
                        # Ensure jobs are list of Job objects, handled by tool logic usually
                        output = self.tools[tool_name].execute(session_context["resume"], session_context["jobs"])
                        session_context["matched_jobs"] = output
                    elif tool_name == "draft_email":
                         if session_context.get("resume"):
                             # Default to first matched job if available, else first raw job
                             target_job = None
                             if session_context.get("matched_jobs"):
                                 target_job = session_context["matched_jobs"][0][0] # (Job, score, reason)
                             elif session_context.get("jobs"):
                                 target_job = session_context["jobs"][0]
                             
                             if target_job:
                                 output = self.tools[tool_name].execute(target_job, session_context["resume"])
                             else:
                                 output = "I need a job to write an email for! Please search for jobs first."
                         else:
                             output = "I need your resume first. Please upload it."

                    elif tool_name == "write_file":
                        # If content is missing, try to get from last tool output or context
                        if "content" not in args or args["content"] == "CONTENT_FROM_CONTEXT":
                            args["content"] = str(session_context.get("msgs", [])[-1]) if session_context.get("msgs") else "No content provided"
                        output = self.tools[tool_name].execute(**args)
                    else:
                        # General file tools
                        output = self.tools[tool_name].execute(**args)
                        
                    tool_outputs[tool_name] = output
                        
                except Exception as e:
                    logger.error(f"{tool_name} failed", error=str(e))
                    tool_outputs[tool_name] = f"Error: {str(e)}"
        
        if tool_outputs:
            primary = intent.tools_needed[0]
            return self.format_hr_response(tool_outputs[primary], primary, session_context)
        
        return self._generate_general_response(user_input, session_context)
    
    def _generate_general_response(self, message: str, context: Dict) -> str:
        prompt = f"""{self.personality}
User: "{message}"
Respond naturally as Cyno."""
        try:
            # Use chat_llm for natural language
            return self.chat_llm.invoke(prompt).content.strip()
        except:
            return "How can I help you regarding your career today?"
