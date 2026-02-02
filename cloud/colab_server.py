"""
Colab GPU Server for Resume Parsing
Runs FastAPI on Google Colab with ngrok tunneling.

DEPLOYMENT INSTRUCTIONS:
1. Open Google Colab: https://colab.research.google.com
2. Change Runtime -> Change runtime type -> T4 GPU
3. Paste this entire file into a cell
4. Run the cell
5. Copy the ngrok URL (e.g., https://xxxx.ngrok.io) and paste it to local client

CRITICAL: This server is FREE but will shut down after ~12 hours of Colab inactivity.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required packages in Colab environment"""
    logger.info("Installing dependencies...")
    
    packages = [
        "fastapi",
        "uvicorn[standard]",
        "pyngrok",
        "transformers",
        "torch",
        "accelerate",
        "bitsandbytes",  # For quantization
        "pydantic"
    ]
    
    for pkg in packages:
        os.system(f"pip install -q {pkg}")
    
    logger.info("Dependencies installed successfully")

def load_model():
    """Load quantized Llama-3-8B-Instruct model"""
    logger.info("Loading model... This may take 2-3 minutes on first run.")
    
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    import torch
    
    model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
    
    # Quantization config for 4-bit loading (fits in 16GB GPU)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
        
        logger.info(f"Model loaded: {model_id} (4-bit quantized)")
        return tokenizer, model
    
    except Exception as e:
        logger.error(f"Model loading failed: {e}")
        logger.info("Falling back to smaller model: google/gemma-2b-it")
        
        # Fallback to smaller model
        model_id = "google/gemma-2b-it"
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto"
        )
        logger.info(f"Fallback model loaded: {model_id}")
        return tokenizer, model

# Global model storage
TOKENIZER = None
MODEL = None

def extract_resume_data(resume_text: str) -> Dict[str, Any]:
    """
    Extract structured data from resume using LLM
    
    Args:
        resume_text: Raw resume text
        
    Returns:
        Dictionary with extracted fields
    """
    global TOKENIZER, MODEL
    
    if TOKENIZER is None or MODEL is None:
        raise RuntimeError("Model not loaded. Call load_model() first.")
    
    prompt = f"""You are an expert resume analyzer. Extract detailed information and return ONLY valid JSON with these exact keys:

{{
  "projects": ["list of notable projects with tech used"],
  "certifications": ["list of certifications/credentials"],
  "achievements": ["key accomplishments with metrics if available"],
  "soft_skills": ["leadership, communication, teamwork, etc."],
  "languages": ["English", "Spanish", etc.],
  "domains": ["SPECIFIC technical domains: AI/ML, Web Development, Cloud, DevOps, Mobile, Data Science, etc."],
  "work_experience": [
    {{
      "role": "job title",
      "company": "company name",
      "duration": "timeframe",
      "key_tech": ["main technologies used"]
    }}
  ],
  "profile_type": "MOST SPECIFIC: AI_ML_ENGINEER, WEB_DEVELOPER, FULLSTACK_ENGINEER, DATA_SCIENTIST, DEVOPS_ENGINEER, SOFTWARE_ENGINEER, or GENERAL"
}}

CRITICAL RULES:
1. Extract ONLY information explicitly stated in the resume
2. For "domains": List ALL technical specializations found (AI, Web Dev, Cloud, etc.)
3. For "work_experience": Extract up to 3 most recent roles with technologies
4. For "profile_type": Choose the MOST SPECIFIC category based on skills and experience
5. Do NOT hallucinate - if unsure, use empty list []
6. Return pure JSON only, no markdown

Resume Text:
{resume_text[:3000]}

JSON:"""

    # Tokenize
    inputs = TOKENIZER(prompt, return_tensors="pt", truncation=True, max_length=2048).to(MODEL.device)
    
    # Generate
    import torch
    with torch.no_grad():
        outputs = MODEL.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.1,
            do_sample=True,
            top_p=0.9,
            pad_token_id=TOKENIZER.eos_token_id
        )
    
    # Decode
    response = TOKENIZER.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    
    logger.info(f"Raw LLM response: {response[:200]}...")
    
    # Parse JSON from response
    try:
        # Clean potential markdown formatting
        content = response.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        parsed = json.loads(content.strip())
        
        # Validate structure
        return {
            'projects': parsed.get('projects', [])[:5],
            'certifications': parsed.get('certifications', [])[:5],
            'achievements': parsed.get('achievements', [])[:5],
            'soft_skills': parsed.get('soft_skills', [])[:5],
            'languages': parsed.get('languages', [])[:3],
            'domains': parsed.get('domains', [])[:10],
            'work_experience': parsed.get('work_experience', [])[:3],
            'profile_type': parsed.get('profile_type', 'GENERAL')
        }
    
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed: {e}. Raw response: {response}")
        # Return empty structure
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

