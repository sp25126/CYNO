"""
CYNO Enhanced Cloud Client v2.0
Wires ALL heavy LLM tasks to Colab Brain with Local fallback.
Same functionality, different speeds:
- Cloud GPU: Fast (5-15 seconds)
- Local Ollama: Slower (30-90 seconds)
"""

import os
import time
import json
import base64
import requests
import structlog
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


@dataclass
class LLMResult:
    """Standardized result from LLM operations."""
    success: bool
    result: Any
    backend: str  # "cloud_gpu" | "local_ollama" | "local_gpu"
    time_seconds: float
    error: Optional[str] = None


class EnhancedCloudClient:
    """
    Enhanced Cloud Client that routes ALL heavy LLM tasks.
    
    Supported Operations:
    - Resume Parsing (text & PDF)
    - Cover Letter Generation
    - Email Drafting
    - Interview Q&A Generation
    - Job Matching/Scoring
    - Skill Gap Analysis
    - Resume Generation
    - General Text Generation
    
    Priority: Cloud GPU → Local GPU → Local Ollama
    """
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        timeout: int = 120,
        enable_fallback: bool = True
    ):
        self.server_url = server_url or os.getenv("COLAB_SERVER_URL")
        self.timeout = timeout
        self.enable_fallback = enable_fallback
        self.local_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.local_model = os.getenv("OLLAMA_MODEL", "gemma2:2b")
        
        # Stats tracking
        self._stats = {
            'cloud_success': 0,
            'cloud_failures': 0,
            'local_success': 0,
            'local_failures': 0,
            'total_time_cloud': 0.0,
            'total_time_local': 0.0
        }
        
        # Check availability
        self._cloud_available = self._check_cloud()
        self._local_available = self._check_local()
        
        logger.info(
            "enhanced_cloud_client_initialized",
            cloud_url=self.server_url,
            cloud_available=self._cloud_available,
            local_available=self._local_available
        )
    
    def _check_cloud(self) -> bool:
        """Check if Cloud GPU is available."""
        if not self.server_url:
            return False
        try:
            response = requests.get(f"{self.server_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _check_local(self) -> bool:
        """Check if Local Ollama is available."""
        try:
            response = requests.get(f"{self.local_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    # =====================================================
    # CORE LLM EXECUTION (Used by all methods)
    # =====================================================
    
    def _execute_llm(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.3,
        parse_json: bool = False
    ) -> LLMResult:
        """
        Execute LLM prompt on Cloud or Local.
        Same prompt, same output - different speeds.
        """
        start = time.time()
        
        # Try Cloud GPU first
        if self._cloud_available:
            try:
                result = self._execute_cloud(prompt, max_tokens, temperature)
                elapsed = time.time() - start
                self._stats['cloud_success'] += 1
                self._stats['total_time_cloud'] += elapsed
                
                return LLMResult(
                    success=True,
                    result=self._parse_output(result, parse_json),
                    backend="cloud_gpu",
                    time_seconds=round(elapsed, 2)
                )
            except Exception as e:
                logger.warning("cloud_execution_failed", error=str(e))
                self._stats['cloud_failures'] += 1
        
        # Fallback to Local
        if self.enable_fallback and self._local_available:
            try:
                result = self._execute_local(prompt, max_tokens, temperature)
                elapsed = time.time() - start
                self._stats['local_success'] += 1
                self._stats['total_time_local'] += elapsed
                
                return LLMResult(
                    success=True,
                    result=self._parse_output(result, parse_json),
                    backend="local_ollama",
                    time_seconds=round(elapsed, 2)
                )
            except Exception as e:
                logger.error("local_execution_failed", error=str(e))
                self._stats['local_failures'] += 1
        
        elapsed = time.time() - start
        return LLMResult(
            success=False,
            result=None,
            backend="none",
            time_seconds=round(elapsed, 2),
            error="No LLM backend available"
        )
    
    def _execute_cloud(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Execute on Cloud GPU via /exec endpoint."""
        url = f"{self.server_url.rstrip('/')}/exec"
        
        # Escape prompt for Python
        safe_prompt = prompt.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
        
        exec_code = f"""
prompt = '''{safe_prompt}'''
inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=5000).to(model.device)
with torch.no_grad():
    outputs = model.generate(
        **inputs, 
        max_new_tokens={max_tokens}, 
        temperature={temperature}, 
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id
    )
result = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(result)
"""
        
        response = requests.post(url, json={"code": exec_code}, timeout=self.timeout)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("output", "").strip()
            raise RuntimeError(result.get("error", "Unknown error"))
        raise RuntimeError(f"Cloud request failed: {response.status_code}")
    
    def _execute_local(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Execute on Local Ollama."""
        url = f"{self.local_url}/api/generate"
        
        payload = {
            "model": self.local_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        response = requests.post(url, json=payload, timeout=180)
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        raise RuntimeError(f"Ollama request failed: {response.status_code}")
    
    def _parse_output(self, text: str, parse_json: bool) -> Any:
        """Parse output, optionally extracting JSON."""
        if not parse_json:
            return text
        
        try:
            # Find JSON object
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
            
            # Try JSON array
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        
        return {"raw_text": text}
    
    # =====================================================
    # HEAVY TASK #1: RESUME PARSING (50+ fields)
    # =====================================================
    
    def parse_resume(self, resume_text: str) -> LLMResult:
        """
        Deep resume analysis extracting 50+ fields.
        Uses same prompt on Cloud or Local.
        """
        if len(resume_text.strip()) < 100:
            return LLMResult(False, None, "none", 0, "Resume too short")
        
        prompt = f"""You are an expert HR analyst. Analyze this resume and extract ALL information.

RESUME:
{resume_text[:4000]}

Return VALID JSON with these exact keys:
{{
    "name": "full name",
    "email": "email",
    "phone": "phone",
    "location": "city, country",
    "linkedin": "linkedin url",
    "github": "github url",
    "summary": "2-3 sentence professional summary",
    "years_experience": number,
    "profile_type": "AI_ML_ENGINEER|DATA_SCIENTIST|WEB_DEVELOPER|BACKEND_ENGINEER|FRONTEND_ENGINEER|FULLSTACK_ENGINEER|DEVOPS_ENGINEER|SOFTWARE_ENGINEER|GENERAL",
    "seniority_level": "INTERN|JUNIOR|MID|SENIOR|LEAD|PRINCIPAL",
    "technical_skills": ["skill1", "skill2"],
    "soft_skills": ["communication", "leadership"],
    "languages_spoken": ["English"],
    "tech_stack": {{
        "languages": [],
        "frameworks": [],
        "databases": [],
        "cloud": [],
        "devops": [],
        "ai_ml": []
    }},
    "work_experience": [
        {{"role": "title", "company": "name", "duration": "dates", "achievements": []}}
    ],
    "education": [
        {{"degree": "degree", "institution": "school", "year": "year"}}
    ],
    "projects": [
        {{"name": "project", "technologies": [], "description": "brief"}}
    ],
    "certifications": [],
    "achievements": [],
    "domains": ["AI/ML", "Web Development"],
    "strengths": ["top strengths"],
    "ideal_roles": ["best-fit job titles"],
    "keywords": ["ATS keywords"]
}}

RULES:
1. Extract ONLY information actually in the resume
2. years_experience must be a NUMBER
3. Use empty arrays [] for missing fields
4. Return pure JSON only

JSON:"""

        return self._execute_llm(prompt, max_tokens=1500, temperature=0.1, parse_json=True)
    
    def parse_resume_pdf(self, pdf_bytes: bytes) -> LLMResult:
        """Parse PDF resume using Cloud OCR."""
        if not self._cloud_available:
            return LLMResult(False, None, "none", 0, "Cloud required for PDF OCR")
        
        start = time.time()
        try:
            url = f"{self.server_url.rstrip('/')}/parse_resume_pdf"
            pdf_b64 = base64.b64encode(pdf_bytes).decode()
            response = requests.post(url, json={"pdf_base64": pdf_b64}, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return LLMResult(
                        success=True,
                        result=result.get("data", {}),
                        backend="cloud_gpu",
                        time_seconds=round(time.time() - start, 2)
                    )
                raise RuntimeError(result.get("error"))
            raise RuntimeError(f"Request failed: {response.status_code}")
        except Exception as e:
            return LLMResult(False, None, "cloud_gpu", round(time.time() - start, 2), str(e))
    
    # =====================================================
    # HEAVY TASK #2: COVER LETTER GENERATION
    # =====================================================
    
    def generate_cover_letter(
        self,
        job_title: str,
        company: str,
        job_description: str,
        skills: List[str],
        experience_years: int,
        projects: List[str] = None,
        tone: str = "professional"
    ) -> LLMResult:
        """Generate personalized cover letter."""
        
        prompt = f"""Write a compelling cover letter for this job application.

JOB DETAILS:
- Position: {job_title}
- Company: {company}
- Description: {job_description[:500]}

CANDIDATE:
- Skills: {', '.join(skills[:10])}
- Experience: {experience_years} years
- Notable Projects: {', '.join(projects[:3]) if projects else 'Various projects'}

TONE: {tone}

REQUIREMENTS:
1. Address to "Dear Hiring Manager" or "Dear {company} Team"
2. Opening: Express genuine interest in the specific role
3. Body: Connect 2-3 specific skills to job requirements
4. Include a brief achievement or project mention
5. Closing: Express enthusiasm for interview opportunity
6. Keep it under 350 words
7. Do NOT include placeholders like [Your Name]

COVER LETTER:"""

        return self._execute_llm(prompt, max_tokens=600, temperature=0.4)
    
    # =====================================================
    # HEAVY TASK #3: EMAIL DRAFTING
    # =====================================================
    
    def draft_email(
        self,
        job_title: str,
        company: str,
        job_description: str,
        resume_skills: List[str],
        resume_experience: int
    ) -> LLMResult:
        """Draft professional job application email."""
        
        # Try dedicated endpoint on Cloud first
        if self._cloud_available:
            try:
                start = time.time()
                url = f"{self.server_url.rstrip('/')}/draft_email"
                response = requests.post(url, json={
                    "job_title": job_title,
                    "company": company,
                    "job_description": job_description,
                    "resume_skills": resume_skills,
                    "resume_experience": resume_experience
                }, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return LLMResult(
                            success=True,
                            result={
                                "subject": result.get("subject"),
                                "body": result.get("body")
                            },
                            backend="cloud_gpu",
                            time_seconds=result.get("processing_time_seconds", time.time() - start)
                        )
            except Exception as e:
                logger.warning("cloud_email_failed", error=str(e))
        
        # Fallback to general prompt
        prompt = f"""Write a professional job application email.

JOB: {job_title} at {company}
Description: {job_description[:300]}

MY SKILLS: {', '.join(resume_skills[:5])}
EXPERIENCE: {resume_experience} years

Write a short, professional email:
1. Subject line
2. Greeting to hiring team
3. Express interest (2-3 sentences)
4. Mention 2 relevant skills
5. Request interview
6. Professional sign-off

EMAIL:"""

        result = self._execute_llm(prompt, max_tokens=400, temperature=0.3)
        
        # Parse into subject/body
        if result.success and isinstance(result.result, str):
            lines = result.result.strip().split('\n')
            subject = f"Application for {job_title}"
            body_lines = []
            for line in lines:
                if line.lower().startswith("subject:"):
                    subject = line.split(":", 1)[1].strip()
                else:
                    body_lines.append(line)
            result.result = {"subject": subject, "body": '\n'.join(body_lines).strip()}
        
        return result
    
    # =====================================================
    # HEAVY TASK #4: INTERVIEW Q&A GENERATION
    # =====================================================
    
    def generate_interview_questions(
        self,
        skills: List[str],
        projects: List[Dict] = None,
        job_title: str = ""
    ) -> LLMResult:
        """Generate personalized interview questions."""
        
        projects_str = json.dumps(projects[:5]) if projects else "None provided"
        
        prompt = f"""Generate interview questions based on this candidate's background.

TARGET ROLE: {job_title or 'Software Engineer'}
SKILLS: {', '.join(skills[:15])}
PROJECTS: {projects_str}

Return JSON with:
{{
    "technical_questions": [
        {{"question": "...", "expected_answer_hints": "...", "difficulty": "easy|medium|hard"}}
    ],
    "behavioral_questions": [
        {{"question": "...", "what_to_assess": "..."}}
    ],
    "project_specific_questions": [
        {{"question": "...", "relates_to": "project name"}}
    ]
}}

Generate 3-5 questions per category. Be specific to their actual experience.

JSON:"""

        return self._execute_llm(prompt, max_tokens=1000, temperature=0.3, parse_json=True)
    
    def generate_behavioral_answer(
        self,
        question: str,
        project_context: Dict
    ) -> LLMResult:
        """Generate STAR-format behavioral answer."""
        
        prompt = f"""Generate a STAR-format answer for this behavioral interview question.

QUESTION: {question}

CANDIDATE BACKGROUND:
- Projects: {json.dumps(project_context.get('projects', [])[:3])}
- Tech Stack: {', '.join(project_context.get('tech_stack', [])[:5])}
- Experience: {project_context.get('description', 'Software development')}

Create a compelling answer using STAR format:
- Situation: Set the context
- Task: Describe your responsibility  
- Action: Explain steps you took
- Result: Share the outcome with metrics if possible

Keep it concise (under 250 words) and specific.

ANSWER:"""

        return self._execute_llm(prompt, max_tokens=500, temperature=0.3)
    
    # =====================================================
    # HEAVY TASK #5: JOB MATCHING & SCORING
    # =====================================================
    
    def match_resume_to_job(
        self,
        resume_text: str,
        job_description: str
    ) -> LLMResult:
        """Calculate match score and provide recommendations."""
        
        prompt = f"""Compare this resume to the job description and calculate fit.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{job_description[:1500]}

Return JSON:
{{
    "match_score": number 0-100,
    "matching_skills": ["skills that match"],
    "missing_skills": ["required skills not in resume"],
    "experience_match": "exceeds|meets|below requirements",
    "recommendations": ["suggestions to improve match"],
    "interview_likelihood": "high|medium|low"
}}

Be honest and specific.

JSON:"""

        return self._execute_llm(prompt, max_tokens=500, temperature=0.1, parse_json=True)
    
    # =====================================================
    # HEAVY TASK #6: RESUME GENERATION
    # =====================================================
    
    def generate_resume(
        self,
        profile: Dict[str, Any],
        style: str = "professional",
        format: str = "markdown"
    ) -> LLMResult:
        """Generate professional resume from profile data."""
        
        # Try dedicated endpoint first
        if self._cloud_available:
            try:
                start = time.time()
                url = f"{self.server_url.rstrip('/')}/generate_resume"
                response = requests.post(url, json={
                    "profile": profile,
                    "style": style,
                    "format": format
                }, timeout=90)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        return LLMResult(
                            success=True,
                            result=result.get("resume"),
                            backend="cloud_gpu",
                            time_seconds=result.get("processing_time_seconds", time.time() - start)
                        )
            except Exception as e:
                logger.warning("cloud_resume_gen_failed", error=str(e))
        
        # Fallback to prompt-based generation
        prompt = f"""Create a professional resume in {format} format.

PROFILE:
- Name: {profile.get('name', 'Candidate')}
- Email: {profile.get('email', '')}
- Location: {profile.get('location', '')}
- Skills: {', '.join(profile.get('skills', [])[:20])}
- Experience: {json.dumps(profile.get('experience', [])[:5])}
- Education: {json.dumps(profile.get('education', [])[:3])}
- Projects: {json.dumps(profile.get('projects', [])[:5])}

STYLE: {style}

Create a well-formatted, ATS-friendly resume. Include all relevant information.
Do not use placeholders - use the actual data provided.

RESUME:"""

        return self._execute_llm(prompt, max_tokens=1500, temperature=0.3)
    
    # =====================================================
    # HEAVY TASK #7: SKILL GAP ANALYSIS
    # =====================================================
    
    def analyze_skill_gaps(
        self,
        resume_skills: List[str],
        job_requirements: List[str],
        job_title: str = ""
    ) -> LLMResult:
        """Deep skill gap analysis with learning recommendations."""
        
        prompt = f"""Analyze the skill gap between this candidate and job requirements.

CANDIDATE SKILLS: {', '.join(resume_skills)}
JOB REQUIREMENTS: {', '.join(job_requirements)}
TARGET ROLE: {job_title}

Return JSON:
{{
    "match_percentage": number 0-100,
    "matched_skills": ["skills that match"],
    "skill_gaps": ["missing required skills"],
    "priority_gaps": [
        {{"skill": "name", "priority": "high|medium|low", "reason": "why important"}}
    ],
    "learning_recommendations": [
        {{"skill": "name", "resource": "course/book/tutorial", "platform": "Coursera/Udemy/etc", "free": true/false}}
    ],
    "timeline_estimate": "estimated weeks to close gaps",
    "summary": "2-3 sentence summary"
}}

Be specific and actionable.

JSON:"""

        return self._execute_llm(prompt, max_tokens=800, temperature=0.2, parse_json=True)
    
    # =====================================================
    # HEAVY TASK #8: GENERAL TEXT GENERATION
    # =====================================================
    
    def generate_text(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.3,
        parse_json: bool = False
    ) -> LLMResult:
        """General-purpose text generation."""
        return self._execute_llm(prompt, max_tokens, temperature, parse_json)
    
    def summarize_text(self, text: str, max_words: int = 200) -> LLMResult:
        """Summarize any text."""
        prompt = f"""Summarize this text in {max_words} words or less:

{text[:4000]}

SUMMARY:"""
        return self._execute_llm(prompt, max_tokens=max_words * 2, temperature=0.2)
    
    def extract_keywords(self, text: str, count: int = 20) -> LLMResult:
        """Extract important keywords from text."""
        prompt = f"""Extract the {count} most important keywords from this text.
Return as a comma-separated list.

TEXT:
{text[:3000]}

KEYWORDS:"""
        result = self._execute_llm(prompt, max_tokens=100, temperature=0.1)
        if result.success:
            keywords = [k.strip() for k in result.result.split(",") if k.strip()]
            result.result = keywords
        return result
    
    # =====================================================
    # STATS & HEALTH
    # =====================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        total_cloud = self._stats['cloud_success'] + self._stats['cloud_failures']
        total_local = self._stats['local_success'] + self._stats['local_failures']
        
        return {
            "cloud_available": self._cloud_available,
            "local_available": self._local_available,
            "cloud_success_rate": self._stats['cloud_success'] / total_cloud if total_cloud > 0 else 0,
            "local_success_rate": self._stats['local_success'] / total_local if total_local > 0 else 0,
            "avg_cloud_time": self._stats['total_time_cloud'] / self._stats['cloud_success'] if self._stats['cloud_success'] > 0 else 0,
            "avg_local_time": self._stats['total_time_local'] / self._stats['local_success'] if self._stats['local_success'] > 0 else 0,
            **self._stats
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all backends."""
        return {
            "cloud": {
                "url": self.server_url,
                "available": self._check_cloud()
            },
            "local": {
                "url": self.local_url,
                "model": self.local_model,
                "available": self._check_local()
            }
        }


# Singleton instance
_client_instance = None

def get_cloud_client() -> EnhancedCloudClient:
    """Get or create the enhanced cloud client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = EnhancedCloudClient()
    return _client_instance


# Convenience functions for quick access
def quick_parse_resume(text: str) -> Dict:
    """Quick resume parsing."""
    client = get_cloud_client()
    result = client.parse_resume(text)
    return result.result if result.success else {"error": result.error}


def quick_generate_cover_letter(job_title: str, company: str, job_desc: str, skills: List[str], exp: int) -> str:
    """Quick cover letter generation."""
    client = get_cloud_client()
    result = client.generate_cover_letter(job_title, company, job_desc, skills, exp)
    return result.result if result.success else ""


def quick_match_job(resume: str, job_desc: str) -> Dict:
    """Quick job matching."""
    client = get_cloud_client()
    result = client.match_resume_to_job(resume, job_desc)
    return result.result if result.success else {"error": result.error}
