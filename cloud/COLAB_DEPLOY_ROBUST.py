# CYNO CLOUD GPU - ROBUST DEPLOYMENT (v4)
# Copy this ENTIRE cell into Google Colab and run it.

#===============================================
# STEP 1: Dependencies
#===============================================
print("📦 Installing dependencies...")
!pip install -q fastapi uvicorn pydantic transformers torch accelerate bitsandbytes pyngrok nest-asyncio

#===============================================
# STEP 2: Ngrok Config
#===============================================
NGROK_TOKEN = "YOUR_NGROK_TOKEN_HERE"  # <--- REPLACE THIS 

if NGROK_TOKEN == "YOUR_NGROK_TOKEN_HERE":
    raise ValueError("❌ Replace YOUR_NGROK_TOKEN_HERE with your token!")

#===============================================
# STEP 3: Write Server Code to File
#===============================================
print("📝 Writing server code to 'server_app.py'...")

server_code = r'''
import os
import torch
import json
import time
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

# --- Load Model ---
print("🧠 Loading Model in separate process...")
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)
print("✅ Model Loaded!")

# --- Logic ---
def extract_json(prompt):
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
    
    # Parse JSON
    try:
        content = response.strip()
        if content.startswith("```json"): content = content[7:]
        if content.startswith("```"): content = content[3:]
        if content.endswith("```"): content = content[:-3]
        if "}" in content: content = content[:content.rindex("}")+1]
        return json.loads(content.strip())
    except:
        return {}

# --- FastAPI App ---
app = FastAPI()

class ParseRequest(BaseModel):
    resume_text: str

class EmailDraftRequest(BaseModel):
    job_title: str
    company: str
    job_description: str
    resume_skills: list[str]
    resume_experience: int

@app.get("/")
def health():
    return {"status": "online", "gpu": torch.cuda.is_available()}

@app.post("/parse_resume")
def parse(req: ParseRequest):
    prompt = f"""You are an expert resume analyzer. Extract detailed information and return ONLY valid JSON with these exact keys:

{{
  "projects": ["list of notable projects with tech used"],
  "certifications": ["list of certifications"],
  "achievements": ["key accomplishments"],
  "soft_skills": ["soft skills list"],
  "languages": ["spoken languages"],
  "domains": ["AI/ML, Web, etc."],
  "work_experience": [{{ "role": "title", "company": "name", "key_tech": ["tech"] }}],
  "profile_type": "SOFTWARE_ENGINEER"
}}

Resume:
{req.resume_text[:3000]}

JSON:"""
    data = extract_json(prompt)
    if not data:
         # Fallback empty structure
         data = {"profile_type": "GENERAL", "projects": [], "domains": []}
         
    return {"success": True, "data": data}

@app.post("/draft_email")
def draft(req: EmailDraftRequest):
    skills_str = ", ".join(req.resume_skills[:5])
    prompt = f"""Write a professional cold email (max 150 words) for a job application.
    
Job: {req.job_title} at {req.company}
Candidate Skills: {skills_str}
Experience: {req.resume_experience} years
Instruction: Concise, enthusiastic, no placeholders.

Subject: <subject>

<body text>"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(model.device)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.7)
    
    raw = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    
    # Parse
    lines = raw.split('\\n')
    subject = f"Application for {req.job_title}"
    body = raw
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
            body = "\\n".join(lines[i+1:]).strip()
            break
            
    return {"success": True, "subject": subject, "body": body}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

with open("server_app.py", "w") as f:
    f.write(server_code)

#===============================================
# STEP 4: Start Server in Background
#===============================================
import subprocess
import time
from pyngrok import ngrok, conf

# Auth
conf.get_default().auth_token = NGROK_TOKEN
ngrok.kill()

print("🚀 Starting Server Process...")
# Run server.py in background
server_process = subprocess.Popen(["python", "server_app.py"])

print("⏳ Waiting 30s for model load...")
time.sleep(30) # Give it time to load model

#===============================================
# STEP 5: Tunnel
#===============================================
public_url = ngrok.connect(8000).public_url

print("\n" + "="*60)
print("✅ NGROK SERVER READY")
print("="*60)
print(f"🌐 Public URL: {public_url}")
print("="*60)
print("\n📝 AUTO-UPDATE INSTRUCTIONS:")
print("   Copy this command and run in your LOCAL terminal:")
print(f"\n   python scripts/update_env.py {public_url}")
print("\n   This will automatically update your .env file!")
print("\n⚠️  IMPORTANT: Keep this cell running. Do NOT stop it.")
print("="*60)

try:
    while True:
        time.sleep(10)
        if server_process.poll() is not None:
            print("❌ Server process died!")
            break
except KeyboardInterrupt:
    server_process.terminate()
    ngrok.kill()