# ==========================================
# FastAPI Server
# ==========================================

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time

app = FastAPI(title="Cyno Resume Parser GPU Server", version="1.0")

class ParseRequest(BaseModel):
    resume_text: str

class ParseResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time_seconds: float

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Cyno Resume Parser",
        "status": "online",
        "model_loaded": MODEL is not None,
        "gpu_available": "cuda" in str(MODEL.device) if MODEL else False
    }

@app.post("/parse_resume", response_model=ParseResponse)
async def parse_resume(request: ParseRequest):
    """
    Parse resume text and extract structured data
    
    Args:
        request: ParseRequest with resume_text
        
    Returns:
        ParseResponse with extracted data
    """
    start_time = time.time()
    
    try:
        if not request.resume_text or len(request.resume_text.strip()) < 100:
            raise HTTPException(status_code=400, detail="Resume text too short (min 100 chars)")
        
        logger.info(f"Processing resume ({len(request.resume_text)} chars)...")
        
        data = extract_resume_data(request.resume_text)
        
        processing_time = time.time() - start_time
        logger.info(f"Resume parsed successfully in {processing_time:.2f}s")
        
        return ParseResponse(
            success=True,
            data=data,
            processing_time_seconds=processing_time
        )
    
    except Exception as e:
        logger.error(f"Parsing error: {str(e)}")
        return ParseResponse(
            success=False,
            error=str(e),
            processing_time_seconds=time.time() - start_time
        )

# ==========================================
# Colab Startup Script
# ==========================================

def start_server(ngrok_token: Optional[str] = None):
    """
    Start the FastAPI server with ngrok tunnel
    
    Args:
        ngrok_token: Your ngrok authtoken (get from https://dashboard.ngrok.com/get-started/your-authtoken)
                     If None, will use free tier with random URLs
    """
    global TOKENIZER, MODEL
    
    logger.info("=" * 60)
    logger.info("CYNO GPU SERVER INITIALIZATION")
    logger.info("=" * 60)
    
    # Step 1: Install dependencies
    install_dependencies()
    
    # Step 2: Load model
    TOKENIZER, MODEL = load_model()
    
    # Step 3: Setup ngrok
    from pyngrok import ngrok
    
    if ngrok_token:
        logger.info("Setting ngrok authtoken...")
        ngrok.set_auth_token(ngrok_token)
    else:
        logger.warning("No ngrok token provided. Using free tier (random URLs, 2-hour limit)")
    
    # Step 4: Start uvicorn in background
    import uvicorn
    from threading import Thread
    
    def run_server():
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Give server time to start
    time.sleep(3)
    
    # Step 5: Create ngrok tunnel
    logger.info("Creating ngrok tunnel...")
    public_url = ngrok.connect(8000)
    
    logger.info("=" * 60)
    logger.info("✅ SERVER READY")
    logger.info("=" * 60)
    logger.info(f"🌐 Public URL: {public_url}")
    logger.info("📝 Copy this URL to your local CloudClient configuration")
    logger.info("=" * 60)
    logger.info("\nServer will run until Colab disconnects (typically 12 hours)")
    logger.info("Press Ctrl+C to stop")
    
    # Keep alive
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("\nShutting down server...")
        ngrok.disconnect(public_url)

# ==========================================
# COLAB USAGE EXAMPLE
# ==========================================

if __name__ == "__main__":
    # OPTION 1: Free tier (recommended for testing)
    start_server()
    
    # OPTION 2: With ngrok token for persistent URLs
    # Get token from: https://dashboard.ngrok.com/get-started/your-authtoken
    # start_server(ngrok_token="YOUR_NGROK_TOKEN_HERE")
