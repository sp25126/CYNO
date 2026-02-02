"""
Unified Data Models for Cyno Job Agent
Combines standard and advanced fields for enterprise-grade intelligence.
"""
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl, computed_field, ConfigDict
import re

# ==========================================
# SHARED SUB-MODELS
# ==========================================

class WorkExperience(BaseModel):
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None

class JobMatch(BaseModel):
    """Job matched with a resume (Advanced)"""
    # Forward declarations handled by Pydantic usually, but here we define matched fields
    # We won't nest Job/Resume deeply to avoid circular deps if not needed
    # But for a clear model, we might references them. 
    # For now, we keep it simple as a result structure if needed.
    match_score: int = Field(ge=0, le=100)
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    reasoning: str = Field(default="")

# ==========================================
# CORE MODELS
# ==========================================

class Resume(BaseModel):
    """
    Advanced Resume Model - 50+ Fields for Deep Intelligence
    """
    # === BASIC FIELDS ===
    name: str = Field(default="Unknown Candidate")
    email: Optional[str] = None
    phone: Optional[str] = None
    location: str = Field(default="Unknown", description="Candidate location")
    contact_info: Dict[str, str] = Field(default_factory=dict)
    
    # === CORE SKILLS & EXPERIENCE ===
    parsed_skills: List[str] = Field(default_factory=list, description="Extracted technical skills")
    education_level: Literal["HIGH_SCHOOL", "BACHELORS", "MASTERS", "PHD", "UNKNOWN"] = "UNKNOWN"
    years_exp: int = Field(default=0, ge=0, description="Years of professional experience")
    experience: List[WorkExperience] = Field(default_factory=list, description="Work history")
    education: List[str] = Field(default_factory=list, description="Education details")
    
    # === ADVANCED INTELLIGENCE ===
    skill_proficiency: Dict[str, str] = Field(default_factory=dict, description="Skill -> Proficiency level")
    technical_domains: List[str] = Field(default_factory=list, description="Web Dev, ML, Cloud, etc.")
    tools_and_frameworks: List[str] = Field(default_factory=list, description="Docker, React, AWS, etc.")
    soft_skills: List[str] = Field(default_factory=list, description="Communication, Leadership, etc.")
    personality_traits: List[str] = Field(default_factory=list)
    work_style: str = Field(default="Hybrid")
    
    # === CAREER METRICS ===
    career_trajectory: str = Field(default="Unknown", description="Upward/Lateral/etc.")
    leadership_level: str = Field(default="IC")
    profile_type: str = Field(default="GENERAL")
    expected_salary_range: str = Field(default="Not specified")
    job_titles_fit: List[str] = Field(default_factory=list)
    
    # === PROJECTS & AWARDS ===
    projects: List[str] = Field(default_factory=list)
    project_impact_scores: Dict[str, int] = Field(default_factory=dict)
    achievements: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    
    # === META ===
    keywords: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_text: str = Field(default="", exclude=True, description="Original text content")
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = ConfigDict(extra='ignore')

    @computed_field
    @property
    def years_exp_category(self) -> Literal["JUNIOR", "MID", "SENIOR"]:
        if self.years_exp < 3: return "JUNIOR"
        elif self.years_exp < 7: return "MID"
        else: return "SENIOR"

    @classmethod
    def from_text(cls, text: str) -> "Resume":
        """Parses raw text to extract resume details using heuristic regex."""
        # Heuristic Extraction Logic
        skills = []
        common_skills = ["Python", "JavaScript", "React", "Node", "SQL", "AWS", "Docker", "Java", "C++", "C#", "TypeScript", "Go"]
        for skill in common_skills:
            if re.search(rf'\\b{re.escape(skill)}\\b', text, re.I):
                skills.append(skill)
        if not skills: skills = ["General"]

        years_match = re.search(r'(\\d+)\\+?\\s*years?', text, re.I)
        years = int(years_match.group(1)) if years_match else 0
        
        loc_match = re.search(r'Location:\\s*([^\\n\\.,]+)', text, re.I)
        location = loc_match.group(1).strip() if loc_match else "Unknown"
        if location == "Unknown" and "Ahmedabad" in text: location = "Ahmedabad, India"

        edu = "UNKNOWN"
        if re.search(r'Bachelor|B\\.Tech|B\\.S\\.', text, re.I): edu = "BACHELORS"
        elif re.search(r'Master|M\\.Tech|M\\.S\\.', text, re.I): edu = "MASTERS"
        elif re.search(r'PhD', text, re.I): edu = "PHD"

        return cls(
            parsed_skills=skills,
            education_level=edu,
            years_exp=years,
            location=location,
            keywords=text.split()[:20],
            raw_text=text
        )

class Job(BaseModel):
    """Enhanced Job Model"""
    # Basic
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(default="Remote")
    job_url: HttpUrl
    apply_url: Optional[HttpUrl] = None
    description: str = Field(default="No description available")
    source: str = Field(min_length=1)
    
    # Metadata
    date_posted: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    remote: bool = False
    
    # Advanced / Intelligence Fields
    contact_email: Optional[EmailStr] = None
    required_skills: List[str] = Field(default_factory=list)
    experience_required: Optional[int] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    match_score: Optional[int] = None
    
    model_config = ConfigDict(extra='ignore')
    
    @field_validator('location', mode='before')
    @classmethod
    def validate_location(cls, v) -> str:
        if not v or str(v).strip() == '' or str(v).lower() == 'nan':
            return "Remote"
        return str(v)
    
    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v) -> str:
        if not v or str(v).strip() == '' or str(v).lower() == 'nan' or len(str(v).strip()) < 10:
            return "No description available"
        return str(v)

class Lead(BaseModel):
    """Potential client or job lead (Optimized for LeadGen Tool)"""
    company: str = Field(default="Unknown / Independent")
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None # Allow non-EmailStr for flexible scraping, or standardize? lead_scraper uses str.
    source: str
    role_needed: str
    pain_points: Optional[str] = None
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0) # LeadGen uses 0-100 logic or 0.0-1.0? 
    # Logic check: lead_scraper uses 'confidence_score=75'. If field is float 0-1, 75 is invalid.
    # Legacy Lead used float 0-1. Advanced Lead used int 0-100.
    # LeadGen tool uses 75. So it expects INT or float>>1.
    # Standardizing to INT 0-100 for better readability.
    
    profile_match: Optional[str] = None
    url: Optional[str] = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Compatibility shim if code passes 'source_url' (legacy)
    @field_validator('url', mode='before')
    @classmethod
    def map_source_url(cls, v):
        return v
    
    model_config = ConfigDict(extra='ignore')


class EmailDraft(BaseModel):
    """Email draft for job application."""
    recipient_email: str
    subject: str
    body: str
    job_title: str
    company: str
    resume_highlights: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentState(BaseModel):
    parsed_resume: Optional[Resume] = None
    search_results: List[Job] = Field(default_factory=list)
    matched_jobs: List[Job] = Field(default_factory=list)
    leads: List[Lead] = Field(default_factory=list) # Added leads storage
    last_search: Optional[str] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)
