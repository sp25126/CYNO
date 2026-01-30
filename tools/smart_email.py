"""
CYNO Smart Email Suite - Advanced Personalized Email Generation
Implements ideas from CYNO_IDEAS.md:
- EmailDrafter with deep personalization
- ColdEmailSequencer with intelligent timing
- ConnectionMessageWriter for LinkedIn
- FollowUpReminder with smart scheduling
- ReferralRequestWriter with context
"""

import os
import re
import json
import structlog
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = structlog.get_logger(__name__)


# =====================================================
# DATA MODELS
# =====================================================

class EmailTone(Enum):
    """Email tone options."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    ENTHUSIASTIC = "enthusiastic"
    FORMAL = "formal"
    CASUAL = "casual"


class EmailType(Enum):
    """Types of emails we can generate."""
    APPLICATION = "application"
    FOLLOW_UP = "follow_up"
    COLD_OUTREACH = "cold_outreach"
    REFERRAL_REQUEST = "referral_request"
    CONNECTION_REQUEST = "connection_request"
    THANK_YOU = "thank_you"
    NETWORKING = "networking"


@dataclass
class UserPersonalization:
    """User's personalization preferences."""
    # Basic Info
    name: str = ""
    email: str = ""
    phone: str = ""
    
    # Professional Identity
    title: str = ""  # e.g., "Senior Machine Learning Engineer"
    years_experience: int = 0
    summary: str = ""  # Personal pitch
    
    # Signature style
    signature: str = ""  # Custom email signature
    preferred_greeting: str = "Hi"  # Hi, Hello, Dear, etc.
    preferred_closing: str = "Best regards"
    
    # Style preferences
    preferred_tone: EmailTone = EmailTone.PROFESSIONAL
    include_linkedin: bool = True
    include_portfolio: bool = True
    include_phone: bool = False
    
    # Links
    linkedin_url: str = ""
    portfolio_url: str = ""
    github_url: str = ""
    
    # Skills & Achievements to highlight
    top_skills: List[str] = field(default_factory=list)
    notable_achievements: List[str] = field(default_factory=list)
    project_highlights: List[Dict] = field(default_factory=list)
    
    # Communication style
    style_keywords: List[str] = field(default_factory=lambda: [
        "results-driven", "passionate", "collaborative"
    ])
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['preferred_tone'] = self.preferred_tone.value
        return result
    
    @classmethod
    def from_resume(cls, resume_data: Dict) -> 'UserPersonalization':
        """Create personalization from parsed resume."""
        return cls(
            name=resume_data.get('name', ''),
            email=resume_data.get('email', ''),
            phone=resume_data.get('phone', ''),
            years_experience=resume_data.get('years_exp', 0),
            top_skills=resume_data.get('parsed_skills', [])[:10],
            notable_achievements=resume_data.get('achievements', [])[:5],
            project_highlights=resume_data.get('projects', [])[:3],
            linkedin_url=resume_data.get('linkedin', ''),
            github_url=resume_data.get('github', ''),
            summary=resume_data.get('summary', '')
        )


@dataclass
class EmailDraft:
    """Enhanced email draft with metadata."""
    subject: str
    body: str
    recipient_email: str = ""
    recipient_name: str = ""
    email_type: EmailType = EmailType.APPLICATION
    company: str = ""
    job_title: str = ""
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    backend_used: str = ""
    generation_time: float = 0.0
    
    # Follow-up tracking
    follow_up_dates: List[datetime] = field(default_factory=list)
    is_sent: bool = False
    response_received: bool = False


@dataclass
class EmailSequence:
    """A sequence of follow-up emails."""
    initial_email: EmailDraft
    follow_ups: List[EmailDraft] = field(default_factory=list)
    schedule: List[datetime] = field(default_factory=list)
    company: str = ""
    status: str = "pending"  # pending, in_progress, completed


# =====================================================
# SMART EMAIL ENGINE
# =====================================================

