import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import EmailDraft

def test_email_draft_valid_creation():
    """Test creating valid email draft."""
    draft = EmailDraft(
        id="draft-123",
        job_id="job-456",
        recipient="hiring@company.com",
        subject="Application: Python Developer",
        body="Dear Hiring Manager, I'm interested in this role.",
        status="DRAFT",
        created_at=datetime.now()
    )
    assert draft.status == "DRAFT"
    assert "python" in draft.subject.lower()

def test_email_draft_invalid_email():
    """Test that invalid email raises ValidationError."""
    with pytest.raises(ValueError):
        EmailDraft(
            id="draft-123",
            job_id="job-456",
            recipient="not-an-email",  # Invalid
            subject="Application",
            body="Body",
            status="DRAFT",
            created_at=datetime.now()
        )

def test_email_draft_invalid_status():
    """Test that invalid status raises ValidationError."""
    with pytest.raises(ValueError):
        EmailDraft(
            id="draft-123",
            job_id="job-456",
            recipient="hiring@company.com",
            subject="Application",
            body="Body",
            status="INVALID",  # Invalid
            created_at=datetime.now()
        )
