# CYNO CLOUD GPU - COLAB DEPLOYMENT (with zrok)
# Copy this entire cell into Google Colab and run

#===============================================
# STEP 1: Install Dependencies
#===============================================
print("📦 Installing dependencies...")
!pip install -q fastapi uvicorn pydantic transformers torch accelerate bitsandbytes

#===============================================
# STEP 2: Install and Setup zrok (LATEST VERSION)
#===============================================
print("🔧 Setting up zrok...")

# Download zrok (v0.4.23 - Stable for Colab)
import requests
import os

print("⬇️ Downloading zrok v0.4.23 (Stable)...")
try:
    download_url = "https://github.com/openziti/zrok/releases/download/v0.4.23/zrok_0.4.23_linux_amd64.tar.gz"
    !wget -q {download_url} -O zrok.tar.gz
    !tar -xzf zrok.tar.gz
    
    # Move binary to path
    !mv zrok /usr/local/bin/
    !chmod +x /usr/local/bin/zrok
        
except Exception as e:
    print(f"❌ Error setting up zrok: {e}")
    raise

# YOU NEED TO GET YOUR FREE ZROK TOKEN
# 1. Go to: https://api.zrok.io/
# 2. Create a free account
# 3. Copy your token from the dashboard
# 4. Paste it below (replace YOUR_ZROK_TOKEN_HERE)

ZROK_TOKEN = "lJdPQnOaVojF"  # Your zrok token

if ZROK_TOKEN == "YOUR_ZROK_TOKEN_HERE":
    raise ValueError("❌ ERROR: You must replace ZROK_TOKEN with your actual token from https://api.zrok.io/")

# Initialize zrok
import subprocess

# Force disable first to clean up any previous session
print("🔄 Cleaning up any existing zrok session...")
disable_result = subprocess.run(["zrok", "disable"], capture_output=True, text=True)
print(f"Disable result: {disable_result.stdout if disable_result.stdout else 'No output'}")

print(f"🔐 Enabling zrok with token...")
result = subprocess.run(["zrok", "enable", ZROK_TOKEN], capture_output=True, text=True)

if result.returncode != 0:
    print(f"❌ zrok enable failed!")
    print(f"Return code: {result.returncode}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    
    # Check if it's already enabled
    status_result = subprocess.run(["zrok", "status"], capture_output=True, text=True)
    if "enabled" in status_result.stdout.lower():
        print("✅ zrok is already enabled! Continuing...")
    else:
        raise RuntimeError(f"Failed to enable zrok. Error: {result.stderr or 'No error message'}")
else:
    print("✅ zrok configured!")

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
    "microsoft/Phi-3-mini-4k-instruct"     # 3.8B params (bleeding edge)
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
        # Debug: Print content that failed
        print(f"FAILED CONTENT: {content[:200]}...")
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

app = FastAPI(title="Cyno AI Server", version="3.0-cloud")

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
        "service": "Cyno AI Server",
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
        
        return ParseResponse(
            success=True,
            data=data,
            processing_time_seconds=time.time() - start_time
        )
    
    except Exception as e:
        return ParseResponse(
            success=False,
            error=str(e),
            processing_time_seconds=time.time() - start_time
        )

@app.post("/draft_email", response_model=EmailDraftResponse)
async def draft_email(request: EmailDraftRequest):
    """Generate a professional cold email for job application"""
    start_time = time.time()
    
    try:
        # Craft prompt for email generation
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
                **inputs,
                max_new_tokens=300,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        # Parse subject and body
        lines = response.split('\n')
        subject = f"Application for {request.job_title}"
        body_start = 0
        
        for i, line in enumerate(lines):
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body_start = i + 1
                break
        
        body = "\n".join(lines[body_start:]).strip()
        
        # Clean up body (remove any trailing instructions/artifacts)
        if len(body) > 500:
            body = body[:500] + "..."
        
        return EmailDraftResponse(
            success=True,
            subject=subject,
            body=body,
            processing_time_seconds=time.time() - start_time
        )
    
    except Exception as e:
        return EmailDraftResponse(
            success=False,
            error=str(e),
            processing_time_seconds=time.time() - start_time
        )

#===============================================
# STEP 6: Start Server with zrok Tunnel
#===============================================
import uvicorn
from threading import Thread
import subprocess
import re

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

# Start FastAPI in background
server_thread = Thread(target=run_server, daemon=True)
server_thread.start()

print("⏳ Waiting for server to start...")
time.sleep(3)

# Create zrok share (persistent public URL)
print("🌐 Creating public zrok URL...")
zrok_process = subprocess.Popen(
    ["zrok", "share", "public", "localhost:8000", "--headless"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

# Parse the zrok URL from output
public_url = None
for line in zrok_process.stdout:
    print(line.strip())
    if "https://" in line:
        match = re.search(r'(https://[^\s]+)', line)
        if match:
            public_url = match.group(1)
            break

print("\n" + "="*60)
print("✅ SERVER READY")
print("="*60)
print(f"🌐 Public URL: {public_url}")
print("📝 COPY THIS URL AND SAVE IT")
print("="*60)
print("\nThis zrok URL is persistent and won't change on restart!")
print("Server will run until Colab disconnects (~12 hours)")
print("\n⚠️ IMPORTANT: Keep this cell running. Do NOT stop it.")
print("="*60)

# Keep alive
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("\nShutting down...")
    zrok_process.terminate()
