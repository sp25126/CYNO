# CYNO CLOUD GPU - COLAB DEPLOYMENT (with NGROK)
# Copy this entire cell into Google Colab and run

#===============================================
# STEP 1: Install Dependencies
#===============================================
print("📦 Installing dependencies...")
!pip install -q fastapi uvicorn pydantic transformers torch accelerate bitsandbytes pyngrok nest-asyncio

#===============================================
# STEP 2: Configure Ngrok
#===============================================
# GET YOUR FREE TOKEN AT: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_TOKEN = "YOUR_NGROK_TOKEN_HERE"  # <--- REPLACE THIS

if NGROK_TOKEN == "YOUR_NGROK_TOKEN_HERE":
    raise ValueError("❌ You must replace YOUR_NGROK_TOKEN_HERE with your actual token from https://dashboard.ngrok.com")

import nest_asyncio
from pyngrok import ngrok, conf

# Apply nest_asyncio to allow nested event loops in Colab
nest_asyncio.apply()

# Authenticate
print("🔐 Authenticating with ngrok...")
conf.get_default().auth_token = NGROK_TOKEN

# Kill existing tunnels
ngrok.kill()

#===============================================
# STEP 3: Load Model (FREE UNGATED MODELS)
#===============================================
print("🧠 Loading AI model (this takes 2-3 minutes)...")

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
import json
import time
from typing import Dict, Any

# Try models in order of preference (STABLE & FAST)
models_to_try = [
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # 1.1B params, SUPER FAST (<2s), Stable
    "mistralai/Mistral-7B-Instruct-v0.3",  # 7B params, high quality
]

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

model = None
tokenizer = None
model_id = None

for candidate_model in models_to_try:
    try:
        print(f"⏳ Trying {candidate_model}...")
        tokenizer = AutoTokenizer.from_pretrained(candidate_model, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            candidate_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        model_id = candidate_model
        print(f"✅ Model loaded: {model_id}")
        break
    except Exception as e:
        print(f"⚠️ {candidate_model} failed: {str(e)[:100]}")
        continue

if model is None:
    raise RuntimeError("❌ All models failed to load. Check your internet connection.")

#===============================================
# STEP 4: Define Resume Parser Logic
#===============================================
def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """Extract structured data from resume using LLM"""
    
    prompt = f"""You are an expert resume analyzer. Extract detailed information and return ONLY valid JSON with these exact keys:

{{
  "projects": ["list of notable projects with tech used"],
  "certifications": ["list of certifications/credentials"],
  "achievements": ["key accomplishments with metrics if available"],
  "soft_skills": ["leadership, communication, teamwork, etc."],
  "languages": ["English", "Spanish", etc.],
  "domains": ["AI/ML, Web Development, Cloud, DevOps, etc."],
  "work_experience": [
    {{
      "role": "job title",
      "company": "company name",
      "duration": "timeframe",
      "key_tech": ["main technologies used"]
    }}
  ],
  "profile_type": "AI_ML_ENGINEER or WEB_DEVELOPER or FULLSTACK_ENGINEER or DATA_SCIENTIST or DEVOPS_ENGINEER or SOFTWARE_ENGINEER or GENERAL"
}}

CRITICAL: Return pure JSON only, no markdown.

Resume Text:
{resume_text[:3000]}

JSON:"""
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=800,
            temperature=0.1,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    
    # Parse JSON (Robust)
    try:
        content = response.strip()
        
        # 1. Strip markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        # 2. TinyLlama Fix: Remove anything after the last }
        if "}" in content:
            last_brace = content.rindex("}")
            content = content[:last_brace+1]
        
        parsed = json.loads(content.strip())
        
        return {
            'projects': parsed.get('projects', [])[:5],
            'certifications': parsed.get('certifications', [])[:5],
            'achievements': parsed.get('achievements', [])[:5],
            'soft_skills': parsed.get('soft_skills', [])[:5],
            'languages': parsed.get('languages', [])[:3],
            'domains': parsed.get('domains', [])[:10],
            'work_experience': parsed.get('work_experience', [])[:5],
            'profile_type': parsed.get('profile_type', 'GENERAL')
        }
    
    except Exception as e:
        print(f"JSON parse error: {e}")
        return {
            'projects': [],
            'certifications': [],
            'achievements': [],
            'soft_skills': [],
            'languages': [],
            'domains': [],
            'work_experience': [],
            'profile_type': 'GENERAL'
        }

#===============================================
# STEP 5: Create FastAPI Server
#===============================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Cyno AI Server", version="3.0-ngrok")

class ParseRequest(BaseModel):
    resume_text: str

class ParseResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_seconds: float

class EmailDraftRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    resume_skills: list
    resume_experience: int

class EmailDraftResponse(BaseModel):
    success: bool
    subject: Optional[str] = None
    body: Optional[str] = None
    error: Optional[str] = None
    processing_time_seconds: float

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Cyno AI Server (Ngrok)",
        "status": "online",
        "model_loaded": model is not None,
        "gpu_available": "cuda" in str(model.device) if model else False,
        "endpoints": ["/parse_resume", "/draft_email"]
    }

