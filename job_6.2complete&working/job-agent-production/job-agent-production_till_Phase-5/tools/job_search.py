import os
import logging
import pandas as pd
import praw
from ddgs import DDGS
from jobspy import scrape_jobs
from datetime import datetime
import csv
import logging
from typing import List, Dict, Any
import pandas as pd
from tools.base import JobAgentTool
from models import Job
from jobspy import scrape_jobs
from pathlib import Path
from config import Config

# Subreddits to search (Expanded List)
DEFAULT_SUBREDDITS = [
    "remotejobs", "forhire", "jobbit", "freelance_forhire", 
    "RemotePython", "pythonjobs", "devopsjobs", "sysadminjobs",
    "hiring", "RemoteWorkSources", "remotework", "techjobs",
    "funtionalprogramming" 
]

# Top Remote Sites from PDF (Expanded)
REMOTE_SITES = [
    "weworkremotely.com", "remoteok.com", "flexjobs.com", "remotive.com",
    "workingnomads.com", "jobspresso.co", "himalayas.app", "wellfound.com",
    "remote.co", "justremote.co", "nodesk.co", "citizenremote.com",
    "jobgether.com", "pangian.com", "skipthedrive.com", "virtualvocations.com",
    "authenticjobs.com", "dribbble.com/jobs", "behance.net/joblist",
    "hackerrank.com/jobs", "stackoverflow.com/jobs", "landing.jobs",
    "gun.io", "toptal.com", "upwork.com", "freelancer.com", "guru.com",
    "arc.dev", "codementor.io", "hired.com", "vettery.com", "monster.com",
    "careerbuilder.com", "simplyhired.com", "ziprecruiter.com"
]

