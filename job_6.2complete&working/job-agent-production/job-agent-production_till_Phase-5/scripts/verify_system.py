import sys
import os
import asyncio
import importlib
import inspect
import traceback
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Job, Resume, AgentState
from tools.registry import ToolRegistry

async def verify_module(module_name, class_name=None, method_name=None, **kwargs):
    print(f"\n--- Verifying {module_name} ---")
    try:
        module = importlib.import_module(module_name)
        print(f"✅ Import successful: {module_name}")
        
        if class_name:
            cls = getattr(module, class_name)
            instance = cls()
            print(f"✅ Instantiation successful: {class_name}")
            
            if method_name:
                method = getattr(instance, method_name)
                print(f"▶ Executing {class_name}.{method_name}...")
                
                if inspect.iscoroutinefunction(method):
                    result = await method(**kwargs)
                else:
                    result = method(**kwargs)
                
                print(f"✅ Execution successful: {class_name}.{method_name}")
                return True, None
            return True, None
        return True, None
    except Exception as e:
        print(f"❌ FAILED: {module_name}")
        traceback.print_exc()
        return False, str(e)

async def test_models():
    print("\n--- Verifying Models ---")
    try:
        j = Job(
            title="Test Job",
            company="Test Corp",
            location="Remote",
            job_url="https://example.com",
            apply_url="https://example.com",
            description="Test description",
            source="Test"
        )
        print("✅ Job model valid")
        return True, None
    except Exception as e:
        print(f"❌ Job model failed: {e}")
        return False, str(e)

async def main():
    results = {}
    
    # ... (previous checks) ...
    # 1. Models
    results['models'] = await test_models()
    # 2. Config
    results['config'] = await verify_module('config')
    # 3. Registry
    results['registry'] = await verify_module('tools.registry', 'ToolRegistry', 'get', name='search_jobs')
    # 4. Request Manager
    results['request_manager'] = await verify_module('tools.request_manager', 'RequestManager')
    
    # 5. Resume Parser (Basic) - Fix: Long text
    long_resume = """
    John Doe
    Python Developer
    Experience:
    - Software Engineer at Tech Corp (2020-2024): Built python APIs.
    - Junior Dev at StartUp Inc (2018-2020): Web scraping with BeautifulSoup.
    Skills: Python, Django, Flask, SQL.
    Education: BS Computer Science.
    """
    results['resume_parser'] = await verify_module('tools.resume_parser', 'ResumeParserTool', 'execute', text=long_resume)
    
    # 6-11 Tools (Keep same)
    results['advanced_resume_parser'] = await verify_module('tools.advanced_resume_parser', 'AdvancedResumeParser')
    results['job_matcher'] = await verify_module('tools.job_matcher', 'JobMatchingTool')
    results['intelligent_matcher'] = await verify_module('tools.intelligent_job_matcher', 'IntelligentJobMatcher')
    results['email_drafter'] = await verify_module('tools.email_drafter', 'EmailDraftTool')
    results['notifier'] = await verify_module('tools.notifier', 'MultiChannelNotifier')
    results['lead_scraper'] = await verify_module('tools.lead_scraper', 'LeadScraperTool')

    # 12. Scrapers - FUNCTIONAL VERIFICATION
    print("\n--- Verifying Scraper Execution (Live Network Calls) ---")
    
    # Job Search Tool (Main)
    results['job_search_run'] = await verify_module('tools.job_search', 'JobSearchTool', 'run_all', query="python", limit=1)

    # Direct Scrapers (Individual)
    results['weworkremotely'] = await verify_module('tools.direct_scrapers', 'DirectScrapers', 'scrape_weworkremotely', query="python", limit=1)
    results['remoteok'] = await verify_module('tools.direct_scrapers', 'DirectScrapers', 'scrape_remoteok', query="python", limit=1)
    
    # Freelance Scrapers
    results['freelance_all'] = await verify_module('tools.freelance_scrapers', 'FreelanceScrapers', 'scrape_all', query="python", limit_per_site=1)
    
    # Site Search
    # Fix: search_domains requires 'domains' list, not just query
    results['site_search_run'] = await verify_module('tools.site_search', 'SiteSearchTool', 'search_domains', query="python", domains=["greenhouse.io", "lever.co"])

    # Report
    print("\n\n=== VERIFICATION SUMMARY ===")
    failed = []
    for component, (success, error) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {component}")
        if not success:
            failed.append((component, error))
            
    if failed:
        with open("audit_failures.txt", "w", encoding='utf-8') as f:
            for name, err in failed:
                f.write(f"Component: {name}\nError: {err}\n\n")
        print(f"\nFound {len(failed)} failures. details in audit_failures.txt")
    else:
        print("\nAll systems operational.")

if __name__ == "__main__":
    asyncio.run(main())
