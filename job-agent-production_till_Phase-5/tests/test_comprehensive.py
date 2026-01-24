"""
Comprehensive E2E test with real-world queries
"""
import sys
import asyncio
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.job_search import JobSearchTool

async def test_comprehensive():
    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE REAL-WORLD JOB SEARCH TEST")
    print("=" * 80)
    
    errors = []
    
    job_tool = JobSearchTool()
    
    # TEST 1: Remote Web Dev in India at 5LPA
    print("\n📌 TEST 1: Remote Web Developer Jobs in India (5 LPA)")
    print("-" * 80)
    try:
        start = time.time()
        results1 = await job_tool.run_all("web developer remote india 5 lpa", limit=20)
        duration1 = time.time() - start
        
        print(f"✅ Search completed in {duration1:.2f}s")
        print(f"📊 Results: {len(results1)} jobs found")
        
        if results1:
            print("\nSample Results:")
            for i, job in enumerate(results1[:3], 1):
                print(f"  {i}. {job.title} - {job.company}")
                print(f"     Location: {job.location}")
                print(f"     Source: {job.source}")
                if job.salary_range:
                    print(f"     Salary: {job.salary_range}")
            
            # Check filters
            india_count = sum(1 for j in results1 if 'india' in j.location.lower())
            remote_count = sum(1 for j in results1 if 'remote' in j.location.lower())
            print(f"\n🔍 Filter Analysis:")
            print(f"   India locations: {india_count}/{len(results1)}")
            print(f"   Remote jobs: {remote_count}/{len(results1)}")
        else:
            errors.append("TEST 1: No results found for web dev in India")
            print("⚠️  No results found")
            
    except Exception as e:
        errors.append(f"TEST 1 ERROR: {str(e)}")
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 80)
    
    # TEST 2: Web Dev Internships
    print("\n📌 TEST 2: Web Developer Internships")
    print("-" * 80)
    try:
        start = time.time()
        results2 = await job_tool.run_all("web developer internship", limit=20)
        duration2 = time.time() - start
        
        print(f"✅ Search completed in {duration2:.2f}s")
        print(f"📊 Results: {len(results2)} internships found")
        
        if results2:
            print("\nSample Results:")
            for i, job in enumerate(results2[:3], 1):
                print(f"  {i}. {job.title} - {job.company}")
                print(f"     Location: {job.location}")
                print(f"     Source: {job.source}")
            
            intern_count = sum(1 for j in results2 if 'intern' in j.title.lower())
            print(f"\n🔍 Filter Analysis:")
            print(f"   Internship titles: {intern_count}/{len(results2)}")
        else:
            errors.append("TEST 2: No results found for internships")
            print("⚠️  No results found")
            
    except Exception as e:
        errors.append(f"TEST 2 ERROR: {str(e)}")
        print(f"❌ ERROR: {e}")
    
    print("\n" + "=" * 80)
    
    # TEST 3: Freelancing Projects
    print("\n📌 TEST 3: Web Developer Freelancing Projects")
    print("-" * 80)
    try:
        start = time.time()
        results3 = await job_tool.run_all("web developer freelance project", limit=20)
        duration3 = time.time() - start
        
        print(f"✅ Search completed in {duration3:.2f}s")
        print(f"📊 Results: {len(results3)} projects found")
        
        if results3:
            print("\nSample Results:")
            for i, job in enumerate(results3[:3], 1):
                print(f"  {i}. {job.title} - {job.company}")
                print(f"     Location: {job.location}")
                print(f"     Source: {job.source}")
                if job.salary_range:
                    print(f"     Budget: {job.salary_range}")
            
            freelance_count = sum(1 for j in results3 if 'freelance' in j.source.lower() or 'freelance' in j.location.lower())
            print(f"\n🔍 Filter Analysis:")
            print(f"   Freelance sources: {freelance_count}/{len(results3)}")
        else:
            errors.append("TEST 3: No results found for freelance projects")
            print("⚠️  No results found")
            
    except Exception as e:
        errors.append(f"TEST 3 ERROR: {str(e)}")
        print(f"❌ ERROR: {e}")
    
    # Final Summary
    print("\n" + "=" * 80)
    print("📋 FINAL SUMMARY")
    print("=" * 80)
    print(f"Total Tests: 3")
    print(f"Errors Found: {len(errors)}")
    
    if errors:
        print("\n⚠️  ERRORS DETECTED:")
        for i, err in enumerate(errors, 1):
            print(f"  {i}. {err}")
    else:
        print("\n✅ ALL TESTS PASSED!")
    
    # Save errors
    with open("errors.md", "w") as f:
        f.write("# Comprehensive Test Errors\n\n")
        f.write(f"**Test Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if errors:
            f.write("## Errors Found\n\n")
            for i, err in enumerate(errors, 1):
                f.write(f"{i}. {err}\n")
        else:
            f.write("## ✅ No Errors Found\n\n")
            f.write("All tests passed successfully!\n")
        
        f.write("\n## Test Details\n\n")
        f.write("### Test 1: Remote Web Dev in India (5 LPA)\n")
        f.write(f"- Results: {len(results1) if 'results1' in locals() else 0}\n")
        f.write(f"- Duration: {duration1 if 'duration1' in locals() else 'N/A'}s\n\n")
        
        f.write("### Test 2: Web Dev Internships\n")
        f.write(f"- Results: {len(results2) if 'results2' in locals() else 0}\n")
        f.write(f"- Duration: {duration2 if 'duration2' in locals() else 'N/A'}s\n\n")
        
        f.write("### Test 3: Freelancing Projects\n")
        f.write(f"- Results: {len(results3) if 'results3' in locals() else 0}\n")
        f.write(f"- Duration: {duration3 if 'duration3' in locals() else 'N/A'}s\n")
    
    print(f"\n💾 Errors saved to: errors.md")

if __name__ == "__main__":
    asyncio.run(test_comprehensive())
