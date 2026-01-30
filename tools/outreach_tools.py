"""
CYNO Outreach Tools
Follow-up Reminders, Cold Email Sequencer, Referral Request Writer
"""

import os
import json
import time
import structlog
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = structlog.get_logger(__name__)


@dataclass
class FollowUpItem:
    """A follow-up reminder item."""
    company: str
    job_title: str
    applied_date: str
    follow_up_dates: List[str]
    status: str = "pending"
    notes: str = ""


class FollowUpReminderTool:
    """
    Tool #14: Smart reminders for application follow-ups.
    Suggests follow-up timing at 3, 7, and 14 days.
    """
    
    def __init__(self):
        self.follow_ups: List[FollowUpItem] = []
        self.storage_path = "data/follow_ups.json"
        self._load_storage()
    
    def _load_storage(self):
        """Load follow-ups from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for item in data:
                        self.follow_ups.append(FollowUpItem(**item))
        except:
            pass
    
    def _save_storage(self):
        """Save follow-ups to storage."""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump([vars(fu) for fu in self.follow_ups], f, indent=2)
        except:
            pass
    
    def execute(
        self,
        action: str = "list",
        company: str = "",
        job_title: str = "",
        applied_date: str = ""
    ) -> Dict[str, Any]:
        """
        Manage follow-up reminders.
        
        Args:
            action: 'add', 'list', 'check', 'complete'
            company: Company name
            job_title: Job title
            applied_date: Date applied (YYYY-MM-DD)
            
        Returns:
            Follow-up status and reminders
        """
        log = logger.bind(tool="FollowUpReminder", action=action)
        log.info("managing_followups")
        
        if action == "add":
            return self._add_followup(company, job_title, applied_date)
        elif action == "list":
            return self._list_followups()
        elif action == "check":
            return self._check_due()
        elif action == "complete":
            return self._mark_complete(company)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    def _add_followup(self, company: str, job_title: str, applied_date: str) -> Dict[str, Any]:
        """Add a new follow-up reminder."""
        try:
            if not applied_date:
                applied_date = datetime.now().strftime("%Y-%m-%d")
            
            base_date = datetime.strptime(applied_date, "%Y-%m-%d")
            follow_up_dates = [
                (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                (base_date + timedelta(days=14)).strftime("%Y-%m-%d"),
            ]
            
            item = FollowUpItem(
                company=company,
                job_title=job_title,
                applied_date=applied_date,
                follow_up_dates=follow_up_dates
            )
            
            self.follow_ups.append(item)
            self._save_storage()
            
            return {
                "success": True,
                "message": f"Added follow-up for {company}",
                "follow_up_schedule": follow_up_dates,
                "tips": [
                    f"First follow-up: {follow_up_dates[0]} (3 days)",
                    f"Second follow-up: {follow_up_dates[1]} (7 days)",
                    f"Final follow-up: {follow_up_dates[2]} (14 days)"
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _list_followups(self) -> Dict[str, Any]:
        """List all follow-ups."""
        pending = [fu for fu in self.follow_ups if fu.status == "pending"]
        completed = [fu for fu in self.follow_ups if fu.status == "completed"]
        
        return {
            "success": True,
            "pending": [vars(fu) for fu in pending],
            "completed": [vars(fu) for fu in completed],
            "total_pending": len(pending),
            "total_completed": len(completed)
        }
    
    def _check_due(self) -> Dict[str, Any]:
        """Check which follow-ups are due today."""
        today = datetime.now().strftime("%Y-%m-%d")
        due_today = []
        overdue = []
        
        for fu in self.follow_ups:
            if fu.status != "pending":
                continue
                
            for date in fu.follow_up_dates:
                if date == today:
                    due_today.append({
                        "company": fu.company,
                        "job_title": fu.job_title,
                        "applied": fu.applied_date
                    })
                    break
                elif date < today:
                    overdue.append({
                        "company": fu.company,
                        "job_title": fu.job_title,
                        "due_date": date
                    })
        
        return {
            "success": True,
            "due_today": due_today,
            "overdue": overdue[:5],  # Limit overdue items
            "message": f"You have {len(due_today)} follow-ups due today!"
        }
    
    def _mark_complete(self, company: str) -> Dict[str, Any]:
        """Mark a follow-up as complete."""
        for fu in self.follow_ups:
            if fu.company.lower() == company.lower():
                fu.status = "completed"
                self._save_storage()
                return {
                    "success": True,
                    "message": f"Marked {company} as completed"
                }
        
        return {"success": False, "error": f"Company not found: {company}"}


class ColdEmailSequencerTool:
    """
    Tool #12: Schedule follow-up emails with intelligent timing.
    """
    
    def __init__(self):
        self.cloud_url = os.getenv("COLAB_SERVER_URL")
    
    def execute(
        self,
        recipient_name: str,
        company: str,
        job_title: str,
        your_name: str,
        sequence_type: str = "job_application"
    ) -> Dict[str, Any]:
        """
        Generate a cold email sequence.
        
        Args:
            recipient_name: Name of recipient
            company: Company name
            job_title: Target job title
            your_name: Your name
            sequence_type: 'job_application', 'networking', 'referral'
            
        Returns:
            Email sequence for different stages
        """
        log = logger.bind(tool="ColdEmailSequencer", company=company)
        log.info("generating_sequence")
        
        # Generate email sequence
        sequence = self._generate_sequence(
            recipient_name, company, job_title, your_name, sequence_type
        )
        
        return {
            "success": True,
            "sequence_type": sequence_type,
            "emails": sequence,
            "schedule": {
                "email_1": "Day 0 (Initial outreach)",
                "email_2": "Day 3-4 (First follow-up)",
                "email_3": "Day 7-10 (Second follow-up)"
            },
            "tips": [
                "Send emails Tuesday-Thursday for best response rates",
                "Best times: 9-10 AM or 1-2 PM recipient's timezone",
                "Always personalize with something specific about them"
            ]
        }
    
    def _generate_sequence(
        self,
        recipient: str,
        company: str,
        job_title: str,
        your_name: str,
        seq_type: str
    ) -> List[Dict[str, str]]:
        """Generate email sequence templates."""
        
        sequences = {
            "job_application": [
                {
                    "stage": "Initial Outreach",
                    "subject": f"Excited about {job_title} opportunity at {company}",
                    "body": f"""Hi {recipient},

