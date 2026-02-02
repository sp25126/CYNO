"""
CYNO UNIFIED API (v3.0)
The "Ferrari Engine" Backend.
Integrates 50+ tools, Shared CLI State, and Advanced Personality.
"""
import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === CORE INTEGRATIONS ===
from cli.state import state as global_state  # Shared Memory
from tools.lead_scraper import LeadScraperTool
from tools.smart_email import SmartEmailEngine, EmailDraft
from tools.interview_prep import ProjectDeepDiveTool, BehavioralAnswerBankTool, SystemDesignSimulatorTool
from tools.job_search import JobSearchTool
from tools.discovery_tools import SalaryEstimatorTool
from tools.application_tools import CoverLetterGeneratorTool, ATSScorerTool
from cloud.enhanced_client import get_cloud_client

# Personality
try:
    from agent.personality import (
        CYNO_SYSTEM_PROMPT,
        format_professional_response,
        analyze_resume_insights
    )
except ImportError:
    CYNO_SYSTEM_PROMPT = "You are CYNO, a professional AI career advisor."
    format_professional_response = None
    analyze_resume_insights = None

app = FastAPI(
    title="CYNO Unified API",
    description="The Real Engine. 50+ Tools. Shared State.",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================
# UNIFIED STATE ENDPOINTS
# ==========================

@app.get("/state")
async def get_state():
    """Get the current shared state (resume, preferences)"""
    resume = global_state.get_resume()
    return {
        "has_resume": resume is not None,
        "resume_summary": {
            "name": resume.get("name") if resume else None,
            "skills": resume.get("parsed_skills", [])[:5] if resume else [],
            "experience": resume.get("years_exp", 0) if resume else 0
        },
        "ngrok_url": global_state.state.ngrok_url
    }

# ==========================
# RESUME & APPLICATION TOOLS
# ==========================

class ResumeRequest(BaseModel):
    resume_text: str # For now, frontend sends text. TODO: File upload.

@app.post("/resume/parse")
async def parse_resume(request: ResumeRequest):
    """Parse resume and SAVE to shared state"""
    client = get_cloud_client()
    if not client:
        raise HTTPException(503, "Cloud Brain disconnected.")
    
    result = client.parse_resume(request.resume_text)
    if result.success:
        # SAVE TO GLOBAL STATE
        # We assume frontend sends the "text" derived from file or paste
        global_state.set_resume("api_upload", request.resume_text, result.result.model_dump())
        
        return {
            "success": True,
            "data": result.result.model_dump(),
            "insights": analyze_resume_insights(result.result) if analyze_resume_insights else {}
        }
    raise HTTPException(400, "Parsing failed.")

class CoverLetterRequest(BaseModel):
    job_description: str
    company: str
    role: str

@app.post("/app/cover-letter")
async def generate_cover_letter(request: CoverLetterRequest):
    """Generate cover letter using SAVED resume"""
    resume_data = global_state.get_resume()
    if not resume_data:
        raise HTTPException(400, "No resume loaded. Please upload resume first.")
    
    tool = CoverLetterGeneratorTool()
    res = tool.execute(
        role=request.role,
        company=request.company,
        job_description=request.job_description,
        user_resume=resume_data
    )
    
    if res['success']:
        return {"success": True, "letter": res['cover_letter']}
    raise HTTPException(500, res.get('error', 'Generation failed'))

@app.post("/app/score")
async def score_resume(job_description: str):
    """ATS Score using SAVED resume"""
    resume_text = global_state.get_resume_text()
    if not resume_text:
        raise HTTPException(400, "No resume loaded.")
        
    tool = ATSScorerTool()
    return tool.execute(resume_text, job_description)

# ==========================
# NETWORK & GROWTH HACKING
# ==========================

@app.get("/net/leads")
async def get_leads(query: str):
    """Growth Hacking: Find unlisted leads"""
    tool = LeadScraperTool()
    leads = tool.scrape_leads([query], limit=10)
    # Serialize leads
    return {"success": True, "leads": [l.model_dump() for l in leads]}

class EmailRequest(BaseModel):
    type: str # cold, followup, connection
    recipient: str
    company: str
    context: Optional[dict] = {}

@app.post("/net/email")
async def draft_email(req: EmailRequest):
    """Draft networking emails"""
    engine = SmartEmailEngine()
    
    if req.type == "cold":
        draft = engine.generate_cold_outreach_email(
            recipient_name=req.recipient,
            recipient_role="Hiring Manager",
            company=req.company,
            connection_reason=req.context.get("reason", "Shared interest")
        )
    elif req.type == "connection":
        draft = engine.generate_connection_request(
            recipient_name=req.recipient,
            recipient_role="Professional",
            company=req.company,
            connection_reason=req.context.get("reason", "Networking"),
            platform="LinkedIn"
        )
    else:
        raise HTTPException(400, "Unsupported email type for API")
        
    return {"success": True, "subject": draft.subject, "body": draft.body}

# ==========================
# INTERVIEW PREP
# ==========================

@app.get("/prep/github")
async def analyze_github(username: str):
    """Deep Dive into GitHub Profile"""
    tool = ProjectDeepDiveTool()
    return tool.execute(username)

@app.get("/prep/behavior")
async def get_behavioral_answer(question: str):
    """Get STAR answer"""
    tool = BehavioralAnswerBankTool()
    return tool.execute(question, {"name": "My Project"}) # Todo: Use state projects

# ==========================
# LEGACY / CHAT SUPPORT
# ==========================

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    """Simple chat endpoint that can check state"""
    msg = req.message.lower()
    
    # Check State
    resume = global_state.get_resume()
    user_name = resume['name'] if resume else "Candidate"
    
    # Basic router - In real prod, this calls an LLM Agent Loop
    if "leads" in msg:
        return {"response": "I can find leads! Try the 'Growth' tab or ask specifically 'find python leads'."}
        
    client = get_cloud_client()
    if client:
        prompt = f"System: You are CYNO. User: {user_name}. Request: {req.message}"
        res = client.generate_text(prompt)
        return {"response": res.result if res.success else "Brain offline."}
        
    return {"response": f"Hello {user_name}, I am ready. Please load a resume or start a search."}

if __name__ == "__main__":
    print("🚀 CYNO UNIFIED SERVER STARTING...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
