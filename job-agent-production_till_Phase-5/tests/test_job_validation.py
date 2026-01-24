import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Job

def test_job_valid_creation():
    """Test creating valid job."""
    job = Job(
        title="Python Developer",
        company="TechCorp",
        location="Bangalore",
        job_url="https://techcorp.com/jobs/123",
        apply_url="https://techcorp.com/apply/123",
        description="Build AI systems",
        source="DuckDuckGo"
    )
    assert job.title == "Python Developer"
    assert job.source == "DuckDuckGo"

def test_job_invalid_url():
    """Test that invalid URL raises ValidationError."""
    with pytest.raises(ValueError):
        Job(
            title="Python Developer",
            company="TechCorp",
            location="Bangalore",
            job_url="not-a-url",  # Invalid
            apply_url="https://techcorp.com/apply/123",
            description="Build AI systems",
            source="DuckDuckGo"
        )

def test_job_missing_required_field():
    """Test that missing required field raises ValidationError."""
    # Pydantic raises ValidationError for missing fields
    with pytest.raises(ValueError):
        Job(
            title="Python Developer",
            company="TechCorp",
            # location missing
            job_url="https://techcorp.com/jobs/123",
            apply_url="https://techcorp.com/apply/123",
            description="Build AI systems",
            source="DuckDuckGo"
        )
