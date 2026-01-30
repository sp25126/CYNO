"""
CYNO Email Drafter Tool - Enhanced with Personalization
Uses the SmartEmailEngine for AI-powered personalized email generation.
"""

import os
from pathlib import Path
from datetime import datetime
import structlog
from typing import Optional, Dict, Any
from tools.base import JobAgentTool
from models import Job, Resume, EmailDraft as LegacyEmailDraft

logger = structlog.get_logger(__name__)


class EmailDraftTool(JobAgentTool):
    """
    Enhanced email drafting tool with deep personalization.
    Uses SmartEmailEngine internally for AI-powered generation.
    
    Features:
    - Personalized emails based on user profile
    - Company research integration
    - Multiple email types (application, follow-up, referral)
    - Automatic draft saving
    """
    
    def __init__(self, user_prefs: Optional[Dict] = None):
        """
        Initialize the email drafter.
        
        Args:
            user_prefs: Optional dictionary with user preferences
        """
        self._engine = None
        self._user_prefs = user_prefs
        self.log = logger.bind(tool="EmailDraftTool")
    
    def _get_engine(self):
        """Lazy load the SmartEmailEngine."""
        if self._engine is None:
            try:
                from tools.smart_email import SmartEmailEngine, UserPersonalization
                
                prefs = None
                if self._user_prefs:
                    prefs = UserPersonalization(**self._user_prefs)
                
                # Try to load from file
                self._engine = SmartEmailEngine(prefs)
                self._engine.load_personalization_from_file("data/user_prefs.json")
                
            except ImportError:
                self.log.warning("smart_email_not_available")
        return self._engine
        
    def validate_input(self, **kwargs) -> bool:
        """Validate input: requires job and resume."""
        return "job" in kwargs and "resume" in kwargs

    def execute(
        self, 
        job: Job, 
        resume: Resume, 
        user_email: str = "applicant@example.com",
        email_type: str = "application",
        company_research: Dict = None,
        custom_hook: str = None
    ) -> LegacyEmailDraft:
        """
        Generate a personalized cold email.
        
        Args:
            job: Job object with title, company, description
            resume: Resume object with skills, experience
            user_email: User's email address
            email_type: Type of email (application, follow_up, cold_outreach)
            company_research: Optional company research data
            custom_hook: Optional custom opening hook
            
        Returns:
            EmailDraft with subject and body
        """
        self.log.info("generating_email", 
                     company=job.company,
                     type=email_type)
        
        engine = self._get_engine()
        
        if engine:
            try:
                # Update personalization from resume if not already set
                if not engine.user_prefs.name:
                    from tools.smart_email import UserPersonalization
                    resume_data = {
                        'name': getattr(resume, 'name', ''),
                        'email': user_email,
                        'years_exp': resume.years_exp,
                        'parsed_skills': resume.parsed_skills,
                        'projects': getattr(resume, 'projects', []),
                        'achievements': getattr(resume, 'achievements', []),
                        'summary': getattr(resume, 'summary', ''),
                        'linkedin': getattr(resume, 'linkedin', ''),
                        'github': getattr(resume, 'github', '')
                    }
                    prefs = UserPersonalization.from_resume(resume_data)
                    prefs.email = user_email
                    engine.set_personalization(prefs)
                
                # Generate based on type
                if email_type == "follow_up":
                    # Create original email reference
                    from tools.smart_email import EmailDraft as SmartEmailDraft
                    original = SmartEmailDraft(
                        subject=f"Application for {job.title}",
                        body="",
                        company=job.company,
                        job_title=job.title
                    )
                    draft = engine.generate_follow_up_email(
                        original_email=original,
                        days_since=3,
                        follow_up_number=1
                    )
                else:
                    # Standard application email
                    draft = engine.generate_application_email(
                        job_title=job.title,
                        company=job.company,
                        job_description=job.description,
                        resume_highlights=resume.parsed_skills[:5],
                        company_research=company_research,
                        custom_hook=custom_hook
                    )
                
                # Save the draft
                engine.save_draft(draft)
                
                self.log.info("email_generated",
                             backend=draft.backend_used,
                             time=draft.generation_time)
                
                # Convert to legacy format
                return LegacyEmailDraft(
                    recipient_email="hiring.manager@company.com",
                    subject=draft.subject,
                    body=draft.body,
                    job_title=job.title,
                    company=job.company
                )
                
            except Exception as e:
                self.log.warning("smart_engine_failed", error=str(e))
        
        # Fallback to basic generation
        return self._generate_basic_email(job, resume, user_email)
    
    def _generate_basic_email(
        self, 
        job: Job, 
        resume: Resume, 
        user_email: str
    ) -> LegacyEmailDraft:
        """Basic email generation fallback."""
        subject = f"Application for {job.title} at {job.company}"
        
        skills_text = ', '.join(resume.parsed_skills[:5])
        
        body = f"""Dear Hiring Team,

I am writing to express my strong interest in the {job.title} position at {job.company}.

With {resume.years_exp} years of experience in {skills_text}, I am confident in my ability to contribute meaningfully to your team.

My background includes hands-on experience with the technologies and methodologies outlined in your job description. I would welcome the opportunity to discuss how my skills align with your needs.

I look forward to the possibility of contributing to {job.company}'s success.

Best regards"""
        
        draft = LegacyEmailDraft(
            recipient_email="hiring.manager@company.com",
            subject=subject,
            body=body,
            job_title=job.title,
            company=job.company
        )
        
        # Save draft to file
        self._save_draft(draft, job.company)
        
        return draft
    
    def _save_draft(self, draft: LegacyEmailDraft, company_name: str):
        """Save draft to file (legacy)."""
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


