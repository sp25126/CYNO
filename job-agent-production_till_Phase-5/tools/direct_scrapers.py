"""
Direct job board scrapers using BeautifulSoup.
Scrapes HTML directly from top remote job sites.
HARDENED: Uses RequestManager for all HTTP calls.
"""
import logging
from bs4 import BeautifulSoup
from typing import List
from models import Job
from datetime import datetime
from tools.request_manager import request_manager


class DirectScrapers:
    """Direct scrapers for popular job boards using BeautifulSoup."""
    
    def __init__(self):
        self.logger = logging.getLogger("DirectScrapers")
    
    def scrape_weworkremotely(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape We Work Remotely."""
        jobs = []
        try:
            url = "https://weworkremotely.com/remote-jobs/search"
            params = {'term': query}
            response = request_manager.get(url, params=params)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('li', class_='feature')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('span', class_='title')
                        company_elem = listing.find('span', class_='company')
                        link_elem = listing.find('a')
                        
                        if title_elem and company_elem and link_elem:
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip(),
                                location="Remote",
                                job_url=f"https://weworkremotely.com{link_elem['href']}",
                                apply_url=f"https://weworkremotely.com{link_elem['href']}",
                                description="",
                                source="We Work Remotely (Direct)",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse WWR job: {e}")
                        
            self.logger.info(f"We Work Remotely: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"We Work Remotely failed: {e}")
        
        return jobs
    
    def scrape_remoteok(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Remote OK."""
        jobs = []
        try:
            url = f"https://remoteok.com/remote-{query.replace(' ', '-')}-jobs"
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('tr', class_='job')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('h2', itemprop='title')
                        company_elem = listing.find('h3', itemprop='name')
                        link_elem = listing.find('a', class_='preventLink')
                        
                        if title_elem and link_elem:
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "Remote Company",
                                location="Remote",
                                job_url=f"https://remoteok.com{link_elem['href']}",
                                apply_url=f"https://remoteok.com{link_elem['href']}",
                                description="",
                                source="Remote OK (Direct)",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse RemoteOK job: {e}")
                        
            self.logger.info(f"Remote OK: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Remote OK failed: {e}")
        
        return jobs
    
    def scrape_remotive(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Remotive."""
        jobs = []
        try:
            url = "https://remotive.com/api/remote-jobs"
            params = {'search': query, 'limit': limit}
            response = request_manager.get(url, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                for job_data in data.get('jobs', [])[:limit]:
                    try:
                        jobs.append(Job(
                            title=job_data.get('title', 'Unknown'),
                            company=job_data.get('company_name', 'Unknown'),
                            location="Remote",
                            job_url=job_data.get('url', ''),
                            apply_url=job_data.get('url', ''),
                            description=job_data.get('description', '')[:500],
                            source="Remotive (API)",
                            salary_range=job_data.get('salary', ''),
                            date_posted=job_data.get('publication_date', 'Recent')
                        ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Remotive job: {e}")
                        
            self.logger.info(f"Remotive: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Remotive failed: {e}")
        
        return jobs
    
    def scrape_himalayas(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Himalayas (has public job board)."""
        jobs = []
        try:
            url = "https://himalayas.app/jobs"
            params = {'search': query}
            response = request_manager.get(url, params=params)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='job-listing')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('h3')
                        company_elem = listing.find('span', class_='company')
                        link_elem = listing.find('a')
                        
                        if title_elem and link_elem:
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "Unknown",
                                location="Remote",
                                job_url=f"https://himalayas.app{link_elem['href']}",
                                apply_url=f"https://himalayas.app{link_elem['href']}",
                                description="",
                                source="Himalayas (Direct)",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Himalayas job: {e}")
                        
            self.logger.info(f"Himalayas: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Himalayas failed: {e}")
        
        return jobs
    
    def scrape_all(self, query: str, limit_per_site: int = 10) -> List[Job]:
        """Run all direct scrapers."""
        all_jobs = []
        
        self.logger.info(f"Running direct scrapers for: {query}")
        
        # Run all scrapers
        all_jobs.extend(self.scrape_weworkremotely(query, limit_per_site))
        all_jobs.extend(self.scrape_remoteok(query, limit_per_site))
        all_jobs.extend(self.scrape_remotive(query, limit_per_site))
        all_jobs.extend(self.scrape_himalayas(query, limit_per_site))
        
        self.logger.info(f"Direct scrapers total: {len(all_jobs)} jobs from {4} sites")
        return all_jobs
