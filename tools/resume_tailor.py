import structlog
from typing import Dict
from models import Resume, Job

logger = structlog.get_logger(__name__)

class ResumeTailorTool:
    """
    Optional tool to generate job-specific resume variants.
    Only activated when user confirms they want to apply to a specific job.
    """
    
    def __init__(self):
        self.llm = None
        
    def _init_llm(self):
        """Lazy initialize LLM only when needed."""
        if self.llm is None:
            from langchain_ollama import ChatOllama
            self.llm = ChatOllama(model="gemma2:2b", base_url="http://localhost:11434", temperature=0.3)
    
    def tailor_resume_to_job(self, resume: Resume, job: Job) -> str:
        """
        Generate a job-specific resume variant.
        
        Args:
            resume: Parsed resume object
            job: Target job object
            
        Returns:
            Markdown-formatted tailored resume
        """
        self._init_llm()
        log = logger.bind(tool="ResumeTailor", job_title=job.title)
        
        try:
            # Build source data summary
            source_summary = f"""
ORIGINAL RESUME DATA:
Skills: {', '.join(resume.parsed_skills)}
Experience: {resume.years_exp} years
Projects: {', '.join(resume.projects) if resume.projects else 'None listed'}
Certifications: {', '.join(resume.certifications) if resume.certifications else 'None'}
Achievements: {', '.join(resume.achievements) if resume.achievements else 'None'}
Soft Skills: {', '.join(resume.soft_skills) if resume.soft_skills else 'None'}
"""

            prompt = f"""You are a professional resume writer. Create a tailored resume for this job WITHOUT hallucinating.

CRITICAL RULES:
1. Use ONLY information from the ORIGINAL RESUME DATA below
2. Do NOT invent experience, skills, or projects
3. Rephrase and reorganize to emphasize relevant skills for the job
4. Keep it concise (max 400 words)
5. Output in clean Markdown format

{source_summary}

TARGET JOB:
Title: {job.title}
Company: {job.company}
Description: {job.description[:500]}...

TASK: Generate a tailored resume that emphasizes the most relevant skills/experience for this job.

TAILORED RESUME (Markdown):"""

            response = self.llm.invoke(prompt)
            tailored = response.content.strip()
            
            # Validate no hallucination
            if self._validate_no_hallucination(resume, tailored):
                log.info("tailoring_success", length=len(tailored))
                return tailored
            else:
                log.warning("hallucination_detected", falling_back=True)
                return self._generate_safe_resume(resume, job)
                
        except Exception as e:
            log.error("tailoring_failed", error=str(e))
            return self._generate_safe_resume(resume, job)
    
    def _validate_no_hallucination(self, resume: Resume, tailored: str) -> bool:
        """
        Check if tailored resume contains only truthful information.
        Uses simple keyword matching as a first check.
        """
        # Extract all meaningful words from source
        source_text = resume.raw_text.lower()
        
        # Check for suspicious patterns (fake companies, fake years)
        suspicious_patterns = [
            r'\d{4}\s*-\s*\d{4}',  # Date ranges not in original
            r'led\s+team\s+of\s+\d+',  # Specific team sizes
            r'increased\s+\w+\s+by\s+\d+%',  # Specific metrics
        ]
        
        import re
        for pattern in suspicious_patterns:
            matches = re.findall(pattern, tailored.lower())
            for match in matches:
                if match not in source_text:
                    # Found potential hallucination
                    return False
        
        return True
    
    def _generate_safe_resume(self, resume: Resume, job: Job) -> str:
        """
        Fallback: Generate safe resume by simple reorganization.
        """
        return f"""# {resume.profile_type.title()} Professional

## Skills
{', '.join(resume.parsed_skills[:10])}

## Experience
{resume.years_exp} years of professional experience in {resume.profile_type.lower()}

## Key Qualifications
{"- " + chr(10).join(resume.achievements[:3]) if resume.achievements else "- Experienced professional seeking new opportunities"}

## Projects
{"- " + chr(10).join(resume.projects[:3]) if resume.projects else "Available upon request"}

## Certifications
{', '.join(resume.certifications) if resume.certifications else 'N/A'}

---
*Tailored for: {job.title} at {job.company}*
"""
