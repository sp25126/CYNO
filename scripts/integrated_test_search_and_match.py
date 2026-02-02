import asyncio
import os
from pprint import pprint
from models import Resume, WorkExperience
from tools.job_search import JobSearchTool
from tools.job_matcher import JobMatchingTool

# Configuration
CONFIG = {
    "reddit_client_id": "u3pdMT0rhgm07aXy3tk7dQ",
    "reddit_client_secret": "qaKDek7iLymS2qVPWFaDhedbbSCNQA"
}

# Sample Resume (Python Developer)
SAMPLE_RESUME = Resume(
    contact_info={"email": "test@example.com"},
    summary="Senior Python Developer with 5 years of experience in Backend, AI, and Cloud.",
    parsed_skills=["Python", "Django", "FastAPI", "AWS", "Docker", "PostgreSQL", "React"],
    education_level="BACHELORS",
    years_exp=5,
    experience=[
        WorkExperience(
            title="Senior Backend Engineer",
            company="Tech Solutions Inc",
            description="Developed microservices using Python FastAPI and AWS Lambda."
        )
    ],
    location="Remote",
    raw_text="Test Resume"
)

async def run_integrated_test():
    print("--- Starting Integrated Test: Phase 2 (Search) + Phase 3 (Match) ---")
    
    # 1. Initialize Tools
    search_tool = JobSearchTool(config=CONFIG)
    match_tool = JobMatchingTool()
    
    # 2. Execute Search (Phase 2)
    query = "Python Developer"
    print(f"\n[Phase 2] Searching for '{query}'...")
    
    # We'll use "all" to get diverse results to test ranking
    jobs = await search_tool.execute(query=query, source="all")
    print(f"-> Found {len(jobs)} raw jobs.")
    
    if not jobs:
        print("No jobs found! Aborting match test.")
        return

    # 3. Execute Match (Phase 3)
    print(f"\n[Phase 3] Matching {len(jobs)} jobs against resume...")
    start_time = asyncio.get_event_loop().time()
    ranked_results = await match_tool.execute(SAMPLE_RESUME, jobs)
    duration = asyncio.get_event_loop().time() - start_time
    
    print(f"-> Ranking completed in {duration:.4f}s")
    
    # 4. Display Top Results
    print("\n=== Top 5 Matched Jobs ===")
    for i, (job, score, reason) in enumerate(ranked_results[:5], 1):
        print(f"{i}. [{score:.2f}] {job.title}")
        print(f"    Company: {job.company}")
        print(f"    Location: {job.location}")
        print(f"    Reason: {reason}")
        print(f"    URL: {job.job_url}")
        print("-" * 40)

    # 5. Display Bottom Results (Sanity Check)
    print("\n=== Bottom 3 Matched Jobs (Least Relevant) ===")
    for i, (job, score, reason) in enumerate(ranked_results[-3:], 1):
        print(f"{i}. [{score:.2f}] {job.title}")
        print(f"    Reason: {reason}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(run_integrated_test())