class SmartEmailEngine:
    """
    AI-powered email generation engine with deep personalization.
    Uses EnhancedCloudClient (Cloud GPU or Local Ollama).
    """
    
    def __init__(self, user_prefs: Optional[UserPersonalization] = None):
        self._client = None
        self.user_prefs = user_prefs or UserPersonalization()
        self.log = logger.bind(engine="SmartEmail")
    
    def _get_client(self):
        """Lazy load enhanced cloud client."""
        if self._client is None:
            try:
                from cloud.enhanced_client import get_cloud_client
                self._client = get_cloud_client()
            except ImportError:
                self.log.warning("enhanced_client_not_available")
        return self._client
    
    def set_personalization(self, prefs: UserPersonalization):
        """Set user personalization preferences."""
        self.user_prefs = prefs
        self.log.info("personalization_set", name=prefs.name)
    
    def load_personalization_from_file(self, filepath: str = "data/user_prefs.json"):
        """Load personalization from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.user_prefs = UserPersonalization(**data)
                self.log.info("personalization_loaded", file=filepath)
        except FileNotFoundError:
            self.log.warning("personalization_file_not_found", file=filepath)
        except Exception as e:
            self.log.error("personalization_load_failed", error=str(e))
    
    def save_personalization_to_file(self, filepath: str = "data/user_prefs.json"):
        """Save personalization to a JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(self.user_prefs.to_dict(), f, indent=2)
        self.log.info("personalization_saved", file=filepath)
    
    # =====================================================
    # CORE EMAIL GENERATION
    # =====================================================
    
    def generate_application_email(
        self,
        job_title: str,
        company: str,
        job_description: str,
        resume_highlights: List[str] = None,
        company_research: Dict = None,
        custom_hook: str = None
    ) -> EmailDraft:
        """
        Generate a personalized job application email.
        
        Args:
            job_title: Target job title
            company: Company name
            job_description: Full job description
            resume_highlights: Specific skills/experiences to highlight
            company_research: Research about the company (from CompanyStalker)
            custom_hook: Custom opening hook
        
        Returns:
            EmailDraft with personalized content
        """
        self.log.info("generating_application_email", 
                     company=company, 
                     job=job_title)
        
        # Build context
        highlights = resume_highlights or self.user_prefs.top_skills[:5]
        
        # Company insights
        company_context = ""
        if company_research:
            company_context = f"""
COMPANY INSIGHTS (for personalization):
- Culture: {company_research.get('culture', 'N/A')}
- Tech Stack: {company_research.get('tech_stack', [])}
- Recent News: {company_research.get('recent_news', 'N/A')}
- Company Size: {company_research.get('size', 'N/A')}
"""
        
        # Hook
        hook_instruction = ""
        if custom_hook:
            hook_instruction = f"\nOPENING HOOK: Start with: \"{custom_hook}\"\n"
        
        prompt = self._build_application_prompt(
            job_title=job_title,
            company=company,
            job_description=job_description,
            highlights=highlights,
            company_context=company_context,
            hook_instruction=hook_instruction
        )
        
        return self._generate_email(
            prompt=prompt,
            email_type=EmailType.APPLICATION,
            company=company,
            job_title=job_title,
            subject_template=f"Application: {job_title} at {company}"
        )
    
    def generate_follow_up_email(
        self,
        original_email: EmailDraft,
        days_since: int,
        follow_up_number: int = 1
    ) -> EmailDraft:
        """
        Generate a follow-up email based on an original application.
        
        Args:
            original_email: The original email that was sent
            days_since: Days since the original email
            follow_up_number: 1st, 2nd, or 3rd follow-up
        """
        self.log.info("generating_follow_up", 
                     company=original_email.company,
                     follow_up_num=follow_up_number)
        
        # Different tones for different follow-ups
        tone_guidance = {
            1: "Be polite and express continued interest. Brief and respectful.",
            2: "Slightly more direct. Mention you're still very interested and provide an update if any.",
            3: "Final follow-up. Be appreciative of their time, ask for any feedback, keep door open."
        }
        
        prompt = f"""Generate a professional follow-up email.

USER INFO:
- Name: {self.user_prefs.name or 'Candidate'}
- Email: {self.user_prefs.email}
- Preferred Closing: {self.user_prefs.preferred_closing}

ORIGINAL APPLICATION:
- Company: {original_email.company}
- Position: {original_email.job_title}
- Days Since Original: {days_since}
- Follow-up Number: {follow_up_number}

TONE GUIDANCE: {tone_guidance.get(follow_up_number, tone_guidance[1])}

FOLLOW-UP EMAIL RULES:
1. Keep it SHORT (3-5 sentences max)
2. Reference the original application date
3. Express continued interest
4. Offer to provide more information
5. End with a clear but soft call-to-action
6. Do NOT be pushy or aggressive
7. Include subject line

FORMAT:
Subject: [Subject Line]

[Email Body]

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}
"""
        
        return self._generate_email(
            prompt=prompt,
            email_type=EmailType.FOLLOW_UP,
            company=original_email.company,
            job_title=original_email.job_title,
            subject_template=f"Following Up: {original_email.job_title} Application"
        )
    
    def generate_cold_outreach_email(
        self,
        recipient_name: str,
        recipient_role: str,
        company: str,
        connection_reason: str,
        ask: str = "coffee chat"
    ) -> EmailDraft:
        """
        Generate a cold outreach email for networking.
        
        Args:
            recipient_name: Name of the person to contact
            recipient_role: Their role at the company
            company: Target company
            connection_reason: Why you're reaching out (shared interest, referral, etc.)
            ask: What you're asking for (coffee chat, referral, advice)
        """
        self.log.info("generating_cold_outreach", 
                     recipient=recipient_name,
                     company=company)
        
        prompt = f"""Generate a cold outreach email for networking.

SENDER INFO:
- Name: {self.user_prefs.name or 'Candidate'}
- Title: {self.user_prefs.title or 'Software Engineer'}
- Background: {self.user_prefs.summary or f'{self.user_prefs.years_experience} years of experience'}
- Top Skills: {', '.join(self.user_prefs.top_skills[:5])}

RECIPIENT INFO:
- Name: {recipient_name}
- Role: {recipient_role}
- Company: {company}

CONNECTION REASON: {connection_reason}

THE ASK: {ask}

COLD EMAIL RULES:
1. Keep it SHORT (under 150 words)
2. Personalize the opening (show you did research)
3. Establish credibility briefly
4. Make the ask clear and easy to accept
5. Respect their time
6. Use a casual but professional tone
7. Include a specific, easy next step

FORMAT:
Subject: [Catchy but professional subject]

{self.user_prefs.preferred_greeting} {recipient_name.split()[0]},

[Email body]

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}
"""
        
        return self._generate_email(
            prompt=prompt,
            email_type=EmailType.COLD_OUTREACH,
            company=company,
            job_title="",
            subject_template=f"Quick question from a fellow {self.user_prefs.title or 'engineer'}"
        )
    
    def generate_referral_request(
        self,
        contact_name: str,
        relationship: str,
        target_company: str,
        target_role: str,
        why_good_fit: str = ""
    ) -> EmailDraft:
        """
        Generate a polite referral request email.
        
        Args:
            contact_name: Name of your contact
            relationship: How you know them (former colleague, university, etc.)
            target_company: Company you want referral to
            target_role: Role you're interested in
            why_good_fit: Why you're a good fit for this role
        """
        self.log.info("generating_referral_request",
                     contact=contact_name,
                     company=target_company)
        
        # Build fit statement
        fit_statement = why_good_fit or f"""
With {self.user_prefs.years_experience} years of experience in {', '.join(self.user_prefs.top_skills[:3])}, 
I believe I'd be a strong fit for this role.
"""
        
        prompt = f"""Generate a referral request email.

SENDER INFO:
- Name: {self.user_prefs.name or 'Candidate'}
- Experience: {self.user_prefs.years_experience} years
- Key Skills: {', '.join(self.user_prefs.top_skills[:5])}
- Notable Achievements: {self.user_prefs.notable_achievements[:2] if self.user_prefs.notable_achievements else 'Various'}

CONTACT INFO:
- Name: {contact_name}
- Relationship: {relationship}

TARGET:
- Company: {target_company}
- Role: {target_role}

FIT STATEMENT: {fit_statement}

REFERRAL REQUEST RULES:
1. Start by acknowledging your relationship
2. Be specific about what role you're asking about
3. Make it EASY for them to refer you (attach resume, key points)
4. Show you've done your research
5. Don't be pushy - make it okay to say no
6. Keep it concise
7. Offer to provide more information

FORMAT:
Subject: [Warm, personal subject line]

{self.user_prefs.preferred_greeting} {contact_name.split()[0]},

[Email body - 3-4 paragraphs max]

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}
"""
        
        return self._generate_email(
            prompt=prompt,
            email_type=EmailType.REFERRAL_REQUEST,
            company=target_company,
            job_title=target_role,
            subject_template=f"Quick Ask - {target_company} {target_role}"
        )
    
    def generate_connection_request(
        self,
        recipient_name: str,
        recipient_role: str,
        company: str,
        connection_reason: str,
        platform: str = "LinkedIn"
    ) -> EmailDraft:
        """
        Generate a LinkedIn connection request message.
        
        Args:
            recipient_name: Name of the person
            recipient_role: Their role
            company: Their company
            connection_reason: Why you want to connect
            platform: Platform (LinkedIn, Twitter, etc.)
        """
        self.log.info("generating_connection_request",
                     recipient=recipient_name,
                     platform=platform)
        
        # LinkedIn has 300 character limit
        char_limit = 300 if platform == "LinkedIn" else 500
        
        prompt = f"""Generate a LinkedIn/professional connection request message.

SENDER INFO:
- Name: {self.user_prefs.name or 'Candidate'}
- Title: {self.user_prefs.title or 'Software Engineer'}

RECIPIENT INFO:
- Name: {recipient_name}
- Role: {recipient_role}
- Company: {company}

CONNECTION REASON: {connection_reason}

PLATFORM: {platform}
CHARACTER LIMIT: {char_limit} characters (this is crucial!)

CONNECTION REQUEST RULES:
1. Keep it VERY short ({char_limit} chars max)
2. Personalize - mention something specific
3. Be genuine, not salesy
4. Don't ask for anything in the first message
5. Make it interesting enough to accept
6. No generic "I'd like to add you to my network"

MESSAGE (MUST be under {char_limit} characters):"""
        
        result = self._generate_email(
            prompt=prompt,
            email_type=EmailType.CONNECTION_REQUEST,
            company=company,
            job_title="",
            subject_template=""
        )
        
        # Truncate if needed
        if len(result.body) > char_limit:
            result.body = result.body[:char_limit-3] + "..."
        
        return result
    
    def generate_thank_you_email(
        self,
        interviewer_name: str,
        interviewer_role: str,
        company: str,
        job_title: str,
        interview_topics: List[str] = None,
        specific_moment: str = ""
    ) -> EmailDraft:
        """
        Generate a thank-you email after an interview.
        
        Args:
            interviewer_name: Name of the interviewer
            interviewer_role: Their role
            company: Company name
            job_title: Position interviewed for
            interview_topics: Key topics discussed
            specific_moment: A specific moment to reference
        """
        self.log.info("generating_thank_you",
                     interviewer=interviewer_name,
                     company=company)
        
        topics = interview_topics or ["the role", "the team", "company culture"]
        
        prompt = f"""Generate a thank-you email after a job interview.

SENDER INFO:
- Name: {self.user_prefs.name or 'Candidate'}
- Preferred Closing: {self.user_prefs.preferred_closing}

INTERVIEW INFO:
- Company: {company}
- Position: {job_title}
- Interviewer: {interviewer_name} ({interviewer_role})
- Topics Discussed: {', '.join(topics)}
- Specific Moment to Reference: {specific_moment or 'General discussion'}

THANK YOU EMAIL RULES:
1. Send within 24 hours of interview
2. Express genuine gratitude
3. Reference something SPECIFIC from the conversation
4. Reinforce your interest and fit
5. Keep it brief (under 200 words)
6. Professional but warm tone
7. Open door for next steps

FORMAT:
Subject: [Thank you subject line]

{self.user_prefs.preferred_greeting} {interviewer_name.split()[0]},

[Email body]

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}
"""
        
        return self._generate_email(
            prompt=prompt,
            email_type=EmailType.THANK_YOU,
            company=company,
            job_title=job_title,
            subject_template=f"Thank You - {job_title} Interview"
        )
    
    # =====================================================
    # EMAIL SEQUENCE GENERATION
    # =====================================================
    
    def generate_email_sequence(
        self,
        job_title: str,
        company: str,
        job_description: str,
        follow_up_days: List[int] = None
    ) -> EmailSequence:
        """
        Generate a complete email sequence: initial + follow-ups.
        
        Args:
            job_title: Target job title
            company: Company name
            job_description: Full job description
            follow_up_days: Days for follow-ups (default: [3, 7, 14])
        
        Returns:
            EmailSequence with initial email and follow-ups
        """
        self.log.info("generating_email_sequence", 
                     company=company,
                     job=job_title)
        
        follow_up_days = follow_up_days or [3, 7, 14]
        
        # Generate initial application email
        initial_email = self.generate_application_email(
            job_title=job_title,
            company=company,
            job_description=job_description
        )
        
        # Generate follow-up emails
        follow_ups = []
        for i, days in enumerate(follow_up_days):
            follow_up = self.generate_follow_up_email(
                original_email=initial_email,
                days_since=days,
                follow_up_number=i + 1
            )
            follow_up.follow_up_dates.append(
                datetime.now() + timedelta(days=days)
            )
            follow_ups.append(follow_up)
        
        # Build schedule
        schedule = [datetime.now()]  # Initial email
        for days in follow_up_days:
            schedule.append(datetime.now() + timedelta(days=days))
        
        return EmailSequence(
            initial_email=initial_email,
            follow_ups=follow_ups,
            schedule=schedule,
            company=company,
            status="pending"
        )
    
    # =====================================================
    # INTERNAL METHODS
    # =====================================================
    
    def _build_application_prompt(
        self,
        job_title: str,
        company: str,
        job_description: str,
        highlights: List[str],
        company_context: str,
        hook_instruction: str
    ) -> str:
        """Build the application email prompt."""
        
        # Build signature
        signature_links = []
        if self.user_prefs.include_linkedin and self.user_prefs.linkedin_url:
            signature_links.append(f"LinkedIn: {self.user_prefs.linkedin_url}")
        if self.user_prefs.include_portfolio and self.user_prefs.portfolio_url:
            signature_links.append(f"Portfolio: {self.user_prefs.portfolio_url}")
        if self.user_prefs.github_url:
            signature_links.append(f"GitHub: {self.user_prefs.github_url}")
        if self.user_prefs.include_phone and self.user_prefs.phone:
            signature_links.append(f"Phone: {self.user_prefs.phone}")
        
        signature = self.user_prefs.signature or f"""
{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}
{self.user_prefs.email}
{chr(10).join(signature_links)}
"""
        
        # Style keywords for tone
        style_words = ', '.join(self.user_prefs.style_keywords[:3])
        
        # Project highlights
        project_text = ""
        if self.user_prefs.project_highlights:
            project_text = "\n".join([
                f"- {p.get('name', 'Project')}: {p.get('description', '')[:100]}"
                for p in self.user_prefs.project_highlights[:2]
            ])
        
        return f"""Generate a compelling job application email.

CANDIDATE PROFILE:
- Name: {self.user_prefs.name or 'Candidate'}
- Title: {self.user_prefs.title or 'Software Professional'}
- Experience: {self.user_prefs.years_experience} years
- Key Skills: {', '.join(highlights)}
- Writing Style: {style_words}
- Summary: {self.user_prefs.summary or 'Experienced professional'}

PROJECT HIGHLIGHTS:
{project_text or 'Various projects in relevant technologies'}

NOTABLE ACHIEVEMENTS:
{chr(10).join([f'- {a}' for a in self.user_prefs.notable_achievements[:3]]) if self.user_prefs.notable_achievements else '- Multiple successful projects delivered'}

{company_context}

TARGET JOB:
- Position: {job_title}
- Company: {company}
- Description (first 500 chars): {job_description[:500]}

{hook_instruction}

EMAIL REQUIREMENTS:
1. Subject line that stands out
2. Opening that grabs attention (no generic "I am writing to...")
3. 2-3 body paragraphs connecting MY experience to THEIR needs
4. Specific skills matched to job requirements
5. Express genuine interest in the company (use company insights if available)
6. Clear but not pushy call-to-action
7. Keep under 250 words
8. Tone: {self.user_prefs.preferred_tone.value}

SIGNATURE TO USE:
{signature}

FORMAT:
Subject: [Compelling subject line]

[Email Body]

[Signature]
"""
    
    def _generate_email(
        self,
        prompt: str,
        email_type: EmailType,
        company: str,
        job_title: str,
        subject_template: str
    ) -> EmailDraft:
        """Core email generation using LLM."""
        client = self._get_client()
        
        if client:
            try:
                result = client.generate_text(
                    prompt=prompt,
                    max_tokens=600,
                    temperature=0.4
                )
                
                if result.success:
                    text = result.result
                    subject, body = self._parse_email_output(text, subject_template)
                    
                    self.log.info("email_generated",
                                 type=email_type.value,
                                 backend=result.backend,
                                 time=result.time_seconds)
                    
                    return EmailDraft(
                        subject=subject,
                        body=body,
                        email_type=email_type,
                        company=company,
                        job_title=job_title,
                        backend_used=result.backend,
                        generation_time=result.time_seconds
                    )
            except Exception as e:
                self.log.warning("generation_failed", error=str(e))
        
        # Fallback to template
        return self._generate_template_email(
            email_type=email_type,
            company=company,
            job_title=job_title,
            subject_template=subject_template
        )
    
    def _parse_email_output(self, text: str, fallback_subject: str) -> tuple:
        """Parse generated text into subject and body."""
        subject = fallback_subject
        body = text
        
        # Try to extract subject
        lines = text.strip().split('\n')
        for i, line in enumerate(lines):
            if line.lower().startswith('subject:'):
                subject = line.split(':', 1)[1].strip()
                body = '\n'.join(lines[i+1:]).strip()
                break
        
        # Clean up body
        body = re.sub(r'^\s*\n', '', body)  # Remove leading empty lines
        
        return subject, body
    
    def _generate_template_email(
        self,
        email_type: EmailType,
        company: str,
        job_title: str,
        subject_template: str
    ) -> EmailDraft:
        """Generate a basic template email as fallback."""
        
        templates = {
            EmailType.APPLICATION: f"""Dear Hiring Team,

I am writing to express my strong interest in the {job_title} position at {company}.

With {self.user_prefs.years_experience} years of experience in {', '.join(self.user_prefs.top_skills[:3])}, I am confident in my ability to contribute meaningfully to your team.

I would welcome the opportunity to discuss how my background aligns with your needs.

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}""",
            
            EmailType.FOLLOW_UP: f"""Dear Hiring Team,

I wanted to follow up on my application for the {job_title} position.

I remain very interested in this opportunity and would appreciate any update on the status of my application.

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}""",
            
            EmailType.THANK_YOU: f"""Dear [Interviewer],

Thank you for taking the time to speak with me about the {job_title} position.

I enjoyed learning more about the role and the team at {company}. I am very excited about this opportunity.

{self.user_prefs.preferred_closing},
{self.user_prefs.name or '[Your Name]'}"""
        }
        
        body = templates.get(email_type, templates[EmailType.APPLICATION])
        
        return EmailDraft(
            subject=subject_template,
            body=body,
            email_type=email_type,
            company=company,
            job_title=job_title,
            backend_used="template",
            generation_time=0.0
        )
    
    # =====================================================
    # UTILITY METHODS
    # =====================================================
    
    def save_draft(self, draft: EmailDraft, folder: str = "emails"):
        """Save an email draft to file."""
        Path(folder).mkdir(exist_ok=True)
        
        safe_company = re.sub(r'[^a-zA-Z0-9]', '_', draft.company or "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{draft.email_type.value}_{safe_company}_{timestamp}.txt"
        
        filepath = Path(folder) / filename
        
        content = f"""EMAIL TYPE: {draft.email_type.value}
COMPANY: {draft.company}
POSITION: {draft.job_title}
RECIPIENT: {draft.recipient_email or 'N/A'}
GENERATED: {draft.created_at.strftime('%Y-%m-%d %H:%M:%S')}
BACKEND: {draft.backend_used}
TIME: {draft.generation_time:.2f}s
{'='*60}

SUBJECT: {draft.subject}

{'='*60}

{draft.body}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.log.info("draft_saved", path=str(filepath))
        return filepath
    
    def save_sequence(self, sequence: EmailSequence, folder: str = "emails/sequences"):
        """Save an email sequence to files."""
        Path(folder).mkdir(parents=True, exist_ok=True)
        
        safe_company = re.sub(r'[^a-zA-Z0-9]', '_', sequence.company or "unknown")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sequence_folder = Path(folder) / f"{safe_company}_{timestamp}"
        sequence_folder.mkdir(exist_ok=True)
        
        # Save initial email
        self.save_draft(sequence.initial_email, str(sequence_folder))
        
        # Save follow-ups
        for i, follow_up in enumerate(sequence.follow_ups):
            follow_up_folder = sequence_folder / f"follow_up_{i+1}"
            follow_up_folder.mkdir(exist_ok=True)
            self.save_draft(follow_up, str(follow_up_folder))
        
        # Save schedule
        schedule_file = sequence_folder / "schedule.json"
        schedule_data = {
            "company": sequence.company,
            "status": sequence.status,
            "schedule": [d.isoformat() for d in sequence.schedule]
        }
        with open(schedule_file, 'w') as f:
            json.dump(schedule_data, f, indent=2)
        
        self.log.info("sequence_saved", path=str(sequence_folder))
        return sequence_folder


# =====================================================
# SINGLETON AND CONVENIENCE FUNCTIONS
# =====================================================

_engine_instance = None

def get_email_engine(user_prefs: Optional[UserPersonalization] = None) -> SmartEmailEngine:
    """Get or create the email engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SmartEmailEngine(user_prefs)
    elif user_prefs:
        _engine_instance.set_personalization(user_prefs)
    return _engine_instance


def quick_application_email(
    job_title: str,
    company: str,
    job_description: str,
    resume_data: Dict = None
) -> str:
    """Quick one-liner for application email."""
    engine = get_email_engine()
    if resume_data:
        prefs = UserPersonalization.from_resume(resume_data)
        engine.set_personalization(prefs)
    
    draft = engine.generate_application_email(
        job_title=job_title,
        company=company,
        job_description=job_description
    )
    return f"Subject: {draft.subject}\n\n{draft.body}"


def quick_follow_up(company: str, job_title: str, days_since: int = 3) -> str:
    """Quick follow-up email."""
    engine = get_email_engine()
    original = EmailDraft(
        subject=f"Application for {job_title}",
        body="",
        company=company,
        job_title=job_title
    )
    draft = engine.generate_follow_up_email(original, days_since)
    return f"Subject: {draft.subject}\n\n{draft.body}"


def quick_referral_request(
    contact_name: str,
    relationship: str,
    target_company: str,
    target_role: str
) -> str:
    """Quick referral request."""
    engine = get_email_engine()
    draft = engine.generate_referral_request(
        contact_name=contact_name,
        relationship=relationship,
        target_company=target_company,
        target_role=target_role
    )
    return f"Subject: {draft.subject}\n\n{draft.body}"
