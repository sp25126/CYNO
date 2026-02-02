import asyncio
import os
import sys

# Ensure current dir is in path
sys.path.append(os.getcwd())

try:
    from tools.job_search import JobSearchTool
    from tools.job_matcher import JobMatchingTool
    from models import Resume
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

from datetime import datetime

async def generate_real_results():
    print("Force-Generating Real Job Results...")
    
    # Config
    search_config = {
        "reddit_client_id": os.getenv("REDDIT_CLIENT_ID"),
        "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET")
    }
    
    search_tool = JobSearchTool(config=search_config)
    match_tool = JobMatchingTool()
    
    query = "Senior Python Developer"
    print(f"1. Scraping jobs for '{query}' (Sources: DDG, JobSpy, Reddit)...")
    
    jobs = await search_tool.execute(query, source="all")
    print(f"   found {len(jobs)} jobs.")
    
    print("2. Ranking jobs...")
    resume = Resume(
        contact_info={},
        summary="Senior Python Developer",
        parsed_skills=["Python", "Django", "FastAPI", "AWS", "React", "Linux"],
        years_exp=5,
        location="Remote",
        raw_text="Placeholder"
    )
    
    scored_jobs = await match_tool.execute(resume, jobs)
    
    filename = "real_job_results.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"Real Job Results (Ranked) for '{query}'\n")
            f.write(f"Generated on: {datetime.now()}\n")
            f.write(f"Total Found: {len(jobs)}\n")
            f.write("="*50 + "\n\n")
            
            for i, (job, score, reason) in enumerate(scored_jobs, 1):
                f.write(f"{i}. [{score:.2f}] {job.title}\n")
                f.write(f"   Company: {job.company}\n")
                f.write(f"   Location: {job.location}\n")
                f.write(f"   Match Reason: {reason}\n")
                f.write(f"   Source: {job.source}\n")
                f.write(f"   Link: {job.job_url}\n")
                f.write("-"*40 + "\n")
                
        print(f"✅ Results saved to {filename}")
    except Exception as e:
        print(f"Failed to write file: {e}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(generate_real_results())
