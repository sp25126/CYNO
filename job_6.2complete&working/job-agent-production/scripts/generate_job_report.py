import asyncio
import os
from datetime import datetime
from tools.job_search import JobSearchTool

# Configuration for the tool
CONFIG = {
    "reddit_client_id": "u3pdMT0rhgm07aXy3tk7dQ",
    "reddit_client_secret": "qaKDek7iLymS2qVPWFaDhedbbSCNQA"
}

OUTPUT_FILE = "real_job_results.txt"

async def generate_report():
    print(f"--- Starting Real Job Search Verification ---")
    print(f"Target: 20+ jobs in {OUTPUT_FILE}")
    
    tool = JobSearchTool(config=CONFIG)
    
    # We use a broad query to ensure volume for this test
    query = "Python Developer"
    print(f"Querying all sources for: '{query}'...")
    
    # Execute search on all sources
    # source="all" roughly triggers ddg + reddit + jobspy (if implemented in 'all' branch)
    # Let's call them explicitly to be safe and combine
    
    jobs = []
    
    # 1. JobSpy (High volume)
    print("1. Querying JobSpy...")
    try:
        j_spy = await tool.execute(query=query, source="jobspy")
        jobs.extend(j_spy)
        print(f"   -> Found {len(j_spy)}")
    except Exception as e:
        print(f"   -> JobSpy error: {e}")

    # 2. DuckDuckGo (ATS)
    print("2. Querying DuckDuckGo...")
    try:
        j_ddg = await tool.execute(query=query, source="ddg")
        jobs.extend(j_ddg)
        print(f"   -> Found {len(j_ddg)}")
    except Exception as e:
        print(f"   -> DDG error: {e}")

    # 3. Reddit
    print("3. Querying Reddit...")
    try:
        j_reddit = await tool.execute(query=query, source="reddit")
        jobs.extend(j_reddit)
        print(f"   -> Found {len(j_reddit)}")
    except Exception as e:
        print(f"   -> Reddit error: {e}")

    # Deduplicate by URL
    unique_jobs = {j.job_url: j for j in jobs}.values()
    print(f"--- Total Unique Jobs: {len(unique_jobs)} ---")
    
    # Write to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(f"Job Search Report - {datetime.now()}\n")
        f.write(f"Query: {query}\n")
        f.write(f"Total Found: {len(unique_jobs)}\n")
        f.write("="*50 + "\n\n")
        
        for i, job in enumerate(unique_jobs, 1):
            f.write(f"{i}. {job.title}\n")
            f.write(f"   Company: {job.company}\n")
            f.write(f"   Source: {job.source}\n")
            f.write(f"   Link: {job.job_url}\n")
            f.write("-" * 40 + "\n")
            
    print(f"Results written to {os.path.abspath(OUTPUT_FILE)}")
    
    if len(unique_jobs) >= 20:
        print("TEST PASSED: Found 20+ jobs.")
    else:
        print("TEST FAILED: Found fewer than 20 jobs.")

if __name__ == "__main__":
    asyncio.run(generate_report())