I recently came across the {job_title} position at {company} and I'm very excited about the opportunity to contribute to your team.

With my background in [your key skill], I believe I can bring immediate value to {company}, particularly in [specific area].

Would you have 15 minutes this week to chat about how I might be able to help?

Best regards,
{your_name}"""
                },
                {
                    "stage": "First Follow-up",
                    "subject": f"Following up: {job_title} at {company}",
                    "body": f"""Hi {recipient},

I wanted to follow up on my previous email about the {job_title} role.

I recently [relevant achievement or news], which I think aligns well with what you're building at {company}.

I'd love to learn more about the team's priorities and see if there's a fit.

Best,
{your_name}"""
                },
                {
                    "stage": "Final Follow-up",
                    "subject": f"One last follow-up - {job_title}",
                    "body": f"""Hi {recipient},

I understand you're busy, so I'll keep this brief.

I'm still very interested in the {job_title} role at {company}. If the timing isn't right now, I'd be happy to reconnect in the future.

Either way, I wish you and the team all the best!

{your_name}"""
                }
            ],
            "networking": [
                {
                    "stage": "Initial Connection",
                    "subject": f"Fellow [industry] professional - would love to connect",
                    "body": f"""Hi {recipient},

I came across your profile and was impressed by your work at {company}. 

I'm currently exploring opportunities in [field] and would love to learn from your experience. Would you be open to a quick 15-minute call?

Best,
{your_name}"""
                },
                {
                    "stage": "Follow-up",
                    "subject": f"Bumping this up - would love to connect",
                    "body": f"""Hi {recipient},

Just wanted to follow up on my previous note. I'm particularly curious about [specific topic] and would value your perspective.

No worries if you're too busy - I appreciate your time either way!

{your_name}"""
                }
            ]
        }
        
        return sequences.get(seq_type, sequences["job_application"])


class ReferralRequestWriterTool:
    """
    Tool #45: Generate polite referral request messages.
    """
    
    def execute(
        self,
        contact_name: str,
        relationship: str,
        company: str,
        job_title: str,
        your_name: str
    ) -> Dict[str, Any]:
        """
        Generate a referral request message.
        
        Args:
            contact_name: Name of person you're asking
            relationship: How you know them (e.g., "former colleague", "met at conference")
            company: Target company
            job_title: Target job title
            your_name: Your name
            
        Returns:
            Referral request message
        """
        log = logger.bind(tool="ReferralRequestWriter")
        log.info("generating_referral_request")
        
        # Adjust tone based on relationship
        formality = "formal" if relationship in ["former manager", "professor", "mentor"] else "casual"
        
        if formality == "formal":
            message = f"""Dear {contact_name},

