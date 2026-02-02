"""
CYNO FastAPI Backend
Connects React frontend to the 53 AI tools via REST API
Enhanced with professional personality engine
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

# Import personality engine
try:
    from agent.personality import (
        CYNO_SYSTEM_PROMPT,
        format_professional_response,
        analyze_resume_insights,
        get_professional_intro
    )
except ImportError:
    CYNO_SYSTEM_PROMPT = "You are CYNO, a professional AI career advisor."
    format_professional_response = None

app = FastAPI(
    title="CYNO API",
    description="AI-Powered Job Search Agent Backend",
    version="2.0.0"
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
    resume_text: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    tool_used: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    insights: Optional[Dict[str, Any]] = None

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

# User context storage (in-memory for prototype)
user_contexts = {}

# Initialize tools lazily
_cloud_client = None

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

# Routes
@app.get("/")
async def root():
    return {
        "service": "CYNO API",
        "version": "2.0.0",
        "personality": "Senior Career Strategist",
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
        "personality": "active"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with professional CYNO personality"""
    message = request.message.strip()
    message_lower = message.lower()
    
    client = get_cloud_client()
    
    # Check if user is sharing a resume
    if request.resume_text or is_resume_text(message):
        return await handle_resume_analysis(request.resume_text or message, client)
    
    # Intent detection with professional responses
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'start', 'help']):
        if format_professional_response:
            return ChatResponse(
                response=format_professional_response("welcome"),
                tool_used="personality"
            )
    
    if any(word in message_lower for word in ['job', 'find', 'search', 'looking', 'opportunity']):
        return await handle_job_search_professional(message, client)
    
    if any(word in message_lower for word in ['resume', 'cv', 'analyze my']):
        return ChatResponse(
            response="""I'd be happy to analyze your resume and provide strategic insights.

Please share your resume text, and I'll give you:
• A clear picture of your **core strengths**
• Insights into your **career trajectory**
• **Actionable recommendations** for improvement
• Opportunities that align with your background

Simply paste your resume content, and let's take a look together.""",
            tool_used="resume_parser"
        )
    
    if any(word in message_lower for word in ['salary', 'pay', 'compensation', 'worth', 'earn']):
        return await handle_salary_professional(message, client)
    
    if any(word in message_lower for word in ['cover letter', 'application letter']):
        if format_professional_response:
            return ChatResponse(
                response=format_professional_response("cover_letter"),
                tool_used="cover_letter"
            )
    
    if any(word in message_lower for word in ['interview', 'prepare', 'question']):
        if format_professional_response:
            return ChatResponse(
                response=format_professional_response("interview_prep"),
                tool_used="interview_prep"
            )
    
    # Use LLM with CYNO personality for general queries
    if client:
        try:
            prompt = f"""{CYNO_SYSTEM_PROMPT}

User message: {message}

Respond as CYNO, providing helpful, professional career guidance. Be specific, insightful, and action-oriented."""
            
            result = client.generate_text(prompt, max_tokens=600, temperature=0.7)
            if result.success:
                return ChatResponse(
                    response=result.result,
                    tool_used="llm_brain"
                )
        except Exception as e:
            print(f"LLM error: {e}")
    
    # Professional fallback
    return ChatResponse(
        response="""I appreciate you reaching out. To give you the most relevant guidance, could you tell me more about what you're looking to accomplish?

I'm here to help with:
• **Career Strategy** — Understanding your goals and mapping a path forward
• **Resume Analysis** — Identifying your strengths and how to present them
• **Job Search** — Finding opportunities that truly fit your profile
• **Interview Preparation** — Walking in confident and prepared
• **Salary Negotiation** — Understanding your market value

What's top of mind for you right now?"""
    )

def is_resume_text(text: str) -> bool:
    """Detect if the message appears to be resume content"""
    resume_indicators = [
        'experience', 'education', 'skills', 'work history',
        'objective', 'summary', 'professional', 'bachelor',
        'master', 'university', 'responsibilities', 'achievements',
        'python', 'javascript', 'developer', 'engineer', 'manager',
        'years of experience', 'proficient in', 'expertise in'
    ]
    text_lower = text.lower()
    matches = sum(1 for indicator in resume_indicators if indicator in text_lower)
    # If 4+ indicators and text is substantial, likely a resume
    return matches >= 4 and len(text) > 300