@app.post("/parse_resume", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """Parse resume and extract structured data"""
    start_time = time.time()
    try:
        if not request.resume_text or len(request.resume_text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Resume text too short")
        data = extract_resume_data(request.resume_text)
        return ParseResponse(success=True, data=data, processing_time_seconds=time.time() - start_time)
    except Exception as e:
        return ParseResponse(success=False, error=str(e), processing_time_seconds=time.time() - start_time)

@app.post("/draft_email", response_model=EmailDraftResponse)
async def draft_email(request: EmailDraftRequest):
    """Generate a professional cold email for job application"""
    start_time = time.time()
    try:
        skills_str = ', '.join(request.resume_skills[:5])
        prompt = f"""You are an expert career coach. Write a concise, professional cold email for a job application.

JOB DETAILS:
Title: {request.job_title}
Company: {request.company}
Description: {request.job_description[:300]}...

CANDIDATE DETAILS:
Skills: {skills_str}
Experience: {request.resume_experience} years

INSTRUCTIONS:
- Write a concise email (max 150 words)
- Highlight 2-3 matching skills
- Show enthusiasm for {request.company}
- NO placeholders like [Your Name]
- Subject line: specific and catchy

OUTPUT FORMAT:
Subject: <subject line>

<email body>

Generate the email now:"""

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs, max_new_tokens=300, temperature=0.3, do_sample=True, top_p=0.9, pad_token_id=tokenizer.eos_token_id
            )
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        lines = response.split('\n')
        subject = f"Application for {request.job_title}"
        body_start = 0
        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body_start = i + 1
                break
        body = "\n".join(lines[body_start:]).strip()
        if len(body) > 500: body = body[:500] + "..."
        
        return EmailDraftResponse(success=True, subject=subject, body=body, processing_time_seconds=time.time() - start_time)
    except Exception as e:
        return EmailDraftResponse(success=False, error=str(e), processing_time_seconds=time.time() - start_time)

#===============================================
# STEP 6: Start Server with Ngrok Tunnel
#===============================================
import uvicorn
from threading import Thread

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

# Start FastAPI in background
server_thread = Thread(target=run_server, daemon=True)
server_thread.start()

print("⏳ Waiting for server to start...")
time.sleep(3)

# Create ngrok tunnel
print("🌐 Opening ngrok tunnel...")
public_url = ngrok.connect(8000).public_url

print("\n" + "="*60)
print("✅ NGROK SERVER READY")
print("="*60)
print(f"🌐 Public URL: {public_url}")
print("📝 COPY THIS URL AND SAVE IT")
print("="*60)
print("\nThis ngrok URL is persistent for this session!")
print("\n⚠️ IMPORTANT: Keep this cell running. Do NOT stop it.")
print("="*60)

# Keep alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\nShutting down...")
    ngrok.kill()