# =====================================================
# ADDITIONAL EMAIL TOOLS (Implementing CYNO_IDEAS)
# =====================================================

class FollowUpReminderTool(JobAgentTool):
    """
    Smart reminders for application follow-ups.
    Tracks sent applications and suggests when to follow up.
    """
    
    def __init__(self):
        self._engine = None
        self.log = logger.bind(tool="FollowUpReminder")
    
    def _get_engine(self):
        if self._engine is None:
            try:
                from tools.smart_email import get_email_engine
                self._engine = get_email_engine()
            except ImportError:
                pass
        return self._engine
    
    def execute(
        self,
        company: str,
        job_title: str,
        application_date: str,
        follow_up_intervals: list = None
    ) -> Dict[str, Any]:
        """
        Generate follow-up reminders and draft emails.
        
        Args:
            company: Company name
            job_title: Position applied for
            application_date: Date of original application (YYYY-MM-DD)
            follow_up_intervals: Days for follow-ups (default: [3, 7, 14])
        """
        from datetime import datetime, timedelta
        
        intervals = follow_up_intervals or [3, 7, 14]
        app_date = datetime.strptime(application_date, "%Y-%m-%d")
        
        # Calculate follow-up dates
        follow_ups = []
        for days in intervals:
            follow_up_date = app_date + timedelta(days=days)
            follow_ups.append({
                "days_after": days,
                "date": follow_up_date.strftime("%Y-%m-%d"),
                "status": "pending" if follow_up_date > datetime.now() else "overdue"
            })
        
        # Generate follow-up emails using engine
        drafts = []
        engine = self._get_engine()
        
        if engine:
            from tools.smart_email import EmailDraft
            original = EmailDraft(
                subject=f"Application for {job_title}",
                body="",
                company=company,
                job_title=job_title
            )
            
            for i, interval in enumerate(intervals):
                try:
                    draft = engine.generate_follow_up_email(
                        original_email=original,
                        days_since=interval,
                        follow_up_number=i + 1
                    )
                    drafts.append({
                        "follow_up_number": i + 1,
                        "days_after": interval,
                        "subject": draft.subject,
                        "body": draft.body[:200] + "..."
                    })
                except Exception as e:
                    self.log.warning("draft_generation_failed", error=str(e))
        
        return {
            "company": company,
            "job_title": job_title,
            "application_date": application_date,
            "follow_up_schedule": follow_ups,
            "draft_previews": drafts
        }


class ColdEmailSequencerTool(JobAgentTool):
    """
    Schedule follow-up emails with intelligent timing.
    Generates a complete email sequence for a job application.
    """
    
    def __init__(self):
        self._engine = None
        self.log = logger.bind(tool="ColdEmailSequencer")
    
    def _get_engine(self):
        if self._engine is None:
            try:
                from tools.smart_email import get_email_engine
                self._engine = get_email_engine()
            except ImportError:
                pass
        return self._engine
    
    def execute(
        self,
        job_title: str,
        company: str,
        job_description: str,
        follow_up_days: list = None
    ) -> Dict[str, Any]:
        """
        Generate a complete email sequence.
        
        Returns:
            Dictionary with initial email and follow-ups
        """
        engine = self._get_engine()
        
        if not engine:
            return {"error": "Smart email engine not available"}
        
        sequence = engine.generate_email_sequence(
            job_title=job_title,
            company=company,
            job_description=job_description,
            follow_up_days=follow_up_days or [3, 7, 14]
        )
        
        # Save the sequence
        engine.save_sequence(sequence)
        
        return {
            "company": company,
            "job_title": job_title,
            "initial_email": {
                "subject": sequence.initial_email.subject,
                "body": sequence.initial_email.body
            },
            "follow_ups": [
                {
                    "day": (i + 1) * 3 if not follow_up_days else follow_up_days[i],
                    "subject": fu.subject,
                    "body": fu.body
                }
                for i, fu in enumerate(sequence.follow_ups)
            ],
            "schedule": [d.strftime("%Y-%m-%d %H:%M") for d in sequence.schedule],
            "status": "Sequence saved to emails/sequences/"
        }


