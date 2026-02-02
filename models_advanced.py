"""
Advanced data models for enterprise-grade job agent.
Includes 50+ fields for deep intelligence.
"""
from datetime import datetime, timezone
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, EmailStr, Field, field_validator, HttpUrl, computed_field, ConfigDict


class WorkExperience(BaseModel):
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None


class Lead(BaseModel):
    """Potential client or job lead"""
    company: str
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    source: str
    role_needed: str
    pain_points: Optional[str] = None
    confidence_score: int = Field(default=50, ge=0, le=100)
    profile_match: Optional[str] = None
    url: Optional[str] = None
    date_found: datetime = Field(default_factory=datetime.now)


class Resume(BaseModel):
    """
    Advanced Resume Model - 50+ Fields for Deep Intelligence
    """
    # === BASIC FIELDS ===
    parsed_skills: List[str] = Field(min_length=1, description="Technical skills")
    education_level: Literal["HIGH_SCHOOL", "BACHELORS", "MASTERS", "PHD", "UNKNOWN"] = "UNKNOWN"
    years_exp: int = Field(ge=0, description="Years of professional experience")
    location: str = Field(min_length=1, description="Candidate location")
    contact_info: Dict[str, str] = Field(default_factory=dict)
    
    # === EXPERIENCE & CAREER ===
    experience: List[WorkExperience] = Field(default_factory=list)
    career_trajectory: str = Field(default="Unknown", description="Upward, Lateral, Career Change, Early Career")
    leadership_level: str = Field(default="IC", description="IC, Lead, Manager, Senior Manager, Executive")
    
    # === ADVANCED SKILLS ===
    skill_proficiency: Dict[str, str] = Field(default_factory=dict, description="Skill -> Proficiency level")
    technical_domains: List[str] = Field(default_factory=list, description="Web Dev, ML, Cloud, etc.")
    tools_and_frameworks: List[str] = Field(default_factory=list, description="Docker, React, AWS, etc.")
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list, description="Spoken languages")
    
    # === PERSONALITY & SOFT SKILLS ===
    soft_skills: List[str] = Field(default_factory=list, description="Communication, Leadership, etc.")
    personality_traits: List[str] = Field(default_factory=list, description="Detail-oriented, Fast learner, etc.")
    work_style: str = Field(default="Hybrid", description="Independent, Collaborative, Hybrid")
    
    # === PROJECTS & ACHIEVEMENTS ===
    projects: List[str] = Field(default_factory=list, description="Notable projects")
    project_impact_scores: Dict[str, int] = Field(default_factory=dict, description="Project -> Impact (0-100)")
    achievements: List[str] = Field(default_factory=list, description="Quantified achievements")
    
    # === CAREER INTELLIGENCE ===
    profile_type: str = Field(default="GENERAL", description="AI_ML_ENGINEER, FULL_STACK_DEV, etc.")
    expected_salary_range: str = Field(default="Not specified")
    job_titles_fit: List[str] = Field(default_factory=list, description="Suggested job titles")
    
    # === META ===
    summary: Optional[str] = None
    raw_text: str = Field(exclude=True, description="Original text")
    parsed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    model_config = ConfigDict(extra='ignore')


class Job(BaseModel):
    """Enhanced Job with intelligence fields"""
    # Basic fields
    title: str
    company: str
    location: str
    job_url: HttpUrl
    apply_url: Optional[HttpUrl] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    source: Optional[str] = None
    date_posted: Optional[str] = None
    
    # Enhanced fields
    contact_email: Optional[EmailStr] = None
    required_skills: List[str] = Field(default_factory=list)
    experience_required: Optional[int] = None
    remote_friendly: bool = Field(default=False)
    company_size: Optional[str] = None  # Startup, Mid-size, Enterprise
    industry: Optional[str] = None
    
    # Intelligence scores
    match_score: Optional[int] = None  # 0-100
    salary_competitiveness: Optional[str] = None  # Below Market, Market Rate, Above Market
    
    model_config = ConfigDict(extra='ignore')


class JobMatch(BaseModel):
    """Job matched with a resume"""
    job: Job
    resume: Resume
    match_score: int = Field(ge=0, le=100)
    matching_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    salary_alignment: str = Field(default="Unknown")
    recommendation: str = Field(default="Review")  # Apply Now, Review, Skip
    reasoning: str = Field(default="")
