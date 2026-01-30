"""
CYNO Unified LLM Brain
Same functionality for Cloud GPU and Local Ollama - only speed differs.
Uses EnhancedCloudClient for all heavy LLM tasks.
"""

import os
import json
import structlog
import requests
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = structlog.get_logger(__name__)


class LLMBrain:
    """
    Unified LLM interface that works identically on Cloud GPU or Local Ollama.
    All heavy tasks are routed through EnhancedCloudClient.
    
    Cloud GPU = Fast (5-15 seconds)
    Local Ollama = Slower (30-90 seconds)
    Same prompts, same outputs.
    """
    
    def __init__(self, prefer_cloud: bool = True):
        """
        Initialize LLM Brain.
        
        Args:
            prefer_cloud: If True, try Cloud GPU first, fallback to Local
        """
        # Import and use enhanced cloud client
        try:
            from cloud.enhanced_client import get_cloud_client
            self._client = get_cloud_client()
            self._use_client = True
        except ImportError:
            self._client = None
            self._use_client = False
            logger.warning("enhanced_client_not_available", fallback="direct")
        
        # Fallback direct connection info
        self.cloud_url = os.getenv("COLAB_SERVER_URL") if prefer_cloud else None
        self.local_model = os.getenv("OLLAMA_MODEL", "gemma2:2b")
        self.local_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.log = logger.bind(brain="LLMBrain")
        
        # Check availability
        if self._use_client:
            self._cloud_available = self._client._cloud_available
            self._local_available = self._client._local_available
        else:
            self._cloud_available = self._check_cloud()
            self._local_available = self._check_local()
        
        self.log.info("brain_initialized", 
                     cloud=self._cloud_available, 
                     local=self._local_available,
                     using_client=self._use_client)
    
    def _check_cloud(self) -> bool:
        """Check if Cloud GPU is available."""
        if not self.cloud_url:
            return False
        try:
            response = requests.get(f"{self.cloud_url}/", timeout=5)
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
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.2,
        output_format: str = "text"
    ) -> Dict[str, Any]:
        """
        Generate text using LLM. Same functionality regardless of backend.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Creativity (0.0 = deterministic, 1.0 = creative)
            output_format: "text", "json", or "list"
            
        Returns:
            Dict with 'success', 'result', 'backend', 'time_seconds'
        """
        import time
        start = time.time()
        
        # Try Cloud first if available
        if self._cloud_available:
            try:
                result = self._generate_cloud(prompt, max_tokens, temperature)
                elapsed = time.time() - start
                self.log.info("cloud_generation_success", time=elapsed)
                return {
                    "success": True,
                    "result": self._parse_output(result, output_format),
                    "raw": result,
                    "backend": "cloud_gpu",
                    "time_seconds": round(elapsed, 2)
                }
            except Exception as e:
                self.log.warning("cloud_generation_failed", error=str(e))
        
        # Fallback to Local
        if self._local_available:
            try:
                result = self._generate_local(prompt, max_tokens, temperature)
                elapsed = time.time() - start
                self.log.info("local_generation_success", time=elapsed)
                return {
                    "success": True,
                    "result": self._parse_output(result, output_format),
                    "raw": result,
                    "backend": "local_ollama",
                    "time_seconds": round(elapsed, 2)
                }
            except Exception as e:
                self.log.error("local_generation_failed", error=str(e))
        
        return {
            "success": False,
            "error": "No LLM backend available. Configure COLAB_SERVER_URL or start Ollama.",
            "backend": "none",
            "time_seconds": 0
        }
    
    def _generate_cloud(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Cloud GPU."""
        url = f"{self.cloud_url.rstrip('/')}/exec"
        
        # Escape prompt for Python string
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
        
        response = requests.post(url, json={"code": exec_code}, timeout=120)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("output", "").strip()
            raise RuntimeError(result.get("error", "Unknown error"))
        raise RuntimeError(f"Cloud request failed: {response.status_code}")
    
    def _generate_local(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate using Local Ollama."""
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
    
    def _parse_output(self, text: str, output_format: str) -> Any:
        """Parse output based on expected format."""
        if output_format == "json":
            # Try to extract JSON
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
        
        elif output_format == "list":
            # Extract numbered or bulleted list
            import re
            lines = text.strip().split("\n")
            items = []
            for line in lines:
                # Remove numbering and bullets
                cleaned = re.sub(r'^[\d\.\-\*\•]+\s*', '', line.strip())
                if cleaned:
                    items.append(cleaned)
            return items
        
        return text
    
    # ==========================================
    # High-Level Analysis Methods
    # ==========================================
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Deep resume analysis - same on Cloud or Local.
        Extracts 50+ fields with AI insights.
        """
        prompt = self._get_resume_prompt(resume_text)
        result = self.generate(prompt, max_tokens=1500, temperature=0.1, output_format="json")
        
        if result["success"]:
            return {
                "success": True,
                "analysis": result["result"],
                "backend": result["backend"],
                "time": result["time_seconds"]
            }
        return result
    
    def generate_interview_questions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate interview questions based on resume/project context."""
        prompt = self._get_interview_prompt(context)
        result = self.generate(prompt, max_tokens=800, temperature=0.3, output_format="json")
        return result
    
    def generate_cover_letter(
        self, 
        job_title: str, 
        company: str, 
        job_description: str, 
        candidate_info: Dict
    ) -> Dict[str, Any]:
        """Generate a personalized cover letter."""
        prompt = self._get_cover_letter_prompt(job_title, company, job_description, candidate_info)
        result = self.generate(prompt, max_tokens=600, temperature=0.4, output_format="text")
        return result
    
    def match_resume_to_job(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate match score and provide recommendations."""
        prompt = self._get_match_prompt(resume_text, job_description)
        result = self.generate(prompt, max_tokens=500, temperature=0.1, output_format="json")
        return result
    
    def generate_behavioral_answer(self, question: str, context: Dict) -> Dict[str, Any]:
        """Generate STAR-format behavioral answer."""
        prompt = self._get_behavioral_prompt(question, context)
        result = self.generate(prompt, max_tokens=500, temperature=0.3, output_format="text")
        return result
    
    def explain_tech_choice(self, tech: str, alternatives: List[str], project_context: Dict) -> Dict[str, Any]:
        """Explain why a technology was chosen over alternatives."""
        prompt = self._get_tech_choice_prompt(tech, alternatives, project_context)
        result = self.generate(prompt, max_tokens=400, temperature=0.3, output_format="text")
        return result
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """Summarize any text."""
        prompt = f"""Summarize the following text in {max_length} words or less.
Be concise and capture the key points.

TEXT:
{text[:4000]}

SUMMARY:"""
        result = self.generate(prompt, max_tokens=max_length * 2, temperature=0.2)
        return result.get("result", "") if result["success"] else ""
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        prompt = f"""Extract the 20 most important keywords from this text.
Return as a simple comma-separated list.

TEXT:
{text[:3000]}

KEYWORDS:"""
        result = self.generate(prompt, max_tokens=100, temperature=0.1)
        if result["success"]:
            keywords = result.get("result", "").split(",")
            return [k.strip() for k in keywords if k.strip()]
        return []
    
    # ==========================================
    # Prompt Templates (Used by both Cloud & Local)
    # ==========================================
    
    def _get_resume_prompt(self, text: str) -> str:
        """Comprehensive resume analysis prompt."""
        return f"""You are an expert HR analyst. Analyze this resume and extract ALL information.

RESUME:
{text[:4000]}

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
    "salary_estimate": "range based on experience",
    "keywords": ["ATS keywords"]
}}