class JobSearchTool:
    def __init__(self):
        self.logger = logging.getLogger("JobSearchTool")
        self._setup_reddit()

    def _setup_reddit(self):
        # Using Config for credentials (loads from credentials_setup.env)
        self.reddit = praw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT
        )


    def search_jobspy(self, term, location="remote", limit=10):
        """
        Uses JobSpy to scrape Indeed, LinkedIn, Glassdoor.
        """
        self.logger.info(f"Running JobSpy for '{term}' in '{location}'...")
        try:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "glassdoor"],
                search_term=term,
                location=location,
                results_wanted=limit,
                hours_old=72,
                country_indeed='USA'
            )
            # Normalize JobSpy output to match our format
            job_list = jobs.to_dict('records') if not jobs.empty else []
            normalized_jobs = []
            for j in job_list:
                normalized_jobs.append({
                    "title": j.get("title"),
                    "company": j.get("company"),
                    "url": j.get("job_url"),
                    "description": j.get("description"),
                    "location": j.get("location"),
                    "source": f"JobSpy ({j.get('site', 'Unknown')})"
                })
            self.logger.info(f"JobSpy found {len(normalized_jobs)} jobs.")
            return normalized_jobs
        except Exception as e:
            self.logger.error(f"JobSpy Failed: {e}")
            return []

    def search_hackernews(self, query: str, limit: int = 15) -> List[Dict]:
        """
        Scrapes Hacker News 'Who is Hiring' threads using RequestManager.
        HARDENED: Uses exponential backoff and rotation.
        """
        self.logger.info(f"Searching Hacker News for '{query}'...")
        results = []
        
        try:
            from tools.request_manager import request_manager
            
            # Get latest "Who is Hiring" thread via Algolia API
            url = "https://hn.algolia.com/api/v1/search?query=who%20is%20hiring&tags=story"
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                data = response.json()
                if data.get('hits'):
                    story_id = data['hits'][0]['objectID']
                    
                    # Get comments from thread
                    comments_url = f"https://hn.algolia.com/api/v1/items/{story_id}"
                    comments_response = request_manager.get(comments_url)
                    
                    if comments_response and comments_response.status_code == 200:
                        comments_data = comments_response.json()
                        
                        # Filter comments for job postings matching term
                        for comment in comments_data.get('children', [])[:50]:
                            comment_text = comment.get('text', '')
                            if query.lower() in comment_text.lower():
                                results.append({
                                    "title": f"{query.title()} Role (HN)",
                                    "company": "Startup (HN)",
                                    "url": f"https://news.ycombinator.com/item?id={comment.get('id')}",
                                    "description": comment_text[:500],
                                    "location": "Remote",
                                    "source": "Hacker News"
                                })
                                if len(results) >= limit:
                                    break
            
            self.logger.info(f"Hacker News found {len(results)} postings")
        except Exception as e:
            self.logger.error(f"Hacker News failed: {e}")
        
        return results

    def search_ddg_pdfs(self, term, limit=10):
        """
        Uses DuckDuckGo to search for jobs - SIMPLIFIED APPROACH.
        """
        self.logger.info(f"Running DDGS Search for '{term}'...")
        results = []
        
        try:
            with DDGS() as ddgs:
                # Simple, direct search - no complex site: filters
                queries = [
                    f"{term} remote job apply",
                    f"{term} job opening site:weworkremotely.com OR site:remoteok.com",
                    f"{term} careers"
                ]
                
                seen_urls = set()
                for query in queries:
                    if len(results) >= limit:
                        break
                    
                    try:
                        ddg_gen = ddgs.text(query, region='us-en', max_results=5)
                        if ddg_gen:
                            for r in ddg_gen:
                                url = r.get('href', '')
                                if url and url not in seen_urls:
                                    seen_urls.add(url)
                                    results.append({
                                        "title": r.get('title', 'Untitled'),
                                        "company": "Unknown (Aggregated)",
                                        "url": url,
                                        "description": r.get('body', ''),
                                        "source": "DuckDuckGo"
                                    })
                    except Exception as e:
                        self.logger.warning(f"DDGS query '{query}' failed: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"DDGS Failed: {e}")

        self.logger.info(f"DDG found {len(results)} jobs.")
        return results
    
    # ========================================
    # BEAUTIFULSOUP DIRECT SCRAPING SECTION
    # ========================================
    
    def scrape_weworkremotely(self, query="python", limit=15):
        """Direct HTML scrape of WeWorkRemotely."""
        import requests
        from bs4 import BeautifulSoup
        
        results = []
        try:
            url = f"https://weworkremotely.com/remote-jobs/search?term={query}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            jobs = soup.find_all('li', class_='feature')[:limit]
            for job in jobs:
                try:
                    title_tag = job.find('span', class_='title')
                    company_tag = job.find('span', class_='company')
                    link_tag = job.find('a')
                    
                    if title_tag and link_tag:
                        results.append({
                            'title': title_tag.text.strip(),
                            'company': company_tag.text.strip() if company_tag else 'Unknown',
                            'url': f"https://weworkremotely.com{link_tag['href']}",
                            'description': 'Remote position',
                            'source': 'WeWorkRemotely'
                        })
                except:
                    continue
        except Exception as e:
            self.logger.error(f"WeWorkRemotely failed: {e}")
        
        self.logger.info(f"WeWorkRemotely found {len(results)} jobs")
        return results
    
    def scrape_remoteok(self, query="python", limit=15):
        """Scrape RemoteOK API."""
        import requests
        
        results = []
        try:
            url = f"https://remoteok.com/api?tag={query}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            jobs_data = response.json()[1:limit+1]
            
            for job in jobs_data:
                try:
                    results.append({
                        'title': job.get('position', 'Unknown'),
                        'company': job.get('company', 'Unknown'),
                        'url': job.get('url', f"https://remoteok.com/jobs/{job.get('id')}"),
                        'description': job.get('description', '')[:500],
                        'source': 'RemoteOK'
                    })
                except:
                    continue
        except Exception as e:
            self.logger.error(f"RemoteOK failed: {e}")
        
        self.logger.info(f"RemoteOK found {len(results)} jobs")
        return results
    
    def scrape_remotive(self, query="python", limit=15):
        """Scrape Remotive API."""
        import requests
        
        results = []
        try:
            url = f"https://remotive.com/api/remote-jobs?category=software-dev&search={query}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            jobs_data = response.json().get('jobs', [])[:limit]
            
            for job in jobs_data:
                try:
                    results.append({
                        'title': job.get('title', 'Unknown'),
                        'company': job.get('company_name', 'Unknown'),
                        'url': job.get('url', ''),
                        'description': job.get('description', '')[:500],
                        'source': 'Remotive'
                    })
                except:
                    continue
        except Exception as e:
            self.logger.error(f"Remotive failed: {e}")
        
        self.logger.info(f"Remotive found {len(results)} jobs")
        return results
    
    # ========================================
    # SPECIALIZED SCRAPERS
    # ========================================
    
    def scrape_startups(self, query="developer", limit=50):
        """
        Scrape startup-focused job boards.
        Sites: AngelList, YCombinator, StartupJobs, Wellfound, etc.
        """
        import requests
        from bs4 import BeautifulSoup
        
        results = []
        
        # 1. AngelList/Wellfound (already have API access)
        try:
            url = f"https://api.wellfound.com/talent/jobs?search={query}"
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            # Note: AngelList requires auth, so we'll use DuckDuckGo with site filter instead
        except:
            pass
        
        # Startup sites list (using DDG site: filter for most)
        startup_sites = [
            "angel.co", "wellfound.com", "ycombinator.com/jobs",
            "startupjobs.com", "startupers.com", "startups.com/jobs",
            "techstars.com/jobs", "f6s.com", "we.co/jobs", "crew.co/jobs"
        ]
        
        # Use DDGS to search these sites
        try:
            with DDGS() as ddgs:
                site_filter = " OR ".join([f"site:{s}" for s in startup_sites[:5]])
                query_str = f"{query} startup ({site_filter})"
                
                for r in ddgs.text(query_str, region='us-en', max_results=limit):
                    results.append({
                        'title': r.get('title', 'Startup Position'),
                        'company': 'Startup',
                        'url': r.get('href', ''),
                        'description': r.get('body', '')[:500],
                        'source': 'Startup Boards'
                    })
        except Exception as e:
            self.logger.error(f"Startup scraping failed: {e}")
        
        self.logger.info(f"Startup boards found {len(results)} jobs")
        return results
    
    def scrape_internships(self, query="developer", limit=50):
        """
        Scrape internship-focused boards.
        Sites: Intern Supply, Chegg Internships, Indeed Internships, etc.
        """
        results = []
        
        internship_sites = [
            "internsupply.com", "cheggInternships.com", "internships.com",
            "wayup.com", "ripplematch.com", "handshake.com",
            "intern.supply", "looksharp.com", "internqueen.com", "idealist.org"
        ]
        
        try:
            with DDGS() as ddgs:
                # Multiple queries for better coverage
                queries = [
                    f"{query} internship 2024 2025",
                    f"summer intern {query}",
                    f"{query} co-op"
                ]
                
                seen = set()
                for q in queries:
                    if len(results) >= limit:
                        break
                    for r in ddgs.text(q, region='us-en', max_results=20):
                        url = r.get('href', '')
                        if url not in seen and 'intern' in r.get('title', '').lower():
                            seen.add(url)
                            results.append({
                                'title': r.get('title', 'Internship'),
                                'company': 'Various',
                                'url': url,
                                'description': r.get('body', '')[:500],
                                'source': 'Internship Boards'
                            })
        except Exception as e:
            self.logger.error(f"Internship scraping failed: {e}")
        
        self.logger.info(f"Internship boards found {len(results)} jobs")
        return results
    
    def scrape_international(self, query="developer", limit=30):
        """
        Scrape international job boards.
        Sites: Indeed Global, Glassdoor International, LinkedIn Global, EU Remote, etc.
        """
        results = []
        
        international_sites = [
            "euremotejobs.com", "remoters.net", "remote-jobs.com",
            "relocate.me", "globalworkandtravel.com"
        ]
        
        try:
            with DDGS() as ddgs:
                queries = [
                    f"{query} remote international",
                    f"{query} europe remote",
                    f"{query} visa sponsorship",
                    f"{query} relocate"
                ]
                
                seen = set()
                for q in queries:
                    if len(results) >= limit:
                        break
                    for r in ddgs.text(q, region='wt-wt', max_results=10):
                        url = r.get('href', '')
                        if url not in seen:
                            seen.add(url)
                            results.append({
                                'title': r.get('title', 'International Position'),
                                'company': 'International',
                                'url': url,
                                'description': r.get('body', '')[:500],
                                'source': 'International Boards'
                            })
        except Exception as e:
            self.logger.error(f"International scraping failed: {e}")
        
        self.logger.info(f"International boards found {len(results)} jobs")
        return results
    
    def scrape_direct_all(self, term):
        """Run all BeautifulSoup scrapers."""
        import time
        all_jobs = []
        
        # Original 3
        all_jobs.extend(self.scrape_weworkremotely(term, limit=15))
        time.sleep(1)
        all_jobs.extend(self.scrape_remoteok(term, limit=15))
        time.sleep(1)
        all_jobs.extend(self.scrape_remotive(term, limit=15))
        time.sleep(1)
        
        # NEW: Specialized scrapers (INCREASED LIMITS)
        all_jobs.extend(self.scrape_startups(term, limit=40))  # Increased from 20
        time.sleep(1)
        all_jobs.extend(self.scrape_internships(term, limit=40))  # Increased from 20
        time.sleep(1)
        all_jobs.extend(self.scrape_international(term, limit=30))  # Increased from 15
        
        self.logger.info(f"Direct scraping total: {len(all_jobs)} jobs")
        return all_jobs

    async def run_all(self, query: str, limit: int = 20) -> List[Job]:
        """
        Master Aggregator: JobSpy + Reddit + PDF Sites (Hybrid)
        """
        from tools.job_lists import PDF_DOMAINS_TOP, STARTUP_INTL, STARTUP_INDIA, INTERNSHIPS
        from tools.site_search import SiteSearchTool
        
        all_jobs = []
        
        # 1. JobSpy (Major Boards)
        self.logger.info("Step 1/3: Checking Major Boards (LinkedIn, Indeed, Glassdoor)...")
        loc = "remote"
        if "india" in query.lower(): loc = "India"
        
        try:
            # We add google and zip_recruiter
            jobs_spy = scrape_jobs(
                site_name=["indeed", "linkedin", "glassdoor", "google"],
                search_term=query,
                location=loc,
                results_wanted=10, 
                country_indeed='India' if loc == 'India' else 'USA'
            )
            if not jobs_spy.empty:
                for _, j in jobs_spy.iterrows():
                    all_jobs.append(Job(
                        title=str(j.get("title", "Unknown")),
                        company=str(j.get("company", "Unknown")),
                        location=str(j.get("location", loc)),
                        job_url=str(j.get("job_url", "")),
                        apply_url=str(j.get("job_url", "")),
                        description=str(j.get("description", "No description")),
                        source=f"JobSpy ({j.get('site', 'Unknown')})",
                        date_posted=str(j.get("date_posted", "Recent"))
                    ))
        except Exception as e:
            self.logger.error(f"JobSpy Error: {e}")
            
        # 2. Hacker News (Community)
        self.logger.info("Step 2/3: Checking Hacker News Community...")
        hn_jobs = self.search_hackernews(query, limit=15)
        for r in hn_jobs:
            all_jobs.append(Job(
                title=r['title'],
                company=r['company'],
                location=r.get('location', 'Remote'),
                job_url=r['url'],
                apply_url=r['url'],
                description=r['description'],
                source=r['source'],
                date_posted="Recent"
            ))

        # 3. Direct Scrapers (4 job boards)
        self.logger.info("Step 3/6: Scraping Direct Job Boards...")
        try:
            from tools.direct_scrapers import DirectScrapers
            direct = DirectScrapers()
            direct_jobs = []
            direct_jobs.extend(direct.scrape_weworkremotely(query, limit=10))
            direct_jobs.extend(direct.scrape_remoteok(query, limit=10))
            direct_jobs.extend(direct.scrape_remotive(query, limit=10))
            direct_jobs.extend(direct.scrape_himalayas(query, limit=10))
            
            for job in direct_jobs:
                all_jobs.append(job)
            
            self.logger.info(f"Direct scrapers: {len(direct_jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Direct scrapers failed: {e}")
        
        # 4. Freelance Scrapers (5 platforms)
        if 'freelance' in query.lower() or 'project' in query.lower():
            self.logger.info("Step 4/6: Scraping Freelance Platforms...")
            try:
                from tools.freelance_scrapers import FreelanceScrapers
                freelance = FreelanceScrapers()
                freelance_jobs = freelance.scrape_all(query, limit_per_site=10)
                
                for job in freelance_jobs:
                    all_jobs.append(job)
                
                self.logger.info(f"Freelance scrapers: {len(freelance_jobs)} projects")
            except Exception as e:
                self.logger.error(f"Freelance scrapers failed: {e}")
        
        # 5. Extended Job Scrapers (4 boards)
        self.logger.info("Step 5/6: Scraping Extended Job Boards...")
        try:
            from tools.extended_job_scrapers import ExtendedJobScrapers
            extended = ExtendedJobScrapers()
            extended_jobs = extended.scrape_all(query, limit_per_site=10)
            
            for job in extended_jobs:
                all_jobs.append(job)
            
            self.logger.info(f"Extended scrapers: {len(extended_jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Extended scrapers failed: {e}")
        
        # 6. Additional Scrapers (BS4)
        self.logger.info("Step 6/7: Scraping Additional Remote Boards (Jobspresso, Remote.io)...")
        try:
            from tools.more_scrapers import MoreScrapers
            more = MoreScrapers()
            more_jobs = more.scrape_all(query, limit=10)
            
            for job in more_jobs:
                all_jobs.append(job)
            
            self.logger.info(f"More scrapers: {len(more_jobs)} jobs")
        except Exception as e:
            self.logger.error(f"More scrapers failed: {e}")

        # 7. Hybrid Site Search (500+ Sites)
        self.logger.info("Step 7/7: Deep Scanning 500+ Dedicated Sites (Hybrid Mode)...")
        hybrid_tool = SiteSearchTool()
        
        # Determine which lists to use based on query
        target_domains = PDF_DOMAINS_TOP # Default
        if "india" in query.lower() or "startup" in query.lower():
            target_domains += STARTUP_INDIA
        if "intern" in query.lower():
            target_domains += INTERNSHIPS
        if "abroad" in query.lower() or "global" in query.lower():
            target_domains += STARTUP_INTL
            
        hybrid_jobs = hybrid_tool.search_domains(query, target_domains)
        all_jobs.extend(hybrid_jobs)

        # Deduplicate by URL
        unique_jobs = {j.job_url: j for j in all_jobs}.values()
        final_list = list(unique_jobs)
        
        # ==========================================
        # ADVANCED FILTERING (Post-Processing)
        # ==========================================
        filtered_jobs = []
        low_query = query.lower()
        
        # 1. Location Filter (PERMISSIVE - only filter if EXPLICITLY non-matching)
        # We only filter OUT jobs if they explicitly mention a different country/region
        # that conflicts with the user's query
        target_india = "india" in low_query
        exclude_keywords = []
        if target_india:
            # If user wants India, exclude jobs that explicitly mention other regions ONLY
            exclude_keywords = ["uk only", "us only", "usa only", "canada only", "europe only"]
        
        # 2. Type Filter (STRICT for internships)
        target_intern = "intern" in low_query
        
        # 3. Salary Filter (5LPA - PERMISSIVE, allow "Not specified")
        import re
        min_lpa = 0
        lpa_match = re.search(r'(\d+)\s*lpa', low_query)
        if lpa_match: min_lpa = int(lpa_match.group(1))
        
        for job in final_list:
            j_loc = str(job.location).lower()
            j_title = str(job.title).lower()
            j_desc = str(job.description).lower()
            j_sal = str(job.salary_range).lower()
            
            # Location Check (PERMISSIVE)
            # Only exclude if the job explicitly says it's region-locked elsewhere
            skip_location = False
            for excl in exclude_keywords:
                if excl in j_loc or excl in j_desc:
                    skip_location = True
                    break
            if skip_location:
                continue
                
            # Intern Check (STRICT - if user wants internship, title MUST say intern)
            if target_intern and "intern" not in j_title:
                continue
            
            # Salary Check (PERMISSIVE - only filter if we have data and it's below threshold)
            if min_lpa > 0:
                job_lpa = 0
                sal_match = re.search(r'(\d+)\s*lpa', j_sal)
                if sal_match: 
                    job_lpa = int(sal_match.group(1))
                    # Only filter if we found a salary AND it's below minimum
                    if job_lpa > 0 and job_lpa < min_lpa:
                        continue
                # If no salary data found, INCLUDE the job (benefit of doubt)

            filtered_jobs.append(job)

        self.logger.info(f"Filtering: {len(final_list)} -> {len(filtered_jobs)} jobs remaining.")

        # Save results
        self._save_to_csv(filtered_jobs, query)
        
        return filtered_jobs[:limit]

    def _save_to_csv(self, jobs: List[Job], query: str):
        """Save jobs to jobs/ folder with custom user format."""
        if not jobs: return
        
        try:
            folder = Path("jobs")
            folder.mkdir(exist_ok=True)
            
            # Sanitize query for filename
            clean_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query).strip()
            filename = f"jobs_{clean_query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            filepath = folder / filename
            
            # Professional CSV format
            data = []
            for j in jobs:
                data.append({
                    "Company": j.company,
                    "Title": j.title,
                    "Location": j.location,
                    "Salary": j.salary_range or "Not Specified",
                    "Posted": j.date_posted or "N/A",
                    "Source": j.source,
                    "URL": str(j.job_url)
                })
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            self.logger.info(f"Saved {len(jobs)} jobs to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Failed to save jobs CSV: {e}")
