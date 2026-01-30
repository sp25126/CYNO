"""
CYNO NLP Tool Router - Intelligent Natural Language Tool Selection
The brain that understands user intent and routes to the right tools.
FULLY INTEGRATED VERSION - All 25+ Tools Connected
"""

import os
import json
import structlog
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

logger = structlog.get_logger(__name__)


@dataclass
class ToolIntent:
    """Represents parsed user intent."""
    primary_action: str
    tools_needed: List[str]
    parameters: Dict[str, Any]
    confidence: float
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    natural_response: str = ""


class CynoNLPRouter:
    """
    Intelligent NLP-based tool router.
    Understands natural language and decides which tools to use.
    FULLY INTEGRATED with all CYNO tools.
    """
    
    # Complete Intent patterns for ALL tools
    INTENT_PATTERNS = {
        # ===================
        # Interview Prep (GitHub-Powered)
        # ===================
        "interview_prep": {
            "keywords": ["interview", "prepare", "question", "practice", "behavioral", "technical", "star", "mock"],
            "tools": ["project_deep_dive", "technical_q_generator", "behavioral_answer_bank"],
            "requires": ["github_username"],
            "response": "Let me analyze your GitHub and prepare interview questions for you! 🎯"
        },
        "project_analysis": {
            "keywords": ["analyze", "project", "github", "repo", "repository", "deep dive", "my projects"],
            "tools": ["project_deep_dive"],
            "requires": ["github_username"],
            "response": "Analyzing your GitHub projects... 🔍"
        },
        "technical_questions": {
            "keywords": ["technical question", "coding question", "algorithm", "code review", "explain code"],
            "tools": ["technical_q_generator"],
            "requires": [],
            "response": "Generating technical interview questions... 💻"
        },
        "behavioral_prep": {
            "keywords": ["behavioral", "star format", "tell me about a time", "challenge story", "conflict"],
            "tools": ["behavioral_answer_bank"],
            "requires": [],
            "response": "Creating STAR-format behavioral answers... 📝"
        },
        "why_this_tech": {
            "keywords": ["why did you use", "why choose", "technology choice", "react vs", "python vs"],
            "tools": ["why_this_tech"],
            "requires": [],
            "response": "Preparing technology choice explanations... 🔧"
        },
        "interviewer_questions": {
            "keywords": ["questions to ask", "ask interviewer", "what should i ask", "smart questions"],
            "tools": ["company_question_generator"],
            "requires": ["company_name"],
            "response": "Generating smart questions to ask the interviewer... 💡"
        },
        
        # ===================
        # Job Search & Discovery
        # ===================
        "job_search": {
            "keywords": ["find job", "search job", "looking for job", "job opening", "hiring", "vacancy", 
                        "jobs", "developer", "engineer", "remote", "nyc", "san francisco", "python", 
                        "javascript", "frontend", "backend", "fullstack", "data scientist", "ml engineer"],
            "tools": ["search_jobs"],
            "requires": ["job_query"],
            "response": "Searching for job opportunities... 🔎"
        },
        "lead_generation": {
            "keywords": ["find leads", "find clients", "freelance", "prospect", "email list", "scrape leads"],
            "tools": ["scrape_leads"],
            "requires": ["industry"],
            "response": "Finding potential leads... 📧"
        },
        "company_research": {
            "keywords": ["research company", "about company", "company info", "culture", "glassdoor", 
                        "tell me about", "what is", "who is"],
            "tools": ["company_stalker"],
            "requires": ["company_name"],
            "response": "Researching company information... 🏢"
        },
        "salary_info": {
            "keywords": ["salary", "compensation", "pay", "how much", "salary range", "market rate"],
            "tools": ["salary_estimator"],
            "requires": ["job_title"],
            "response": "Looking up salary information... 💰"
        },
        
        # ===================
        # Resume & Documents
        # ===================
        "parse_resume": {
            "keywords": ["parse resume", "analyze resume", "read resume", "understand resume", "extract from resume"],
            "tools": ["parse_resume"],
            "requires": ["resume_text"],
            "response": "Parsing your resume... 📄"
        },
        "generate_resume": {
            "keywords": ["create resume", "generate resume", "build resume", "make resume", "new resume", "resume from github"],
            "tools": ["generate_resume", "github_scraper"],
            "requires": ["github_username"],
            "response": "Creating your resume from GitHub data... 📋"
        },
        "tailor_resume": {
            "keywords": ["tailor resume", "customize resume", "adapt resume", "specific job resume", "optimize resume"],
            "tools": ["generate_resume", "ats_scorer"],
            "requires": ["resume", "job"],
            "response": "Tailoring your resume for this job... ✨"
        },
        "ats_check": {
            "keywords": ["ats score", "ats check", "ats friendly", "resume score", "keyword match", "applicant tracking"],
            "tools": ["ats_scorer"],
            "requires": ["resume_text", "job_description"],
            "response": "Scoring your resume for ATS compatibility... 📊"
        },
        
        # ===================
        # Cover Letter & Email
        # ===================
        "cover_letter": {
            "keywords": ["cover letter", "application letter", "intro letter", "write cover"],
            "tools": ["cover_letter_generator"],
            "requires": ["company_name", "job_title"],
            "response": "Writing your cover letter... ✉️"
        },
        "draft_email": {
            "keywords": ["write email", "draft email", "email template", "application email"],
            "tools": ["draft_email"],
            "requires": ["recipient", "purpose"],
            "response": "Drafting your email... 📧"
        },
        "cold_email": {
            "keywords": ["cold email", "outreach email", "reach out", "contact recruiter", "email sequence"],
            "tools": ["cold_email_sequencer"],
            "requires": ["company_name"],
            "response": "Creating email outreach sequence... 📬"
        },
        "referral_request": {
            "keywords": ["referral", "refer me", "ask for referral", "internal referral", "connection"],
            "tools": ["referral_request_writer"],
            "requires": ["contact_name", "company_name"],
            "response": "Writing referral request message... 🤝"
        },
        
        # ===================
        # Application Tracking
        # ===================
        "add_followup": {
            "keywords": ["add follow up", "remind me", "track application", "applied to", "set reminder"],
            "tools": ["follow_up_reminder"],
            "requires": ["company_name"],
            "response": "Setting up follow-up reminder... ⏰"
        },
        "check_followups": {
            "keywords": ["check follow up", "pending follow", "due today", "what's due", "my applications"],
            "tools": ["follow_up_reminder"],
            "requires": [],
            "response": "Checking your follow-up schedule... 📅"
        },
        
        # ===================
        # Skills & Learning
        # ===================
        "skill_gap": {
            "keywords": ["skill gap", "missing skills", "need to learn", "improve skills", "what should i learn",
                        "skills for", "required skills"],
            "tools": ["skill_gap_analyzer"],
            "requires": [],
            "response": "Analyzing your skill gaps... 📚"
        },
        "match_jobs": {
            "keywords": ["match jobs", "fit score", "how well do i fit", "compare skills", "job fit"],
            "tools": ["match_jobs"],
            "requires": ["resume", "job"],
            "response": "Calculating job match score... 🎯"
        },
        
        # ===================
        # File Operations
        # ===================
        "save_file": {
            "keywords": ["save to file", "write file", "export", "save as"],
            "tools": ["write_file"],
            "requires": ["content", "filename"],
            "response": "Saving to file... 💾"
        },
        "read_file": {
            "keywords": ["read file", "open file", "load file", "show file"],
            "tools": ["read_file"],
            "requires": ["filename"],
            "response": "Reading file... 📂"
        },
        
        # ===================
        # General
        # ===================
        "help": {
            "keywords": ["help", "what can you do", "capabilities", "how to use", "commands", "features"],
            "tools": [],
            "requires": [],
            "response": ""
        }
    }
    
    def __init__(self, use_cloud: bool = True):
        self.cloud_url = os.getenv("COLAB_SERVER_URL") if use_cloud else None
        self.conversation_context: Dict[str, Any] = {}
    
    def route(self, user_message: str, context: Dict[str, Any] = None) -> ToolIntent:
        """Analyze user message and determine which tools to use."""
        log = logger.bind(router="CynoNLP")
        log.info("routing_message", message_length=len(user_message))
        
        if context:
            self.conversation_context.update(context)
        
        # Try LLM-based intent detection (works on Cloud or Local)
        try:
            intent = self._detect_intent_llm(user_message)
            if intent and intent.confidence > 0.7:
                return intent
        except Exception as e:
            log.warning("llm_routing_failed", error=str(e))
        
        # Fallback to rule-based routing
        return self._detect_intent_local(user_message)
    
    def _detect_intent_llm(self, message: str) -> Optional[ToolIntent]:
        """
        Use LLM for sophisticated intent detection.
        Works on both Cloud GPU and Local Ollama (same prompts).
        """
        try:
            from agent.llm_brain import get_brain
            brain = get_brain()
        except ImportError:
            return None
        
        available_intents = list(self.INTENT_PATTERNS.keys())
        
        prompt = f"""You are CYNO, an intelligent job search assistant. Analyze this user message and determine what they want.

User message: "{message}"

Available actions: {available_intents}

Return JSON only:
{{"primary_action": "action_name", "tools_needed": ["tool1"], "parameters": {{}}, "confidence": 0.9, "natural_response": "response"}}"""
        
        result = brain.generate(prompt, max_tokens=300, temperature=0.2, output_format="json")
        
        if result.get("success") and isinstance(result.get("result"), dict):
            parsed = result["result"]
            return ToolIntent(
                primary_action=parsed.get("primary_action", "help"),
                tools_needed=parsed.get("tools_needed", []),
                parameters=parsed.get("parameters", {}),
                confidence=parsed.get("confidence", 0.5),
                needs_clarification=parsed.get("needs_clarification", False),
                clarification_question=parsed.get("clarification_question"),
                natural_response=parsed.get("natural_response", "")
            )
        
        return None
    
    
    def _detect_intent_local(self, message: str) -> ToolIntent:
        """Enhanced rule-based intent detection."""
        message_lower = message.lower()
        
        best_match = None
        best_score = 0
        
        for intent_name, intent_config in self.INTENT_PATTERNS.items():
            score = 0
            for keyword in intent_config["keywords"]:
                if keyword in message_lower:
                    # Longer keywords get more weight
                    score += len(keyword.split())
            
            if score > best_score:
                best_score = score
                best_match = (intent_name, intent_config)
        
        if best_match and best_score > 0:
            intent_name, config = best_match
            params = self._extract_parameters(message, config.get("requires", []))
            missing_params = [p for p in config.get("requires", []) if not params.get(p)]
            needs_clarification = len(missing_params) > 0 and not self._can_use_context(missing_params)
            
            clarification = None
            if needs_clarification:
                clarification = self._generate_clarification_question(intent_name, missing_params)
            
            # Fill from context if available
            for param in missing_params:
                if param in self.conversation_context:
                    params[param] = self.conversation_context[param]
            
            return ToolIntent(
                primary_action=intent_name,
                tools_needed=config.get("tools", []),
                parameters=params,
                confidence=min(best_score / 4, 1.0),
                needs_clarification=needs_clarification,
                clarification_question=clarification,
                natural_response=config.get("response", "Let me help you with that! 🚀")
            )
        
        return ToolIntent(
            primary_action="help",
            tools_needed=[],
            parameters={},
            confidence=0.3,
            needs_clarification=False,
            natural_response=self._get_help_response()
        )
    
    def _can_use_context(self, missing: List[str]) -> bool:
        """Check if missing params are in context."""
        for param in missing:
            if param not in self.conversation_context:
                return False
        return True
    
    def _extract_parameters(self, message: str, required: List[str]) -> Dict[str, Any]:
        """Extract parameters from message."""
        import re
        params = {}
        
        # GitHub username
        if "github_username" in required or any("github" in r for r in required):
            match = re.search(r'github\.com/(\w+)|@(\w+)|github\s+(\w+)', message, re.I)
            if match:
                params["github_username"] = match.group(1) or match.group(2) or match.group(3)
            elif self.conversation_context.get("github_username"):
                params["github_username"] = self.conversation_context["github_username"]
        
        # Job query - extract what comes after common phrases
        if "job_query" in required:
            patterns = [
                r'(?:find|search|looking for|get)\s+(.+?)(?:\s+jobs?|\s+positions?|\s+roles?|$)',
                r'(.+?)\s+(?:jobs?|positions?|roles?|opportunities)',
            ]
            for pattern in patterns:
                match = re.search(pattern, message, re.I)
                if match:
                    params["job_query"] = match.group(1).strip()
                    break
            if not params.get("job_query"):
                # Extract key terms
                terms = []
                job_keywords = ["python", "javascript", "react", "frontend", "backend", "fullstack", 
                              "data", "ml", "ai", "devops", "cloud", "remote", "senior", "junior"]
                for kw in job_keywords:
                    if kw in message.lower():
                        terms.append(kw)
                if terms:
                    params["job_query"] = " ".join(terms)
        
        # Company name - look for known patterns
        if "company_name" in required:
            patterns = [
                r'(?:at|for|about|to)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)',
                r'([A-Z][a-zA-Z]+)\s+(?:company|inc|corp|llc)',
            ]
            for pattern in patterns:
                match = re.search(pattern, message)
                if match:
                    params["company_name"] = match.group(1).strip()
                    break
        
        # Job title
        if "job_title" in required:
            match = re.search(r'(?:for|as)\s+(?:a\s+)?(.+?)(?:\s+at|\s+role|$)', message, re.I)
            if match:
                params["job_title"] = match.group(1).strip()
        
        # Contact name (for referrals)
        if "contact_name" in required:
            match = re.search(r'(?:ask|contact|reach out to)\s+(\w+(?:\s+\w+)?)', message, re.I)
            if match:
                params["contact_name"] = match.group(1).strip()
        
        return params
    
    def _generate_clarification_question(self, intent: str, missing: List[str]) -> str:
        """Generate a natural clarification question."""
        questions = {
            "github_username": "What's your GitHub username? I'll analyze your projects.",
            "job_query": "What type of job are you looking for? (e.g., 'Python developer', 'Data Scientist')",
            "company_name": "Which company?",
            "job_title": "What job title are you targeting?",
            "resume_text": "Please share your resume text.",
            "job_description": "Please paste the job description.",
            "industry": "What industry are you targeting?",
            "contact_name": "Who would you like to contact?",
            "recipient": "Who should I address this to?",
            "purpose": "What's the purpose of this email?",
        }
        
        if missing:
            return questions.get(missing[0], f"I need more info: {missing[0]}")
        return "Could you tell me more?"
    
    def _get_help_response(self) -> str:
        """Return comprehensive help message."""
        return """👋 **Hi! I'm CYNO, your AI job search assistant.**

🎯 **Interview Prep** (powered by your GitHub)
- "Prepare me for interviews" - Custom Q&A from your projects
- "Help with behavioral questions"
- "What questions should I ask the interviewer?"

💼 **Job Search**
- "Find Python developer jobs in NYC"
- "Search remote frontend positions"

📄 **Resume & Applications**
- "Generate resume from my GitHub"
- "Check my resume ATS score"
- "Write cover letter for Google"

📧 **Outreach**
- "Draft cold email sequence"
- "Write referral request"
- "Track my application follow-ups"

🏢 **Research**
- "Research [company name]"
- "What's the salary for [job title]?"

📚 **Skills**
- "What skills am I missing?"
- "How well do I fit this job?"

**Just type naturally!** I understand plain English. 🚀"""


