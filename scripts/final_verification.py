import asyncio
import sys
import os
import pytest
from datetime import datetime

# Ensure root is in path
sys.path.append(os.getcwd())

from agent.graph import build_agent_graph
from tools.job_search import JobSearchTool
from tools.job_matcher import JobMatchingTool
from models import Resume

async def run_final_proof():
    print(f"STARING FINAL SYSTEM VERIFICATION at {datetime.now()}")
    print("=" * 60)

    results = {}

    # 1. PARAMETER VALIDATION & SCHEMA (Implicit in imports)
    print("\n[STEP 1] Validating Pydantic Schemas...")
    try:
        r = Resume(
            contact_info={"email": "test@test.com"}, 
            parsed_skills=["Python"], 
            years_exp=5, 
            education_level="BACHELORS",
            raw_text="Simple Resume"
        )
        print(f"   ✅ Resume Model Init: OK ({r.education_level})")
        results["Schemas"] = "PASS"
    except Exception as e:
        print(f"   ❌ Resume Model Failed: {e}")
        results["Schemas"] = "FAIL"

    # 2. RESUME PARSER
    print("\n[STEP 2] Verifying Resume Parser Tool...")
    # we run pytest programmatically
    ret_code = pytest.main(["-q", "acceptance_tests/resume_parser/test_resume_parser.py"])
    if ret_code == 0:
        print("   ✅ Parser Tests: PASS")
        results["Parser"] = "PASS"
    else:
        print(f"   ❌ Parser Tests: FAIL (Code {ret_code})")
        results["Parser"] = "FAIL"

    # 3. JOB SEARCH & MATCHING (Integration)
    print("\n[STEP 3] Verifying Search + Matching (End-to-End Tools)...")
    try:
        search_config = {
            "reddit_client_id": os.getenv("REDDIT_CLIENT_ID"),
            "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET")
        }
        search_tool = JobSearchTool(config=search_config)
        match_tool = JobMatchingTool()
        
        query = "Senior Python Developer"
        print(f"   -> Searching for '{query}'...")
        jobs = await search_tool.execute(query, source="all")
        print(f"   -> Found {len(jobs)} jobs from [DDG, Reddit, JobSpy].")
        
        if len(jobs) > 0:
             # Matching
            resume = Resume(
                contact_info={},
                parsed_skills=["Python", "Django", "FastAPI", "AWS", "React"],
                years_exp=5,
                education_level="BACHELORS",
                raw_text="Synthentic"
            )
            scored = await match_tool.execute(resume, jobs)
            print(f"   -> Matched {len(scored)} jobs.")
            print(f"   -> Top Match: {scored[0][0].title} (Score: {scored[0][1]:.2f})")
            results["Search_Match"] = "PASS"
            
            # Save Results
            save_results(scored, query)
        else:
            print("   ❌ No jobs found to match.")
            results["Search_Match"] = "FAIL"

    except Exception as e:
        print(f"   ❌ Search/Match Failed: {e}")
        import traceback
        traceback.print_exc()
        results["Search_Match"] = "FAIL"

    # 4. AGENT ORCHESTRATION
    print("\n[STEP 4] Verifying LangGraph Orchestrator...")
    try:
        graph = build_agent_graph()
        user_input = "I am a Senior Python Developer. Find me jobs."
        state = {
            "messages": [{"role": "user", "content": user_input}],
            "parsed_resume": None,
            "jobs_found": [],
            "matched_jobs": []
        }
        # Run graph
        final = await graph.ainvoke(state, config={"recursion_limit": 20})
        
        if final.get("matched_jobs") and len(final["matched_jobs"]) > 0:
            print(f"   ✅ Agent routed successfully: Parse -> Search -> Match.")
            results["Agent"] = "PASS"
        else:
            print(f"   ❌ Agent finished but no matches found. Final Output: {final.get('messages')[-1]['content']}")
            results["Agent"] = "WARN" # Might be just 0 results
            
    except Exception as e:
        print(f"   ❌ Agent Expectation Failed: {e}")
        results["Agent"] = "FAIL"

    print("\n" + "=" * 60)
    print("FINAL VERIFICATION REPORT")
    print("=" * 60)
    for k, v in results.items():
        print(f"{k.ljust(15)}: {v}")
    
    if all(v == "PASS" for v in results.values()):
        print("\n✅ SYSTEM FULLY VERIFIED.")
    else:
        print("\n⚠️ SYSTEM PARTIALLY VERIFIED.")

def save_results(scored_jobs, query):
    filename = "real_job_results.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Real Job Results (Ranked) for '{query}'\n")
        f.write(f"Generated on: {datetime.now()}\n")
        f.write(f"Total Found: {len(scored_jobs)}\n")
        f.write("="*50 + "\n\n")
        for i, (job, score, reason) in enumerate(scored_jobs, 1):
            f.write(f"{i}. [{score:.2f}] {job.title}\n")
            f.write(f"   Company: {job.company}\n")
            f.write(f"   Location: {job.location}\n")
            f.write(f"   Match Reason: {reason}\n")
            f.write(f"   Link: {job.job_url}\n")
            f.write("-"*40 + "\n")
    print(f"   -> Results saved to {filename}")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(run_final_proof())