RULES:
1. Extract ONLY information actually in the resume
2. years_experience must be a NUMBER
3. Use empty arrays [] for missing fields
4. Return pure JSON only

JSON:"""

    def _get_interview_prompt(self, context: Dict) -> str:
        """Interview questions prompt."""
        projects = context.get("projects", [])
        skills = context.get("skills", [])
        
        return f"""Generate interview questions based on this candidate's background.

SKILLS: {', '.join(skills[:15])}
PROJECTS: {json.dumps(projects[:5]) if projects else 'None'}

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

    def _get_cover_letter_prompt(self, job_title: str, company: str, job_desc: str, candidate: Dict) -> str:
        """Cover letter prompt."""
        skills = candidate.get("skills", [])
        experience = candidate.get("years_exp", 0)
        
        return f"""Write a compelling cover letter for this job application.

JOB: {job_title} at {company}
DESCRIPTION: {job_desc[:500]}

CANDIDATE:
- Skills: {', '.join(skills[:10])}
- Experience: {experience} years

REQUIREMENTS:
1. Address to "Dear Hiring Team"
2. Opening: Express genuine interest
3. Body: Connect 2-3 specific skills to job requirements
4. Mention a relevant achievement
5. Closing: Express enthusiasm for interview
6. Keep under 300 words
7. Professional but personable tone

COVER LETTER:"""

    def _get_match_prompt(self, resume: str, job_desc: str) -> str:
        """Resume-job matching prompt."""
        return f"""Compare this resume to the job description and calculate fit.

RESUME:
{resume[:2000]}

JOB DESCRIPTION:
{job_desc[:1500]}

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

    def _get_behavioral_prompt(self, question: str, context: Dict) -> str:
        """Behavioral answer prompt."""
        projects = context.get("projects", [])
        experience = context.get("experience", "")
        
        return f"""Generate a STAR-format answer for this behavioral interview question.

QUESTION: {question}

CANDIDATE BACKGROUND:
- Projects: {json.dumps(projects[:3]) if projects else 'Various projects'}
- Experience: {experience if experience else 'Software development experience'}

Create a compelling answer using STAR format:
- Situation: Set the context
- Task: Describe your responsibility  
- Action: Explain steps you took
- Result: Share the outcome with metrics if possible

Keep it concise (under 250 words) and specific.

ANSWER:"""

    def _get_tech_choice_prompt(self, tech: str, alternatives: List[str], context: Dict) -> str:
        """Technology choice explanation prompt."""
        project = context.get("project_name", "the project")
        
        return f"""Explain why {tech} was chosen over {', '.join(alternatives)} for {project}.

PROJECT CONTEXT: {json.dumps(context)}

Create a convincing explanation covering:
1. Key advantages of {tech} for this use case
2. Why alternatives weren't ideal
3. Specific benefits realized

Keep it technical but accessible. Under 200 words.

EXPLANATION:"""


# Singleton instance
_brain_instance = None

def get_brain(prefer_cloud: bool = True) -> LLMBrain:
    """Get or create the LLM brain instance."""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = LLMBrain(prefer_cloud=prefer_cloud)
    return _brain_instance


# Convenience functions
def quick_generate(prompt: str, output_format: str = "text") -> Any:
    """Quick generation without creating an instance."""
    brain = get_brain()
    result = brain.generate(prompt, output_format=output_format)
    return result.get("result") if result["success"] else None


def quick_analyze_resume(text: str) -> Dict:
    """Quick resume analysis."""
    brain = get_brain()
    return brain.analyze_resume(text)
