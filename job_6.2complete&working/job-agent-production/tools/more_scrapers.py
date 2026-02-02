"""
Additional Job Scrapers (Jobspresso, Remote.io, DailyRemote).
Uses RequestManager (with curl-cffi) to bypass protections.
"""
import logging
from bs4 import BeautifulSoup
from typing import List, Optional
from models import Job
from tools.request_manager import request_manager

logger = logging.getLogger(__name__)

class MoreScrapers:
    """Extra scrapers for high-value remote job boards."""
    
    def scrape_jobspresso(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Jobspresso.co"""
        jobs = []
        try:
            # Jobspresso uses a specific URL structure or standard search
            # Try browse page with search assumed or just latest if query fails
            # https://jobspresso.co/?s=python&feed=job_feed&job_types=remote-work ...
            # Actually, standard search is: https://jobspresso.co/remote-work/?search_keywords=python
            
            url = "https://jobspresso.co/remote-work/"
            params = {'search_keywords': query}
            
            response = request_manager.get(url, params=params)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_list = soup.find_all('div', class_='job_listing')[:limit]
                
                for item in job_list:
                    try:
                        title_elem = item.find('h3', class_='job_listing-title')
                        company_elem = item.find('div', class_='job_listing-company')
                        link_elem = item.find('a', class_='job_listing-clickbox')
                        
                        if title_elem and link_elem:
                            title = title_elem.text.strip()
                            company = company_elem.text.strip() if company_elem else "Unknown"
                            link = link_elem.get('href')
                            
                            jobs.append(Job(
                                title=title,
                                company=company,
                                location="Remote",
                                job_url=link,
                                apply_url=link,
                                description="",
                                source="Jobspresso",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        continue
                        
            logger.info(f"Jobspresso: {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Jobspresso failed: {e}")
            
        return jobs

    def scrape_remote_io(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Remote.io"""
        jobs = []
        try:
            # https://www.remote.io/remote-jobs?s=python
            url = "https://www.remote.io/remote-jobs"
            params = {'s': query}
            
            response = request_manager.get(url, params=params)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_list = soup.find_all('div', class_='job-listing-item')[:limit]
                
                for item in job_list:
                    try:
                        title_elem = item.find('h3')
                        if not title_elem: continue
                        link_elem = item.find('a', class_='job-listing-title-link')
                        if not link_elem: link_elem = item.find('a')
                        
                        company_elem = item.find('div', class_='job-listing-footer')
                        
                        if title_elem and link_elem:
                            title = title_elem.text.strip()
                            link = "https://www.remote.io" + link_elem.get('href') if link_elem.get('href').startswith('/') else link_elem.get('href')
                            company = company_elem.text.strip() if company_elem else "Unknown"
                            
                            jobs.append(Job(
                                title=title,
                                company=company.split('|')[0].strip(),
                                location="Remote",
                                job_url=link,
                                apply_url=link,
                                description="",
                                source="Remote.io",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        continue
                        
            logger.info(f"Remote.io: {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"Remote.io failed: {e}")
            
        return jobs
        
    def scrape_dailyremote(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape DailyRemote.com"""
        jobs = []
        try:
            # https://dailyremote.com/remote-python-jobs
            # Search URL might be different
            url = f"https://dailyremote.com/remote-{query.replace(' ', '-')}-jobs"
            
            response = request_manager.get(url)
            
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_list = soup.find_all('article', class_='job-post')[:limit]
                
                for item in job_list:
                    try:
                        title_elem = item.find('h3')
                        company_elem = item.find('span', class_='company-name')
                        link_elem = item.find('a', class_='job-title-link')
                        if not link_elem: link_elem = item.find('a')


                        if title_elem and link_elem:
                            title = title_elem.text.strip()
                            link = "https://dailyremote.com" + link_elem.get('href') if link_elem.get('href').startswith('/') else link_elem.get('href')
                            
                            jobs.append(Job(
                                title=title,
                                company=company_elem.text.strip() if company_elem else "Unknown",
                                location="Remote",
                                job_url=link,
                                apply_url=link,
                                description="",
                                source="DailyRemote",
                                date_posted="Recent"
                            ))
                    except Exception as e:
                        continue
                        
            logger.info(f"DailyRemote: {len(jobs)} jobs")
        except Exception as e:
            logger.error(f"DailyRemote failed: {e}")
            
        return jobs

    def scrape_all(self, query: str, limit: int = 10) -> List[Job]:
        """Run all extra scrapers."""
        all_jobs = []
        all_jobs.extend(self.scrape_jobspresso(query, limit))
        all_jobs.extend(self.scrape_remote_io(query, limit))
        all_jobs.extend(self.scrape_dailyremote(query, limit))
        return all_jobs
