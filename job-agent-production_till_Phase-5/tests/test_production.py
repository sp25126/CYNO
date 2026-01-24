import pytest
from pydantic import ValidationError
from pathlib import Path
import sys
import os
import json

# Ensure models can be imported
sys.path.append(os.getcwd())
from models import Resume, Job, Session, EmailDraft

def test_resume_valid_parsing():
    """Test Case 1: Load a real resume text, parse it, assert fields are extracted."""
    resume_path = Path("acceptance_tests/resume_samples/resume_1.txt")
    if not resume_path.exists():
        pytest.fail("Resume sample not found")
    
    text = resume_path.read_text()
    resume = Resume.from_text(text)
    
    assert "Python" in resume.parsed_skills
    assert resume.years_exp >= 0
    assert resume.location == "Ahmedabad" or "Ahmedabad" in resume.location
    assert resume.education_level == "BACHELORS"

def test_resume_invalid_years():
    """Test Case 2: Pass negative years, expect ValidationError."""
    with pytest.raises(ValidationError):
        Resume(
            parsed_skills=["Python"],
            education_level="BACHELORS",
            years_exp=-5, # Invalid
            location="Remote",
            keywords=[],
            raw_text="Test"
        )

def test_job_url_validation():
    """Test Case 3: Pass invalid URLs, expect ValidationError."""
    with pytest.raises(ValidationError):
        Job(
            title="Dev",
            company="Corp",
            location="Remote",
            job_url="invalid-url", # Invalid
            apply_url="https://valid.com",
            description="Short but valid length description.",
            source="Test"
        )

def test_session_message_persistence():
    """Test Case 4: Add 5 messages, serialize to dict, deserialize, assert consistency."""
    session = Session(session_id="s123", user_id="u456")
    for i in range(5):
        session.add_message("user", f"Message {i}")
    
    data = session.to_dict()
    assert len(data["messages"]) == 5
    
    new_session = Session.model_validate(data)
    assert new_session.session_id == "s123"
    assert len(new_session.messages) == 5
    assert new_session.messages[0]["content"] == "Message 0"

def test_email_draft_sanitization():
    """Test Case 5: Pass XSS payload in subject, expect cleaned output."""
    draft = EmailDraft(
        job_id="j123",
        recipient="test@example.com",
        subject="Hello <script>alert('xss')</script> World",
        body="Normal body",
        status="DRAFT"
    )
    # Sanitizer strips tags and their content (as implemented in models.py)
    assert "<script>" not in draft.subject
    assert "alert" not in draft.subject
    assert "Hello  World" in draft.subject

def test_resume_empty_location():
    """Additional Test: Ensure empty location raises error."""
    with pytest.raises(ValidationError):
        Resume(
            parsed_skills=["Python"],
            years_exp=2,
            location="", # Invalid
            raw_text="Test"
        )
