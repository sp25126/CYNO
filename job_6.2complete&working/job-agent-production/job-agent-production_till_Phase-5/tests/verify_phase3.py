import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.email_drafter import EmailDraftTool
from models import Job, Resume

def test_email_generation():
    print("Testing Email Generation...")
    
    # 1. Create Dummy Data
    job = Job(
        title="Senior Python AI Engineer",
        company="DeepMind (Simulation)",
        location="Remote",
        job_url="https://google.com/jobs/123",
        apply_url="https://google.com/jobs/123",
        description="We are looking for an expert in Python and LLMs to build agentic coding assistants.",
        source="Test"
    )
    
    resume = Resume(
        parsed_skills=["Python", "LangChain", "LLMs", "Pydantic"],
        years_exp=5,
        location="San Francisco, CA",
        keywords=["AI", "Agent"],
        raw_text="Test Resume"
    )
    
    # 2. Run Tool
    tool = EmailDraftTool()
    draft = tool.execute(job, resume)
    
    # 3. Verify
    print(f"Draft Generated: {draft.subject}")
    print(f"Status: {draft.status}")
    print(f"Body Preview: {draft.body[:100]}...")
    
    # 4. Check File
    folder = Path("emails")
    files = list(folder.glob("draft_DeepMind_Simulation_*.txt"))
    if files:
        print(f"SUCCESS: File created at {files[-1]}")
    else:
        print("FAILURE: No file created.")

if __name__ == "__main__":
    test_email_generation()
