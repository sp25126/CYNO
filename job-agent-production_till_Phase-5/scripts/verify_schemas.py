import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import Resume, Job, Session, EmailDraft, WorkExperience
from pydantic import ValidationError
from datetime import datetime

def test_schemas():
    print("=== Pydantic Schema Verification ===")
    
    # 1. WorkExperience
    print("\n[1/5] Testing 'WorkExperience'...")
    try:
        we = WorkExperience(title="Dev", company="Corp", start_date="2020", end_date="2021", description="Coded things")
        print("✅ Valid WorkExperience created.")
    except ValidationError as e:
        print(f"❌ WorkExperience Failed: {e}")

    # 2. Resume
    print("\n[2/5] Testing 'Resume'...")
    try:
        r = Resume(
            parsed_skills=["Python"], 
            years_exp=5, 
            education_level="BACHELORS", 
            location="Remote",
            experience=[we],
            contact_info={"email": "test@example.com"},
            raw_text="Original text"
        )
        print("✅ Valid Resume created.")
    except ValidationError as e:
        print(f"❌ Resume Failed: {e}")
        
    print("   -> Testing Invalid Resume (Negative years_exp)...")
    try:
        Resume(parsed_skills=["Python"], years_exp=-1, location="Remote", raw_text="Fail")
        print("❌ Failed to catch negative years_exp!")
    except ValidationError:
        print("✅ Correctly caught negative years_exp.")

    # 3. Job
    print("\n[3/5] Testing 'Job'...")
    try:
        j = Job(
            title="Senior Dev",
            company="Tech Inc",
            location="Remote",
            job_url="https://example.com/job",
            apply_url="https://example.com/apply",
            description="A very long description for the job position...",
            source="Manual",
            salary_range="$100k"
        )
        print("✅ Valid Job created.")
    except ValidationError as e:
        print(f"❌ Job Failed: {e}")
        
    print("   -> Testing Invalid Job (Invalid URL)...")
    try:
        Job(title="Dev", company="A", location="B", job_url="invalid-url", apply_url="http://ok.com", description="Desc", source="Test")
        print("❌ Failed to catch invalid URL!")
    except ValidationError:
        print("✅ Correctly caught invalid URL.")

    # 4. Session
    print("\n[4/5] Testing 'Session'...")
    try:
        s = Session(session_id="sess_1", user_id="user_1")
        s.add_message("user", "Hello")
        if len(s.messages) == 1:
            print("✅ Valid Session created & updated.")
    except ValidationError as e:
        print(f"❌ Session Failed: {e}")

    # 5. EmailDraft
    print("\n[5/5] Testing 'EmailDraft'...")
    try:
        draft = EmailDraft(
            job_id="job_123",
            recipient="recruiter@example.com",
            subject="Application",
            body="Hello <script>alert('xss')</script>World"
        )
        if "<script>" not in draft.body:
             print("✅ Valid EmailDraft created & Sanitized XSS.")
        else:
             print("❌ XSS Sanitization Failed.")
    except ValidationError as e:
        print(f"❌ EmailDraft Failed: {e}")

if __name__ == "__main__":
    test_schemas()
