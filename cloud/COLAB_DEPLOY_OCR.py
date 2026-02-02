# CYNO CLOUD GPU - ENHANCED COLAB DEPLOYMENT (NGROK + OCR)
# With OCR Support + Upgraded LLM Model + Ngrok Tunneling
# Copy this entire cell into Google Colab and run

#===============================================
# STEP 1: Install Dependencies (Including OCR)
#===============================================
print("📦 Installing dependencies...")
!pip install -q fastapi uvicorn pydantic transformers torch accelerate bitsandbytes
!pip install -q pdf2image pytesseract Pillow pyngrok nest-asyncio
!apt-get install -q -y tesseract-ocr poppler-utils

#===============================================
# STEP 2: Configure Ngrok
#===============================================
# GET YOUR FREE TOKEN AT: https://dashboard.ngrok.com/get-started/your-authtoken
NGROK_TOKEN = "31yYPXhPRNGBB9mEcNpDp8YOaZK_65SMKRBe8C7UUe1V2wfMx"  # User's token

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
# STEP 3: Load Model (UPGRADED - Llama-3.2-3B)
#===============================================
print("🧠 Loading AI model (this takes 2-3 minutes)...")

from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
import json
import time
import base64
import io
from typing import Dict, Any, List
from PIL import Image

# UPGRADED MODEL LIST - Prioritize Llama-3.2-3B for better accuracy
models_to_try = [
    "unsloth/Llama-3.2-3B-Instruct",   # 3B - Best balance of speed + quality
    "meta-llama/Llama-3.2-3B-Instruct", # Official Meta (may need HF token)
    "microsoft/Phi-3-mini-4k-instruct", # 3.8B - Good fallback
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0", # 1.1B - Last resort
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
# STEP 4: OCR Functions (PDF to Clean Text)
#===============================================
from pdf2image import convert_from_bytes
import pytesseract

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Convert PDF bytes to clean text using OCR (Tesseract)"""
    try:
        # Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes, dpi=300)
        
        # OCR each page
        full_text = []
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='eng')
            full_text.append(text)
        
        return "\n\n".join(full_text)
    except Exception as e:
        print(f"OCR Error: {e}")
        raise RuntimeError(f"PDF OCR failed: {str(e)}")

def clean_extracted_text(text: str) -> str:
    """Clean OCR artifacts from extracted text"""
    import re
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove common OCR artifacts
    text = re.sub(r'\(cid:\d+\)', '', text)
    text = text.strip()
    return text

#===============================================
# STEP 5: Resume Parser Logic (SIMPLIFIED PROMPT)
#===============================================
def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """Extract structured data from resume using LLM (Simplified for Llama-3.2)"""
    
    # SIMPLIFIED PROMPT - Llama-3.2 works better with simpler structures
    prompt = f"""You are a resume parser. Extract information from the resume below and return ONLY a JSON object.

Resume:
{resume_text[:3500]}

Extract and return this JSON (fill in actual values from resume):
{{
  "name": "person's full name",
  "skills": ["skill1", "skill2", "skill3", "...all technical skills mentioned"],
  "profile_type": "choose one: AI_ML_ENGINEER, WEB_DEVELOPER, FULLSTACK_ENGINEER, DATA_SCIENTIST, DEVOPS_ENGINEER, SOFTWARE_ENGINEER, or GENERAL",
  "experience_years": number,
  "projects": ["project1", "project2"],
  "education": "highest degree and field"
}}

IMPORTANT: 
- skills list must include ALL programming languages, frameworks, and tools mentioned
- Return ONLY the JSON, no other text

JSON:"""
    
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=1500,
            temperature=0.1,
            do_sample=True,
            top_p=0.95,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    
    # Parse JSON (Robust)
    try:
        content = response.strip()
        
        # Strip markdown
        if "```json" in content:
            content = content.split("```json")[1]
        if "```" in content:
            content = content.split("```")[0]
            
        # Find JSON object
        start = content.find("{")
        end = content.rfind("}") + 1
        if start != -1 and end > start:
            content = content[start:end]
        
        parsed = json.loads(content)
        
        # Extract skills - handle both list and string
        skills = parsed.get('skills', [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(',')]
        
        # Normalize and return (simplified structure)
        return {
            'name': parsed.get('name', 'Unknown'),
            'skills': skills[:30],  # Allow more skills
            'projects': parsed.get('projects', [])[:5],
            'education': parsed.get('education', ''),
            'experience_years': parsed.get('experience_years', 0),
            'profile_type': parsed.get('profile_type', 'GENERAL').upper().replace(' ', '_')
        }
    
    except Exception as e:
        print(f"JSON parse error: {e}")
        print(f"RAW RESPONSE: {response[:800]}...")
        return {
            'name': 'Unknown',
            'skills': [],
            'projects': [],
            'education': '',
            'experience_years': 0,
            'profile_type': 'GENERAL'
        }

#===============================================
# STEP 6: Create FastAPI Server
#===============================================
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Cyno AI Server", version="4.0-ngrok-ocr")

class ParseRequest(BaseModel):
    resume_text: str

class ParsePDFRequest(BaseModel):
    pdf_base64: str  # Base64 encoded PDF bytes

class ParseResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_seconds: float
    ocr_used: bool = False

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
        "version": "4.0-ngrok-ocr",
        "status": "online",
        "model_loaded": model is not None,
        "model_name": model_id,
        "gpu_available": "cuda" in str(model.device) if model else False,
        "ocr_available": True,
        "endpoints": ["/parse_resume", "/parse_resume_pdf", "/draft_email"]
    }

@app.post("/parse_resume", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """Parse resume text and extract structured data"""
    start_time = time.time()
    
    try:
        if not request.resume_text or len(request.resume_text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Resume text too short")
        
        # Clean text if it has OCR artifacts
        clean_text = clean_extracted_text(request.resume_text)
        data = extract_resume_data(clean_text)
        
        return ParseResponse(
            success=True,
            data=data,
            processing_time_seconds=time.time() - start_time,
            ocr_used=False
        )
    
    except Exception as e:
        return ParseResponse(
            success=False,
            error=str(e),
            processing_time_seconds=time.time() - start_time
        )

@app.post("/parse_resume_pdf", response_model=ParseResponse)
async def parse_resume_pdf(request: ParsePDFRequest):
    """Parse resume from PDF (with OCR) - Heavy processing on Cloud GPU"""
    start_time = time.time()
    
    try:
        # Decode base64 PDF
        pdf_bytes = base64.b64decode(request.pdf_base64)
        
        # OCR the PDF
        print(f"📄 Processing PDF ({len(pdf_bytes)} bytes)...")
        raw_text = extract_text_from_pdf_bytes(pdf_bytes)
        clean_text = clean_extracted_text(raw_text)
        
        print(f"📝 Extracted {len(clean_text)} characters")
        
        if len(clean_text.strip()) < 100:
            raise ValueError("OCR extracted too little text. PDF may be empty or unreadable.")
        
        # Extract structured data using LLM
        data = extract_resume_data(clean_text)
        
        # Include raw text for debugging
        data['raw_extracted_text'] = clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text
        
        return ParseResponse(
            success=True,
            data=data,
            processing_time_seconds=time.time() - start_time,
            ocr_used=True
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
        skills_str = ', '.join(request.resume_skills[:5])
        
        # SIMPLIFIED PROMPT - Precise professional email
        prompt = f"""You are a career expert. Write a short, professional job application email.

JOB: {request.job_title} at {request.company}
About: {request.job_description[:300]}

ME: 
- Skills: {skills_str}
- Experience: {request.resume_experience} years

INSTRUCTIONS:
1. Subject Line: "Application for {request.job_title} - [My Name]"
2. Salutation: "Dear Hiring Team,"
3. Opening: specific interest in {request.company}
4. Middle: mention 2 specific skills from my list that fit the job
5. Closing: Request an interview
6. Sign-off: "Best regards," (no name needed)

Write ONLY the email body. Do not include placeholders like [Your Name].

EMAIL:"""

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=400,
                temperature=0.3,
                do_sample=True,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        
        # Parse subject and body (Robust)
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        subject = f"Application for {request.job_title} - Candidate"
        body_lines = []
        
        for line in lines:
            if line.lower().startswith("subject:") or line.lower().startswith("subject line:"):
                subject = line.split(":", 1)[1].strip()
            # Stop if we hit user instruction repeats (common in small models)
            elif "email:" in line.lower() or "job:" in line.lower():
                continue
            else:
                body_lines.append(line)
        
        body = "\n".join(body_lines).strip()
        
        # Clean up
        if len(body) > 1000:
            body = body[:1000]
        
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
# STEP 7: Start Server with Ngrok Tunnel
#===============================================
# For Colab + CUDA + nest_asyncio, we need to run uvicorn in the main thread

print("🚀 Starting FastAPI server...")

# Create ngrok tunnel FIRST (before blocking uvicorn)
print("🌐 Opening ngrok tunnel...")
public_url = ngrok.connect(8000).public_url

print("\n" + "="*60)
print("✅ NGROK SERVER READY (v4.0 - OCR + Llama-3.2)")
print("="*60)
print(f"🌐 Public URL: {public_url}")
print(f"🧠 Model: {model_id}")
print("📝 COPY THIS URL AND UPDATE YOUR .env FILE")
print("="*60)
print("\nEndpoints available:")
print("  POST /parse_resume      - Parse text")
print("  POST /parse_resume_pdf  - Parse PDF with OCR (NEW)")
print("  POST /draft_email       - Generate email")
print("="*60)
print("\n⚠️ IMPORTANT: Keep this cell running. Do NOT stop it.")
print("\n🚀 Starting server... (press Stop button to terminate)")

# Use uvicorn.Server directly (avoids loop_factory issue with nest_asyncio)
import uvicorn
import asyncio

config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
server = uvicorn.Server(config)

# Run the server - this works with nest_asyncio in Python 3.12
asyncio.get_event_loop().run_until_complete(server.serve())