I hope this message finds you well. I wanted to reach out because I'm currently exploring new opportunities and noticed that {company} is hiring for a {job_title} position.

Given your connection to {company}, I was wondering if you might be willing to refer me for this role. I believe my experience in [key skills] aligns well with what they're looking for.

I've attached my resume for your reference. Of course, I completely understand if you're not comfortable making a referral - I appreciate your time either way.

Thank you for considering my request.

Best regards,
{your_name}"""
        else:
            message = f"""Hey {contact_name}!

Hope you're doing well! I saw that {company} is hiring for a {job_title} role and immediately thought of you.

I'm really interested in this opportunity and was wondering if you'd be open to putting in a referral for me? I know internal referrals carry a lot of weight!

Totally understand if it's not possible - just thought I'd ask since we're connected there.

Let me know if you need my resume or any other info!

Thanks so much,
{your_name}"""
        
        return {
            "success": True,
            "message": message,
            "relationship": relationship,
            "formality": formality,
            "tips": [
                "Make it easy for them - attach your resume",
                "Mention specific reasons why you're a good fit",
                "Offer to provide more information if needed",
                "Thank them regardless of outcome"
            ],
            "follow_up": "If no response in 3-4 days, send a gentle reminder"
        }


class CompanyQuestionGeneratorTool:
    """
    Tool #48: Generate smart questions to ask the interviewer.
    """
    
    def execute(
        self,
        company: str,
        job_title: str,
        interview_stage: str = "final",
        industry: str = ""
    ) -> Dict[str, Any]:
        """
        Generate intelligent questions to ask interviewers.
        
        Args:
            company: Company name
            job_title: Position you're interviewing for
            interview_stage: 'phone_screen', 'technical', 'final'
            industry: Company's industry
            
        Returns:
            List of smart questions organized by category
        """
        log = logger.bind(tool="CompanyQuestionGenerator")
        log.info("generating_questions", company=company)
        
        questions = {
            "role_specific": [
                f"What does success look like for the {job_title} role in the first 90 days?",
                "What are the biggest challenges someone in this role would face?",
                "How does this role contribute to the company's overall goals?",
                "What's the typical career path for someone in this position?"
            ],
            "team_culture": [
                "Can you tell me about the team I'd be working with?",
                "How does the team handle disagreements or different opinions?",
                "What's the work-life balance like on this team?",
                f"How has the team at {company} evolved over the past year?"
            ],
            "company_growth": [
                f"What are {company}'s biggest priorities for the next year?",
                "How does the company support professional development?",
                f"What excites you most about {company}'s future?",
                "How has the company adapted to recent industry changes?"
            ],
            "interviewer_focused": [
                "What do you enjoy most about working here?",
                "What's something you wish you knew before joining?",
                "How would you describe the management style here?",
                "What's your favorite project you've worked on recently?"
            ],
            "process": [
                "What are the next steps in the interview process?",
                "Is there anything about my background you'd like me to clarify?",
                "When can I expect to hear back about a decision?"
            ]
        }
        
        # Adjust based on interview stage
        recommended = []
        if interview_stage == "phone_screen":
            recommended = questions["role_specific"][:2] + questions["company_growth"][:1] + questions["process"]
        elif interview_stage == "technical":
            recommended = questions["role_specific"] + questions["team_culture"][:2]
        else:  # final
            recommended = questions["interviewer_focused"] + questions["company_growth"][:2] + questions["process"]
        
        return {
            "success": True,
            "company": company,
            "stage": interview_stage,
            "recommended_questions": recommended[:5],
            "all_questions": questions,
            "tips": [
                "Pick 3-5 questions to ask",
                "Listen carefully - don't repeat what was already discussed",
                "Show genuine curiosity, not just checking boxes",
                "Take notes on their answers for future reference"
            ]
        }


# Tool Registration
def register_outreach_tools():
    """Register all outreach tools."""
    from tools.registry import ToolRegistry
    
    ToolRegistry.register_instance("follow_up_reminder", FollowUpReminderTool)
    ToolRegistry.register_instance("cold_email_sequencer", ColdEmailSequencerTool)
    ToolRegistry.register_instance("referral_request_writer", ReferralRequestWriterTool)
    ToolRegistry.register_instance("company_question_generator", CompanyQuestionGeneratorTool)
