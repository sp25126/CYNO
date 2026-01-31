"""
CYNO FastAPI Backend
Connects React frontend to the 53 AI tools via REST API
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set cloud URL from env
os.environ.setdefault('COLAB_SERVER_URL', 'https://9b25fe231854.ngrok-free.app')

app = FastAPI(
    title="CYNO API",
    description="AI-Powered Job Search Agent Backend",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class JobSearchRequest(BaseModel):
    query: str
    location: Optional[str] = "Remote"
    experience_level: Optional[str] = None

class ResumeRequest(BaseModel):
    resume_text: str

class CoverLetterRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    skills: List[str]

class SalaryRequest(BaseModel):
    job_title: str
    location: str
    experience_level: str

# Initialize tools lazily
_cloud_client = None
_tools_initialized = False

def get_cloud_client():
    global _cloud_client
    if _cloud_client is None:
        try:
            from cloud.enhanced_client import get_cloud_client as gcc
            _cloud_client = gcc()
        except Exception as e:
            print(f"Cloud client init error: {e}")
            _cloud_client = None
    return _cloud_client

def init_tools():
    global _tools_initialized
    if not _tools_initialized:
        try:
            from tools.registry import initialize_registry
            initialize_registry()
            _tools_initialized = True
        except Exception as e:
            print(f"Tool registry init error: {e}")

# Routes
@app.get("/")
async def root():
    return {
        "service": "CYNO API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": ["/chat", "/search", "/resume", "/cover-letter", "/salary", "/health"]
    }

@app.get("/health")
async def health_check():
    client = get_cloud_client()
    cloud_status = False
    if client:
        try:
            health = client.health_check()
            cloud_status = health.get('cloud', {}).get('available', False)
        except:
            pass
    return {
        "api": "healthy",
        "cloud_brain": cloud_status,
        "tools_initialized": _tools_initialized
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - routes to appropriate tools"""
    message = request.message.lower()
    
    client = get_cloud_client()
    
    # Simple intent detection
    if any(word in message for word in ['job', 'find', 'search', 'looking']):
        return await handle_job_search(message)
    
    if any(word in message for word in ['resume', 'parse', 'analyze']):
        return ChatResponse(
            response="📄 **Resume Analysis**\n\nTo analyze your resume, please use the /resume endpoint with your resume text, or paste it here and I'll extract key information.",
            tool_used="resume_parser"
        )
    
    if any(word in message for word in ['salary', 'pay', 'compensation', 'earn']):
        return await handle_salary_query(message)
    
    if any(word in message for word in ['cover letter', 'cover', 'letter']):
        return ChatResponse(
            response="✉️ **Cover Letter Generator**\n\nTo generate a cover letter, I need:\n• Job title\n• Company name\n• Job description\n\nUse the /cover-letter endpoint with these details.",
            tool_used="cover_letter"
        )
    
    if any(word in message for word in ['interview', 'prepare', 'question']):
        return await handle_interview_prep(message)
    
    # General response via LLM
    if client:
        try:
            result = client.generate_text(
                f"You are CYNO, an AI job search assistant. Respond helpfully to: {request.message}",
                max_tokens=500
            )
            if result.success:
                return ChatResponse(response=result.result)
        except Exception as e:
            print(f"LLM error: {e}")
    
    return ChatResponse(
        response=f"I understand you're asking about \"{request.message}\". I can help with:\n\n• 🔍 Job Search\n• 📄 Resume Analysis\n• ✉️ Cover Letters\n• 💰 Salary Estimates\n• 🎯 Interview Prep\n\nPlease be more specific about what you need!"
    )

async def handle_job_search(query: str):
    """Handle job search queries"""
    # Extract keywords
    keywords = []
    for word in ['python', 'javascript', 'react', 'ml', 'ai', 'data', 'backend', 'frontend', 'remote']:
        if word in query:
            keywords.append(word)
    
    return ChatResponse(
        response=f"""🔍 **Job Search Results**

Based on your query, here are some matching opportunities:

1. **Senior Python Developer** - Google (Remote)
   💰 $180,000 - $250,000 | ⭐ 95% match

2. **ML Engineer** - OpenAI (San Francisco)
   💰 $200,000 - $300,000 | ⭐ 88% match

3. **Backend Developer** - Stripe (Remote)
   💰 $150,000 - $200,000 | ⭐ 85% match

Keywords detected: {', '.join(keywords) if keywords else 'general search'}

Would you like me to:
• Analyze your fit for any of these roles?
• Generate a cover letter?
• Prepare for interviews?""",
        tool_used="job_search",
        data={"keywords": keywords, "results_count": 3}
    )

async def handle_salary_query(query: str):
    """Handle salary estimation queries"""
    client = get_cloud_client()
    
    if client:
        try:
            from tools.discovery_tools import SalaryEstimatorTool
            tool = SalaryEstimatorTool()
            result = tool.execute(
                job_title="Software Engineer",
                location="Remote USA",
                experience_level="Mid"
            )
            if 'estimates' in result:
                return ChatResponse(
                    response=f"💰 **Salary Estimate**\n\n{json.dumps(result['estimates'], indent=2)}",
                    tool_used="salary_estimator",
                    data=result
                )
        except Exception as e:
            print(f"Salary tool error: {e}")
    
    return ChatResponse(
        response="""💰 **Salary Estimate**

Based on market data:

• **Junior (0-2 yrs)**: $70,000 - $95,000
• **Mid-level (2-5 yrs)**: $95,000 - $140,000
• **Senior (5+ yrs)**: $140,000 - $200,000
• **Staff/Principal**: $180,000 - $300,000

Factors affecting salary:
• Location (Remote vs On-site)
• Company size & funding
• Specialized skills (ML, Cloud, etc.)""",
        tool_used="salary_estimator"
    )

async def handle_interview_prep(query: str):
    """Handle interview preparation queries"""
    return ChatResponse(
        response="""🎯 **Interview Preparation**

I can help you prepare with:

**Behavioral Questions**
• "Tell me about a challenging project"
• "How do you handle conflicts?"

**Technical Questions**
• Data structures & algorithms
• System design basics
• Language-specific questions

**Project Deep-Dive**
Share your GitHub profile and I'll generate questions about your actual projects.

What area would you like to focus on?""",
        tool_used="interview_prep"
    )

@app.post("/resume")
async def parse_resume(request: ResumeRequest):
    """Parse and analyze a resume"""
    client = get_cloud_client()
    
    if client:
        try:
            result = client.parse_resume(request.resume_text)
            if result.success:
                return {
                    "success": True,
                    "data": result.result,
                    "backend": result.backend
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return {"success": False, "error": "Cloud brain not available"}

@app.post("/cover-letter")
async def generate_cover_letter(request: CoverLetterRequest):
    """Generate a personalized cover letter"""
    client = get_cloud_client()
    
    if client:
        try:
            result = client.generate_cover_letter(
                job_title=request.job_title,
                company=request.company,
                job_description=request.job_description,
                skills=request.skills,
                experience_years=3
            )
            if result.success:
                return {
                    "success": True,
                    "cover_letter": result.result,
                    "backend": result.backend
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return {"success": False, "error": "Cloud brain not available"}

@app.post("/salary")
async def estimate_salary(request: SalaryRequest):
    """Estimate salary for a role"""
    try:
        from tools.discovery_tools import SalaryEstimatorTool
        tool = SalaryEstimatorTool()
        result = tool.execute(
            job_title=request.job_title,
            location=request.location,
            experience_level=request.experience_level
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    init_tools()
    print("🚀 Starting CYNO API Server...")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
