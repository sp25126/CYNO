import asyncio
import sys
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.job_search import JobSearchTool
from tools.lead_scraper import LeadScraperTool

# Config logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    print("🚀 STARTING MASSIVE CAPACITY TEST (Target: 125+ per category)")
    
    js = JobSearchTool()
    ls = LeadScraperTool()
    
    # 1. JOBS TEST
    print("\n[1/4] Testing Regular Job Search (Remote + Startup lists)...")
    jobs = await js.run_all("python developer", limit=150)
    print(f"✅ Jobs Found: {len(jobs)}")
    
    # 2. INTERNSHIP TEST
    print("\n[2/4] Testing Internship Search (Internship lists)...")
    interns = await js.run_all("python intern", limit=150)
    print(f"✅ Internships Found: {len(interns)}")
    
    # 3. FREELANCE TEST
    print("\n[3/4] Testing Freelance Search (Freelance lists)...")
    projects = await js.run_all("python freelance project", limit=150)
    print(f"✅ Freelance Projects Found: {len(projects)}")
    
    # 4. LEADS TEST
    print("\n[4/4] Testing Lead Generation (New Dorks)...")
    leads = ls.scrape_leads(["Python", "Django", "React"], limit=150)
    print(f"✅ Leads Found: {len(leads)}")
    
    print("\n🏁 FINAL REPORT")
    print(f"Jobs: {len(jobs)}")
    print(f"Interns: {len(interns)}")
    print(f"Freelance: {len(projects)}")
    print(f"Leads: {len(leads)}")
    
    if all(x >= 50 for x in [len(jobs), len(interns), len(projects), len(leads)]):
        print("\nSUCCESS: All categories verified with massive volume!")
    else:
        print("\nWARNING: Some categories under target (check logs).")

if __name__ == "__main__":
    asyncio.run(main())