class ReferralRequestWriterTool(JobAgentTool):
    """
    Generate polite referral request messages.
    """
    
    def __init__(self):
        self._engine = None
        self.log = logger.bind(tool="ReferralRequestWriter")
    
    def _get_engine(self):
        if self._engine is None:
            try:
                from tools.smart_email import get_email_engine
                self._engine = get_email_engine()
            except ImportError:
                pass
        return self._engine
    
    def execute(
        self,
        contact_name: str,
        relationship: str,
        target_company: str,
        target_role: str,
        why_good_fit: str = ""
    ) -> Dict[str, Any]:
        """Generate a referral request email."""
        engine = self._get_engine()
        
        if not engine:
            return {"error": "Smart email engine not available"}
        
        draft = engine.generate_referral_request(
            contact_name=contact_name,
            relationship=relationship,
            target_company=target_company,
            target_role=target_role,
            why_good_fit=why_good_fit
        )
        
        # Save draft
        engine.save_draft(draft)
        
        return {
            "contact_name": contact_name,
            "target_company": target_company,
            "target_role": target_role,
            "email": {
                "subject": draft.subject,
                "body": draft.body
            },
            "backend": draft.backend_used,
            "generation_time": draft.generation_time
        }


class ConnectionMessageWriterTool(JobAgentTool):
    """
    Generate personalized LinkedIn connection requests.
    """
    
    def __init__(self):
        self._engine = None
        self.log = logger.bind(tool="ConnectionMessageWriter")
    
    def _get_engine(self):
        if self._engine is None:
            try:
                from tools.smart_email import get_email_engine
                self._engine = get_email_engine()
            except ImportError:
                pass
        return self._engine
    
    def execute(
        self,
        recipient_name: str,
        recipient_role: str,
        company: str,
        connection_reason: str,
        platform: str = "LinkedIn"
    ) -> Dict[str, Any]:
        """Generate a connection request message."""
        engine = self._get_engine()
        
        if not engine:
            return {"error": "Smart email engine not available"}
        
        draft = engine.generate_connection_request(
            recipient_name=recipient_name,
            recipient_role=recipient_role,
            company=company,
            connection_reason=connection_reason,
            platform=platform
        )
        
        return {
            "recipient": recipient_name,
            "company": company,
            "platform": platform,
            "message": draft.body,
            "character_count": len(draft.body),
            "backend": draft.backend_used
        }


class ThankYouEmailTool(JobAgentTool):
    """
    Generate thank-you emails after interviews.
    """
    
    def __init__(self):
        self._engine = None
        self.log = logger.bind(tool="ThankYouEmail")
    
    def _get_engine(self):
        if self._engine is None:
            try:
                from tools.smart_email import get_email_engine
                self._engine = get_email_engine()
            except ImportError:
                pass
        return self._engine
    
    def execute(
        self,
        interviewer_name: str,
        interviewer_role: str,
        company: str,
        job_title: str,
        interview_topics: list = None,
        specific_moment: str = ""
    ) -> Dict[str, Any]:
        """Generate a thank-you email."""
        engine = self._get_engine()
        
        if not engine:
            return {"error": "Smart email engine not available"}
        
        draft = engine.generate_thank_you_email(
            interviewer_name=interviewer_name,
            interviewer_role=interviewer_role,
            company=company,
            job_title=job_title,
            interview_topics=interview_topics,
            specific_moment=specific_moment
        )
        
        # Save draft
        engine.save_draft(draft)
        
        return {
            "interviewer": interviewer_name,
            "company": company,
            "email": {
                "subject": draft.subject,
                "body": draft.body
            },
            "backend": draft.backend_used,
            "generation_time": draft.generation_time
        }


# =====================================================
# REGISTRATION
# =====================================================

def register_email_tools():
    """Register all email tools with the ToolRegistry."""
    from tools.registry import ToolRegistry
    
    ToolRegistry.register_instance("draft_email", EmailDraftTool)
    ToolRegistry.register_instance("follow_up_reminder", FollowUpReminderTool)
    ToolRegistry.register_instance("cold_email_sequencer", ColdEmailSequencerTool)
    ToolRegistry.register_instance("referral_request", ReferralRequestWriterTool)
    ToolRegistry.register_instance("connection_message", ConnectionMessageWriterTool)
    ToolRegistry.register_instance("thank_you_email", ThankYouEmailTool)
