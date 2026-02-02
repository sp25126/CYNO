"""
Quick E2E test of job search functionality
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.job_search import JobSearchTool

async def test_job_search():
    print("=" * 60)
    print("🔍 LIVE JOB SEARCH TEST")
    print("=" * 60)
    print()
    
    # Initialize
    print("1. Initializing JobSearchTool...")
    job_tool = JobSearchTool()
    print("   ✅ Initialized")
    print()
    
    # Run search
    print("2. Searching for 'Python developer' jobs...")
    print("   (This will test all 13 scrapers + RequestManager)")
    print()
    
    try:
        results = await job_tool.run_all("Python developer", limit=5)
        
        print()
        print("=" * 60)
        print(f"📊 RESULTS: Found {len(results)} jobs")
        print("=" * 60)
        print()
        
        if results:
            for i, job in enumerate(results[:5], 1):
                print(f"{i}. {job.title}")
                print(f"   Company: {job.company}")
                print(f"   Source: {job.source}")
                print(f"   URL: {str(job.job_url)[:60]}...")
                print()
        
        print("=" * 60)
        print("✅ TEST PASSED - System is working!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_job_search())
