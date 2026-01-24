import os
from pathlib import Path
from datetime import datetime
from contextlib import closing
from langchain_ollama import ChatOllama
from tools.base import JobAgentTool
from models import Job, Resume, EmailDraft
from config import Config

class EmailDraftTool(JobAgentTool):
    def __init__(self):
        # No persistent LLM connection - create on-demand to avoid leaks
        pass
        
    def validate_input(self, **kwargs) -> bool:
        # We need a job and resume to draft an email
        return "job" in kwargs and "resume" in kwargs

    def execute(self, job: Job, resume: Resume, user_email: str = "applicant@example.com") -> EmailDraft:
        """
        Generates a cold email based on the job description and resume skills.
        Saves the draft to emails/ folder.
        """
        try:
            # 1. Construction Prompt
            prompt = f"""You are an expert career coach writing a cold email for a job application.
            
            JOB DETAILS:
            Title: {job.title}
            Company: {job.company}
            Description (Snippet): {job.description[:500]}...
            
            CANDIDATE DETAILS:
            Skills: {', '.join(resume.parsed_skills[:10])}
            Experience: {resume.years_exp} years
            Location: {resume.location}
            
            INSTRUCTIONS:
            - Write a concise, professional cold email (max 200 words).
            - Highlight 2-3 matching skills.
            - Show enthusiasm for {job.company}.
            - Do NOT use placeholders like [Your Name] - use the context provided or generic sign-offs.
            - Subject Line: Specific and catchy.
            
            OUTPUT FORMAT (Strict):
            Subject: <subject line>
            
            <Body of the email>
            """
            
            # 2. Generate with proper resource management
            with closing(ChatOllama(
                model=Config.CHAT_LLM_MODEL,
                base_url=Config.OLLAMA_BASE_URL,
                temperature=0.3,
                timeout=Config.LLM_REQUEST_TIMEOUT
            )) as llm:
                response = llm.invoke(prompt).content.strip()
            
            # 3. Parse Subject/Body
            lines = response.split('\n')
            subject = "Application for " + job.title
            body_start = 0
            
            for i, line in enumerate(lines):
                if line.lower().startswith("subject:"):
                    subject = line.split(":", 1)[1].strip()
                    body_start = i + 1
                    break
            
            body = "\n".join(lines[body_start:]).strip()
            
            # 4. Create Draft Object
            draft = EmailDraft(
                job_id=str(job.job_url), # Using URL as ID for now
                recipient="hiring.manager@company.com", # Placeholder
                subject=subject,
                body=body,
                status="DRAFT"
            )
            
            # 5. Save to File
            self._save_draft(draft, job.company)
            
            return draft

        except Exception as e:
            # Fallback for errors - don't crash
            return EmailDraft(
                job_id="error",
                recipient="error@system.com", # Must be valid EmailStr
                subject="Error Generating Draft",
                body=f"Failed to generate draft: {str(e)}",
                status="DRAFT"
            )

    def _save_draft(self, draft: EmailDraft, company_name: str):
        """Saves the draft to a text file."""
        import re
        folder = Path("emails")
        folder.mkdir(exist_ok=True)
        
        safe_company = re.sub(r'[^a-zA-Z0-9]', '_', company_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"draft_{safe_company}_{timestamp}.txt"
        
        filepath = folder / filename
        
        content = f"""SUBJECT: {draft.subject}
RECIPIENT: {draft.recipient}
STATUS: {draft.status}
---------------------------------------------------
{draft.body}
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
