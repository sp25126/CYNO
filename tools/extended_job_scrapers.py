"""
Extended job board scrapers.
Covers Wellfound, Arc.dev, Y Combinator, JustRemote.
HARDENED: Uses RequestManager for all HTTP calls.
"""
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Optional
from models import Job
from datetime import datetime
from tools.request_manager import request_manager


class ExtendedJobScrapers:
    """Scrapers for additional job boards."""
    
    def __init__(self):
        self.logger = logging.getLogger("ExtendedJobScrapers")
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text."""
        if not text:
            return None
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def scrape_wellfound(self, query: str, limit: int = 15) -> List[Job]:
        """Scrape Wellfound (AngelList Talent)."""
        jobs = []
        try:
            url = f"https://wellfound.com/role/r/{query.replace(' ', '-')}"
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('div', class_='job-listing')[:limit]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h2')
                        company_elem = card.find('span', class_='company-name')
                        salary_elem = card.find('span', class_='salary')
                        link_elem = card.find('a')
                        description_elem = card.find('div', class_='description')
                        
                        if title_elem and link_elem:
                            description_text = description_elem.text.strip() if description_elem else ""
                            email = self._extract_email(description_text)
                            
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "Startup",
                                location="Remote/Flexible",
                                job_url=f"https://wellfound.com{link_elem['href']}",
                                apply_url=f"https://wellfound.com{link_elem['href']}",
                                description=description_text[:1000],
                                source="Wellfound",
                                salary_range=salary_elem.text.strip() if salary_elem else None,
                                date_posted="Recent",
                                contact_email=email
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Wellfound job: {e}")
            
            self.logger.info(f"Wellfound: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Wellfound failed: {e}")
        
        return jobs
    
    def scrape_arc_dev(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Arc.dev."""
        jobs = []
        try:
            url = f"https://arc.dev/remote-jobs/{query.replace(' ', '-')}"
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='job-card')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('h3')
                        company_elem = listing.find('span', class_='company')
                        salary_elem = listing.find('span', class_='salary')
                        link_elem = listing.find('a')
                        
                        if title_elem and link_elem:
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "Arc Client",
                                location="Remote",
                                job_url=f"https://arc.dev{link_elem['href']}",
                                apply_url=f"https://arc.dev{link_elem['href']}",
                                description="",
                                source="Arc.dev",
                                salary_range=salary_elem.text.strip() if salary_elem else None,
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Arc job: {e}")
            
            self.logger.info(f"Arc.dev: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Arc.dev failed: {e}")
        
        return jobs
    
    def scrape_ycombinator(self, query: str, limit: int = 15) -> List[Job]:
        """Scrape Y Combinator jobs."""
        jobs = []
        try:
            url = f"https://www.ycombinator.com/jobs?query={query.replace(' ', '+')}"
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='job')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('h4')
                        company_elem = listing.find('span', class_='company')
                        link_elem = listing.find('a')
                        
                        if title_elem and link_elem:
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "YC Startup",
                                location="Startup Office/Remote",
                                job_url=f"https://www.ycombinator.com{link_elem['href']}",
                                apply_url=f"https://www.ycombinator.com{link_elem['href']}",
                                description="",
                                source="Y Combinator",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse YC job: {e}")
            
            self.logger.info(f"Y Combinator: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Y Combinator failed: {e}")
        
        return jobs
    
    def scrape_justremote(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape JustRemote.co."""
        jobs = []
        try:
            url = f"https://justremote.co/remote-{query.replace(' ', '-')}-jobs"
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_cards = soup.find_all('article', class_='job-listing')[:limit]
                
                for card in job_cards:
                    try:
                        title_elem = card.find('h3')
                        company_elem = card.find('span', class_='company-name')
                        link_elem = card.find('a')
                        
                        if title_elem and link_elem:
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "Remote Company",
                                location="Remote",
                                job_url=f"https://justremote.co{link_elem['href']}",
                                apply_url=f"https://justremote.co{link_elem['href']}",
                                description="",
                                source="JustRemote",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse JustRemote job: {e}")
            
            self.logger.info(f"JustRemote: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"JustRemote failed: {e}")
        
        return jobs
    
    def scrape_all(self, query: str, limit_per_site: int = 10) -> List[Job]:
        """Run all extended job scrapers."""
        all_jobs = []
        
        self.logger.info(f"Running extended job scrapers for: {query}")
        
        all_jobs.extend(self.scrape_wellfound(query, limit_per_site))
        all_jobs.extend(self.scrape_arc_dev(query, limit_per_site))
        all_jobs.extend(self.scrape_ycombinator(query, limit_per_site))
        all_jobs.extend(self.scrape_justremote(query, limit_per_site))
        
        self.logger.info(f"Extended job scrapers total: {len(all_jobs)} jobs from 4 sites")
        return all_jobs