async def handle_resume_analysis(resume_text: str, client):
    """Analyze resume with professional insights"""
    parsed_data = None
    
    if client:
        try:
            result = client.parse_resume(resume_text)
            if result.success:
                parsed_data = result.result
        except Exception as e:
            print(f"Resume parse error: {e}")
    
    # Generate insights
    if format_professional_response:
        from agent.personality import analyze_resume_insights
        insights = analyze_resume_insights(parsed_data)
    else:
        insights = {}
    
    # Extract key info for personalized response
    skills = parsed_data.get("skills", []) if parsed_data else []
    experience = parsed_data.get("total_experience_years", 0) if parsed_data else 0
    
    # Build personalized response
    if skills:
        top_skills = skills[:3]
        skill_analysis = f"**{', '.join(top_skills)}**"
    else:
        skill_analysis = "**technical problem-solving and project delivery**"
    
    response = f"""I've carefully reviewed your background, and I can see you have a compelling professional story.

**What stands out to me:**
Based on your experience, you excel at {skill_analysis}. This combination is particularly valuable in today's market.

**Your career trajectory:**
{insights.get('career_pattern', "You're at an interesting point in your career where strategic moves can have significant impact.")}

**Key observations:**
• Your technical foundation is solid—this opens doors to multiple paths
• I notice patterns that suggest you thrive in environments that challenge you
• There's an opportunity to better highlight your unique value proposition

**My recommendations:**
1. Quantify your achievements—numbers make impact tangible
2. Lead with your differentiators, not just your responsibilities
3. Consider how your projects tell a story of growth

Would you like me to:
• Find job opportunities that match your strengths?
• Help you craft a more compelling resume narrative?
• Prepare you for interviews at specific companies?"""

    return ChatResponse(
        response=response,
        tool_used="resume_analyzer",
        data=parsed_data,
        insights=insights
    )

async def handle_job_search_professional(query: str, client):
    """Handle job search with professional insights"""
    
    response = """I'd be happy to help you find the right opportunities. But first, let me understand what you're really looking for.

**A few strategic questions:**
1. What type of work genuinely energizes you?
2. Are you looking for growth, stability, compensation, or work-life balance?
3. Any specific companies or industries you're drawn to?

**Based on current market trends:**
The job market is dynamic right now. Roles in **Python development**, **ML/AI**, and **cloud infrastructure** are seeing particularly strong demand. Remote opportunities remain robust, though some companies are increasing on-site expectations.

**My approach:**
Rather than overwhelming you with listings, I prefer to identify 3-5 opportunities that genuinely align with your goals and have a realistic path to success.

Tell me a bit more about what you're looking for—or share your resume and I'll suggest roles that match your actual strengths."""

    return ChatResponse(
        response=response,
        tool_used="job_search",
        data={"status": "gathering_context"}
    )

async def handle_salary_professional(query: str, client):
    """Handle salary queries with professional insights"""
    
    if format_professional_response:
        response = format_professional_response("salary_query", {"role": "Software Engineer", "location": "the US market"})
    else:
        response = """Let me give you the real picture on compensation.

**Market Reality:**
Salaries vary significantly based on company stage, location, and your specific skill stack. Here's what I'm seeing:

• **Entry Level (0-2 yrs)**: $70,000 - $95,000
• **Mid-Senior (3-7 yrs)**: $110,000 - $160,000
• **Senior/Lead (7+ yrs)**: $150,000 - $220,000
• **Staff/Principal**: $200,000 - $350,000+

**Key factors that move the needle:**
• Big Tech vs. Startups (significant difference)
• Specialized skills (ML, Cloud, Security)
• Negotiation strategy and timing

Would you like me to help you understand where you specifically should be targeting?"""

    return ChatResponse(
        response=response,
        tool_used="salary_advisor"
    )

@app.post("/resume")
async def parse_resume(request: ResumeRequest):
    """Parse and analyze a resume with professional insights"""
    client = get_cloud_client()
    
    if client:
        try:
            result = client.parse_resume(request.resume_text)
            if result.success:
                # Add professional insights
                if format_professional_response:
                    from agent.personality import analyze_resume_insights
                    insights = analyze_resume_insights(result.result)
                else:
                    insights = {}
                
                return {
                    "success": True,
                    "data": result.result,
                    "insights": insights,
                    "backend": result.backend
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return {"success": False, "error": "Cloud brain not available"}

@app.post("/cover-letter")
async def generate_cover_letter(request: CoverLetterRequest):
    """Generate a personalized cover letter"""
    client = get_cloud_client()
    
    prompt = f"""{CYNO_SYSTEM_PROMPT}

Generate a compelling cover letter for:
- Position: {request.job_title}
- Company: {request.company}
- Key Skills: {', '.join(request.skills)}
- Job Description: {request.job_description}

Write a professional, engaging cover letter that:
1. Opens with a hook that shows genuine interest
2. Connects specific skills to the role requirements
3. Demonstrates understanding of the company
4. Closes with a confident call to action

Keep it concise (3-4 paragraphs) and authentic."""
    
    if client:
        try:
            result = client.generate_text(prompt, max_tokens=800, temperature=0.7)
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
    """Estimate salary with professional insights"""
    try:
        from tools.discovery_tools import SalaryEstimatorTool
        tool = SalaryEstimatorTool()
        result = tool.execute(
            job_title=request.job_title,
            location=request.location,
            experience_level=request.experience_level
        )
        
        # Add professional context
        result["advice"] = f"""Based on current market data for {request.job_title} roles in {request.location}, 
here's my analysis. Remember, these ranges are starting points for negotiation—your specific background 
and the company's situation can significantly impact the final offer."""
        
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CYNO API Server v2.0...")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    print("🎭 Personality: Senior Career Strategist")
    uvicorn.run(app, host="0.0.0.0", port=8000)