class CynoAgent:
    """
    The main CYNO agent that orchestrates ALL tools based on NLP understanding.
    FULLY INTEGRATED VERSION.
    """
    
    def __init__(self):
        self.router = CynoNLPRouter()
        self.context: Dict[str, Any] = {}
        self.tool_registry = None
        self._init_tools()
    
    def _init_tools(self):
        """Initialize and register ALL tools."""
        from tools.registry import ToolRegistry, initialize_registry
        
        # Initialize all tools from registry
        initialize_registry()
        self.tool_registry = ToolRegistry
        
        # Log registered tools
        tools = ToolRegistry.list_tools()
        logger.info("tools_registered", count=len(tools), tools=tools)
    
    def chat(self, user_message: str) -> str:
        """Main entry point for user interaction."""
        log = logger.bind(agent="CYNO")
        log.info("user_message", message=user_message[:100])
        
        # Route the message
        intent = self.router.route(user_message, self.context)
        log.info("intent_detected", 
                action=intent.primary_action, 
                tools=intent.tools_needed,
                confidence=intent.confidence)
        
        # Check if clarification is needed
        if intent.needs_clarification:
            return f"🤔 {intent.clarification_question}"
        
        # Special handling for help
        if intent.primary_action == "help":
            return intent.natural_response
        
        # Execute tools
        results = []
        for tool_name in intent.tools_needed:
            tool = self.tool_registry.get(tool_name)
            if tool:
                try:
                    log.info("executing_tool", tool=tool_name)
                    result = self._execute_tool(tool, tool_name, intent.parameters)
                    results.append({"tool": tool_name, "result": result, "success": True})
                except Exception as e:
                    log.error("tool_execution_failed", tool=tool_name, error=str(e))
                    results.append({"tool": tool_name, "error": str(e), "success": False})
            else:
                log.warning("tool_not_found", tool=tool_name)
        
        # Generate response
        if results:
            return self._format_results(intent, results)
        else:
            return intent.natural_response
    
    def _execute_tool(self, tool: Any, tool_name: str, params: Dict) -> Any:
        """Execute a tool with appropriate parameters."""
        
        # Interview Prep Tools
        if tool_name == "project_deep_dive":
            username = params.get("github_username") or self.context.get("github_username", "")
            return tool.execute(username=username)
        
        elif tool_name == "technical_q_generator":
            return tool.execute(
                code_snippet=params.get("code", "# Sample code"),
                language=params.get("language", "python"),
                context=params.get("context", "")
            )
        
        elif tool_name == "behavioral_answer_bank":
            return tool.execute(
                question=params.get("question", "Tell me about a challenge you faced"),
                project_context=self.context.get("project_context", {}),
                experience_years=self.context.get("experience_years", 0)
            )
        
        elif tool_name == "why_this_tech":
            return tool.execute(
                tech_used=params.get("tech", "Python"),
                alternatives=params.get("alternatives", ["Java", "Go"]),
                project_context=self.context.get("project_context", {})
            )
        
        elif tool_name == "company_question_generator":
            return tool.execute(
                company=params.get("company_name", "the company"),
                job_title=params.get("job_title", "Software Engineer"),
                interview_stage=params.get("stage", "final")
            )
        
        # Job Search Tools
        elif tool_name == "search_jobs":
            # JobSearchTool uses run_all, not execute
            if hasattr(tool, 'run_all'):
                return tool.run_all(query=params.get("job_query", "software developer"), limit=20)
            elif hasattr(tool, 'search_jobspy'):
                return tool.search_jobspy(term=params.get("job_query", "software developer"))
            return {"error": "Job search not available"}
        
        elif tool_name == "scrape_leads":
            # LeadScraperTool uses scrape_leads method
            if hasattr(tool, 'scrape_leads'):
                return tool.scrape_leads(industry=params.get("industry", "technology"))
            return {"error": "Lead scraper not available"}
        
        elif tool_name == "company_stalker":
            return tool.execute(company_name=params.get("company_name", ""))
        
        # Resume Tools
        elif tool_name == "parse_resume":
            return tool.execute(resume_text=params.get("resume_text", ""))
        
        elif tool_name == "generate_resume":
            github_data = None
            username = params.get("github_username") or self.context.get("github_username")
            if username:
                from tools.profile_scrapers import scrape_github
                github_data = scrape_github(username)
            
            return tool.generate_resume(
                profile=tool.aggregate_from_sources(
                    resume_data=self.context.get("resume", {}),
                    github_data=github_data
                )
            )
        
        elif tool_name == "ats_scorer":
            return tool.execute(
                resume_text=params.get("resume_text", str(self.context.get("resume", ""))),
                job_description=params.get("job_description", "")
            )
        
        # Cover Letter & Email Tools
        elif tool_name == "cover_letter_generator":
            return tool.execute(
                job_title=params.get("job_title", "Software Engineer"),
                company=params.get("company_name", ""),
                job_description=params.get("job_description", ""),
                resume_data=self.context.get("resume", {}),
                tone="professional"
            )
        
        elif tool_name == "draft_email":
            # EmailDraftTool expects Job and Resume models
            try:
                from models import Job, Resume
                job = Job(
                    title=params.get("job_title", "Software Engineer"),
                    company=params.get("company_name", "Company"),
                    location="Remote",
                    description=params.get("job_description", ""),
                    url=""
                )
                resume_data = self.context.get("resume", {})
                resume = Resume(
                    raw_text="",
                    parsed_skills=resume_data.get("skills", []),
                    education_level=resume_data.get("education", ""),
                    years_exp=resume_data.get("years_exp", 0)
                )
                return tool.execute(job=job, resume=resume)
            except Exception as e:
                # Fallback: return simple draft
                return {
                    "subject": f"Application for {params.get('job_title', 'Position')}",
                    "body": f"I am interested in the {params.get('job_title', 'position')} at {params.get('company_name', 'your company')}.",
                    "error": str(e)
                }
        
        elif tool_name == "cold_email_sequencer":
            return tool.execute(
                recipient_name=params.get("recipient", "Hiring Manager"),
                company=params.get("company_name", ""),
                job_title=params.get("job_title", "Software Engineer"),
                your_name=self.context.get("name", "Candidate"),
                sequence_type="job_application"
            )
        
        elif tool_name == "referral_request_writer":
            return tool.execute(
                contact_name=params.get("contact_name", ""),
                relationship=params.get("relationship", "professional contact"),
                company=params.get("company_name", ""),
                job_title=params.get("job_title", ""),
                your_name=self.context.get("name", "")
            )
        
        # Follow-up Tools
        elif tool_name == "follow_up_reminder":
            action = params.get("action", "check")
            return tool.execute(
                action=action,
                company=params.get("company_name", ""),
                job_title=params.get("job_title", ""),
                applied_date=params.get("applied_date", "")
            )
        
        # Skill Tools
        elif tool_name == "skill_gap_analyzer":
            return tool.execute(
                resume_skills=self.context.get("resume", {}).get("skills", []),
                job_requirements=params.get("job_requirements", []),
                job_title=params.get("job_title", "")
            )
        
        elif tool_name == "match_jobs":
            return tool.execute(
                resume=self.context.get("resume", {}),
                jobs=params.get("jobs", [])
            )
        
        # GitHub Scraper
        elif tool_name == "github_scraper":
            username = params.get("github_username") or self.context.get("github_username", "")
            if hasattr(tool, 'scrape_profile'):
                return tool.scrape_profile(username=username)
            elif hasattr(tool, 'execute'):
                return tool.execute(username=username)
            # Fallback to function
            from tools.profile_scrapers import scrape_github
            return scrape_github(username)
        
        # File Operations
        elif tool_name == "write_file":
            return tool.execute(
                path=params.get("filename", "output.txt"),
                content=params.get("content", "")
            )
        
        elif tool_name == "read_file":
            return tool.execute(path=params.get("filename", ""))
        
        # Generic fallback
        else:
            if hasattr(tool, "execute"):
                # Try to call execute with available params
                try:
                    return tool.execute(**params)
                except TypeError:
                    # If params don't match, try without params
                    return tool.execute()
            return {"error": f"Tool {tool_name} execution not implemented"}
    
    def _format_results(self, intent: ToolIntent, results: List[Dict]) -> str:
        """Format tool results into natural language."""
        output_parts = [intent.natural_response]
        
        for res in results:
            tool_name = res.get("tool", "")
            result = res.get("result", {})
            error = res.get("error")
            
            if error:
                output_parts.append(f"\n⚠️ {tool_name}: {error}")
                continue
            
            # Format based on tool type
            output_parts.append(self._format_tool_result(tool_name, result))
        
        return "\n".join(filter(None, output_parts))
    
    def _format_tool_result(self, tool_name: str, result: Any) -> str:
        """Format a single tool's result."""
        if not result:
            return ""
        
        if isinstance(result, str):
            return f"\n{result}"
        
        if not isinstance(result, dict):
            return f"\n{str(result)}"
        
        # Interview Prep formatting
        if tool_name == "project_deep_dive":
            projects = result.get("projects", [])
            if not projects:
                return "\n❌ No projects found."
            
            lines = [f"\n\n📊 **Analyzed {len(projects)} projects:**"]
            for proj in projects[:3]:
                lines.append(f"\n### {proj.get('name')} ({proj.get('main_language', '?')})")
                lines.append(f"⭐ {proj.get('stars', 0)} stars | Tech: {', '.join(proj.get('tech_stack', [])[:4])}")
                
                questions = proj.get("potential_questions", [])[:3]
                if questions:
                    lines.append("\n**Interview Questions:**")
                    for i, q in enumerate(questions, 1):
                        q_text = q.get('q', q) if isinstance(q, dict) else str(q)
                        lines.append(f"{i}. {q_text}")
            return "\n".join(lines)
        
        elif tool_name == "technical_q_generator":
            questions = result.get("questions", [])
            if not questions:
                return ""
            lines = ["\n\n💻 **Technical Questions:**"]
            for i, q in enumerate(questions[:5], 1):
                lines.append(f"{i}. {q.get('question', q)}")
            return "\n".join(lines)
        
        elif tool_name == "behavioral_answer_bank":
            answer = result.get("formatted", result.get("answer", ""))
            return f"\n\n📝 **STAR Answer:**\n{answer}"
        
        elif tool_name == "search_jobs":
            jobs = result if isinstance(result, list) else result.get("jobs", [])
            if not jobs:
                return "\n❌ No jobs found matching your criteria."
            lines = [f"\n\n💼 **Found {len(jobs)} jobs:**"]
            for job in jobs[:5]:
                lines.append(f"\n• **{job.get('title', 'Unknown')}** at {job.get('company', 'Unknown')}")
                lines.append(f"  📍 {job.get('location', 'Remote')}")
                if job.get('url'):
                    lines.append(f"  🔗 {job.get('url', '')[:50]}...")
            return "\n".join(lines)
        
        elif tool_name == "cover_letter_generator":
            letter = result.get("cover_letter", "")
            return f"\n\n✉️ **Cover Letter:**\n\n{letter}"
        
        elif tool_name == "ats_scorer":
            score = result.get("score", 0)
            grade = result.get("grade", "?")
            lines = [f"\n\n📊 **ATS Score: {score}/100 ({grade})**"]
            if result.get("matched_keywords"):
                lines.append(f"✅ Matched: {', '.join(result['matched_keywords'][:5])}")
            if result.get("missing_keywords"):
                lines.append(f"❌ Missing: {', '.join(result['missing_keywords'][:5])}")
            if result.get("recommendations"):
                lines.append("\n💡 **Recommendations:**")
                for rec in result["recommendations"][:3]:
                    lines.append(f"• {rec}")
            return "\n".join(lines)
        
        elif tool_name == "cold_email_sequencer":
            emails = result.get("emails", [])
            if not emails:
                return ""
            lines = ["\n\n📬 **Email Sequence:**"]
            for email in emails[:3]:
                lines.append(f"\n**{email.get('stage', 'Email')}**")
                lines.append(f"Subject: {email.get('subject', '')}")
                lines.append(f"```\n{email.get('body', '')[:300]}...\n```")
            return "\n".join(lines)
        
        elif tool_name == "company_question_generator":
            questions = result.get("recommended_questions", [])
            if not questions:
                return ""
            lines = ["\n\n💡 **Questions to Ask:**"]
            for i, q in enumerate(questions[:5], 1):
                lines.append(f"{i}. {q}")
            return "\n".join(lines)
        
        elif tool_name == "skill_gap_analyzer":
            lines = [f"\n\n📚 **Skill Analysis:**"]
            lines.append(f"Match Rate: {result.get('match_rate', 0)}%")
            if result.get("skill_gaps"):
                lines.append(f"❌ Gaps: {', '.join(result['skill_gaps'][:5])}")
            if result.get("summary"):
                lines.append(f"\n{result['summary']}")
            return "\n".join(lines)
        
        elif tool_name == "follow_up_reminder":
            if result.get("due_today"):
                lines = [f"\n\n⏰ **Follow-ups Due Today:**"]
                for item in result["due_today"]:
                    lines.append(f"• {item.get('company')} - {item.get('job_title')}")
                return "\n".join(lines)
            elif result.get("message"):
                return f"\n\n✅ {result['message']}"
            elif result.get("pending"):
                return f"\n\n📋 You have {result.get('total_pending', 0)} pending follow-ups."
            return ""
        
        # Generic formatting
        elif result.get("success"):
            if result.get("message"):
                return f"\n\n✅ {result['message']}"
            return "\n\n✅ Done!"
        else:
            return f"\n\n{json.dumps(result, indent=2)[:500]}"
    
    def set_context(self, key: str, value: Any):
        """Set context for the conversation."""
        self.context[key] = value
        self.router.conversation_context[key] = value
    
    def get_context(self, key: str) -> Any:
        """Get context value."""
        return self.context.get(key)
    
    def clear_context(self):
        """Clear conversation context."""
        self.context = {}
        self.router.conversation_context = {}


# Convenience functions
def create_cyno_agent() -> CynoAgent:
    """Create and return a CYNO agent instance."""
    return CynoAgent()


def quick_chat(message: str) -> str:
    """Quick one-off chat without maintaining state."""
    agent = CynoAgent()
    return agent.chat(message)
