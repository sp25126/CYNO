import pytest
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Session, Resume

def test_session_message_persistence():
    """Test adding and retrieving messages from session."""
    session = Session(
        session_id="test-123",
        user_id="user-456",
        messages=[],
        parsed_resume=None,
        matched_jobs=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Add messages
    session.add_message("user", "Find me Python jobs")
    session.add_message("assistant", "Searching...")
    
    assert len(session.messages) == 2
    assert session.messages[0]["role"] == "user"
    assert session.messages[1]["role"] == "assistant"
    
    # Serialize and deserialize
    session_dict = session.to_dict()
    assert isinstance(session_dict, dict)
    assert session_dict["session_id"] == "test-123"
    assert len(session_dict["messages"]) == 2

def test_session_resume_assignment():
    """Test assigning parsed resume to session."""
    resume = Resume.from_text("5 years Python developer from Bangalore")
    
    session = Session(
        session_id="test-789",
        user_id="user-999",
        messages=[],
        parsed_resume=resume,
        matched_jobs=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    assert session.parsed_resume is not None
    assert session.parsed_resume.years_exp >= 0
