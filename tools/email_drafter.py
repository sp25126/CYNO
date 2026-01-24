import os
from pathlib import Path
from datetime import datetime
from tools.base import JobAgentTool
from models import Job, Resume, EmailDraft
from cloud.cloud_client import CloudClient

class EmailDraftTool(JobAgentTool):
    def __init__(self):
        # Initialize cloud client for email generation
        self.cloud_client = CloudClient()
        
    def validate_input(self, **kwargs) -> bool:
        # We need a job and resume to draft an email
        return "job" in kwargs and "resume" in kwargs

    def execute(self, job: Job, resume: Resume, user_email: str = "applicant@example.com") -> EmailDraft:
        """
        Generates a cold email based on the job description and resume skills.
        Uses Cloud GPU for generation. Saves the draft to emails/ folder.
        """
        try:
            # Generate email using cloud
            result = self.cloud_client.draft_email(
                job_title=job.title,
                company=job.company,
                job_description=job.description,
                resume_skills=resume.parsed_skills,
                resume_experience=resume.years_exp
            )
            
            subject = result.get('subject', f"Application for {job.title}")
            body = result.get('body', '')
            
            # Create Draft Object
            draft = EmailDraft(
                recipient_email="hiring.manager@company.com",
                subject=subject,
                body=body,
                job_title=job.title,
                company=job.company
            )
            
            # Save to File
            self._save_draft(draft, job.company)
            
            return draft

        except Exception as e:
            # Fallback for errors - don't crash
            return EmailDraft(
                recipient_email="error@system.com",
                subject="Error Generating Draft",
                body=f"Failed to generate draft: {str(e)}",
                job_title=job.title if job else "Unknown",
                company=job.company if job else "Unknown"
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
RECIPIENT: {draft.recipient_email}
---------------------------------------------------
{draft.body}
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
