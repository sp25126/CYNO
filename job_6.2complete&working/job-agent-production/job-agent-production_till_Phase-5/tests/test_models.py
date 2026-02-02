import pytest
import json
from pydantic import ValidationError
from models import Resume, Job, Session, EmailDraft

# --- Resume Tests ---

def test_resume_valid_creation():
    """Test creating a valid Resume checks computed fields."""
    resume = Resume(
        parsed_skills=["Python", "AI"],
        education_level="BACHELORS",
        years_exp=4,
        experience=[],
        location="Remote",
        raw_text="Test resume content"
    )
    assert resume.years_exp_category == "MID"
    assert "Python" in resume.parsed_skills
    assert resume.education_level == "BACHELORS"

def test_resume_years_exp_category_boundary():
    """Test years_exp_category boundaries."""
    # Junior < 3
    r_jr = Resume(parsed_skills=["A"], years_exp=0, location="Loc", raw_text="t")
    assert r_jr.years_exp_category == "JUNIOR"
    
    # Mid < 7
    r_mid = Resume(parsed_skills=["A"], years_exp=3, location="Loc", raw_text="t")
    assert r_mid.years_exp_category == "MID"
    
    # Senior >= 7
    r_sr = Resume(parsed_skills=["A"], years_exp=7, location="Loc", raw_text="t")
    assert r_sr.years_exp_category == "SENIOR"

def test_resume_invalid_years_exp():
    """Test negative years_exp raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        Resume(
            parsed_skills=["Python"],
            years_exp=-1,
            location="Remote",
            raw_text="Test"
        )
    assert "Input should be greater than or equal to 0" in str(excinfo.value)

def test_resume_empty_location():
    """Test empty location raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        Resume(
            parsed_skills=["Python"],
            years_exp=5,
            location="   ", # Whitespace only
            raw_text="Test"
        )
    assert "Location cannot be empty" in str(excinfo.value)

# --- Job Tests ---

def test_job_valid_creation():
    """Test valid job creation."""
    job = Job(
        title="Dev",
        company="Co",
        location="Remote",
        job_url="https://example.com/job",
        apply_url="https://example.com/apply",
        description="A cool job description.",
        source="Test"
    )
    assert str(job.job_url) == "https://example.com/job" # Pydantic v2 keeps it as is if path present
    assert job.title == "Dev"

def test_job_invalid_url():
    """Test invalid URL raises ValidationError."""
    with pytest.raises(ValidationError) as excinfo:
        Job(
            title="Dev",
            company="Co",
            location="Remote",
            job_url="not-a-url",
            apply_url="https://example.com",
            description="Desc",
            source="Test"
        )
    # Pydantic v2 URL error message usually contains "Input should be a valid URL"
    assert "Input should be a valid URL" in str(excinfo.value) or "url" in str(excinfo.value)

# --- Session Tests ---

def test_session_message_persistence():
    """Test appending messages and serialization."""
    session = Session(session_id="s1", user_id="u1")
    session.add_message("user", "Hello")
    session.add_message("assistant", "Hi there")
    
    assert len(session.messages) == 2
    assert session.messages[0]["content"] == "Hello"
    
    # Serialization
    data = session.model_dump()
    assert data["session_id"] == "s1"
    assert len(data["messages"]) == 2
    
    # Load
    session_loaded = Session.model_validate(data)
    assert session_loaded.session_id == "s1"
    assert session_loaded.messages[1]["content"] == "Hi there"

# --- EmailDraft Tests ---

def test_email_draft_sanitization():
    """Test XSS sanitization in EmailDraft."""
    dirty_subject = "Hello <script>alert(1)</script>"
    dirty_body = "Click <a href='bad'>here</a> <script>evil()</script>"
    
    draft = EmailDraft(
        job_id="j1",
        recipient="test@example.com",
        subject=dirty_subject,
        body=dirty_body
    )
    
    # Check subject (script removed)
    assert "<script>" not in draft.subject
    assert "alert(1)" in draft.subject or "Hello" in draft.subject # Text might remain depending on regex
    # Our regex was: re.sub(r'<script.*?>.*?</script>', '', v, flags=re.I | re.S) -> removes content too
    # Then re.sub(r'<.*?>', '', v) -> strips tags
    
    assert draft.subject == "Hello " # Script tag and content removed
    
    # Check body
    # <script>evil()</script> removed completely
    # <a href='bad'>here</a> -> 'here' (tags stripped)
    assert "evil()" not in draft.body
    assert "here" in draft.body
    assert "<a" not in draft.body
