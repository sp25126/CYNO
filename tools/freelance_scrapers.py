"""
Freelance platform scrapers.
Scrapes Freelancer, Upwork, Guru, PeoplePerHour, and Toptal.
HARDENED: Uses RequestManager for all HTTP calls.
"""
import logging
import re
from bs4 import BeautifulSoup
from typing import List, Optional
from models import Job
from datetime import datetime
from tools.request_manager import request_manager


class FreelanceScrapers:
    """Scrapers for major freelance platforms."""
    
    def __init__(self):
        self.logger = logging.getLogger("FreelanceScrapers")
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email from text using regex."""
        if not text:
            return None
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None
    
    def scrape_freelancer(self, query: str, limit: int = 15) -> List[Job]:
        """Scrape Freelancer.com projects."""
        jobs = []
        try:
            url = f"https://www.freelancer.com/jobs/{query.replace(' ', '-')}/"
            response = request_manager.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                project_cards = soup.find_all('div', class_='JobSearchCard-item')[:limit]
                
                for card in project_cards:
                    try:
                        title_elem = card.find('a', class_='JobSearchCard-primary-heading-link')
                        description_elem = card.find('p', class_='JobSearchCard-primary-description')
                        budget_elem = card.find('div', class_='JobSearchCard-primary-price')
                        
                        if title_elem:
                            description_text = description_elem.text.strip() if description_elem else ""
                            email = self._extract_email(description_text)
                            
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company="Freelancer.com Client",
                                location="Remote (Freelance)",
                                job_url=f"https://www.freelancer.com{title_elem['href']}",
                                apply_url=f"https://www.freelancer.com{title_elem['href']}",
                                description=description_text[:1000],
                                source="Freelancer.com",
                                salary_range=budget_elem.text.strip() if budget_elem else "Budget: TBD",
                                date_posted="Recent",
                                contact_email=email
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Freelancer project: {e}")
            
            self.logger.info(f"Freelancer.com: {len(jobs)} projects")
        except Exception as e:
            self.logger.error(f"Freelancer.com failed: {e}")
        
        return jobs
    
    def scrape_upwork_rss(self, query: str, limit: int = 15) -> List[Job]:
        """Scrape Upwork via RSS feed (public)."""
        jobs = []
        try:
            # Upwork has RSS feeds for searches
            url = f"https://www.upwork.com/ab/feed/jobs/rss?q={query.replace(' ', '+')}"
            response = request_manager.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')[:limit]
                
                for item in items:
                    try:
                        title = item.find('title').text if item.find('title') else "Upwork Project"
                        link = item.find('link').text if item.find('link') else ""
                        description = item.find('description').text if item.find('description') else ""
                        
                        # Extract budget from description
                        budget_match = re.search(r'\$[\d,]+', description)
                        budget = budget_match.group(0) if budget_match else "Budget: TBD"
                        
                        email = self._extract_email(description)
                        
                        jobs.append(Job(
                            title=title,
                            company="Upwork Client",
                            location="Remote (Freelance)",
                            job_url=link,
                            apply_url=link,
                            description=description[:1000],
                            source="Upwork (RSS)",
                            salary_range=budget,
                            date_posted="Recent",
                            contact_email=email
                        ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Upwork project: {e}")
            
            self.logger.info(f"Upwork: {len(jobs)} projects")
        except Exception as e:
            self.logger.error(f"Upwork failed: {e}")
        
        return jobs
    
    def scrape_guru(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Guru.com projects."""
        jobs = []
        try:
            url = f"https://www.guru.com/d/jobs/{query.replace(' ', '-')}/"
            response = request_manager.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                listings = soup.find_all('div', class_='jobListing')[:limit]
                
                for listing in listings:
                    try:
                        title_elem = listing.find('a', class_='jobTitle')
                        description_elem = listing.find('div', class_='jobDescription')
                        budget_elem = listing.find('span', class_='budget')
                        
                        if title_elem:
                            description_text = description_elem.text.strip() if description_elem else ""
                            email = self._extract_email(description_text)
                            
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company="Guru.com Client",
                                location="Remote (Freelance)",
                                job_url=f"https://www.guru.com{title_elem['href']}",
                                apply_url=f"https://www.guru.com{title_elem['href']}",
                                description=description_text[:1000],
                                source="Guru.com",
                                salary_range=budget_elem.text.strip() if budget_elem else "Budget: TBD",
                                date_posted="Recent",
                                contact_email=email
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Guru project: {e}")
            
            self.logger.info(f"Guru.com: {len(jobs)} projects")
        except Exception as e:
            self.logger.error(f"Guru.com failed: {e}")
        
        return jobs
    
    def scrape_peopleperhour(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape PeoplePerHour.com projects."""
        jobs = []
        try:
            url = f"https://www.peopleperhour.com/freelance-jobs?q={query.replace(' ', '+')}"
            response = request_manager.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                project_cards = soup.find_all('div', class_='project-card')[:limit]
                
                for card in project_cards:
                    try:
                        title_elem = card.find('h3')
                        description_elem = card.find('p', class_='description')
                        budget_elem = card.find('span', class_='budget')
                        link_elem = card.find('a')
                        
                        if title_elem and link_elem:
                            description_text = description_elem.text.strip() if description_elem else ""
                            email = self._extract_email(description_text)
                            
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company="PeoplePerHour Client",
                                location="Remote (Freelance)",
                                job_url=f"https://www.peopleperhour.com{link_elem['href']}",
                                apply_url=f"https://www.peopleperhour.com{link_elem['href']}",
                                description=description_text[:1000],
                                source="PeoplePerHour",
                                salary_range=budget_elem.text.strip() if budget_elem else "Budget: TBD",
                                date_posted="Recent",
                                contact_email=email
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse PeoplePerHour project: {e}")
            
            self.logger.info(f"PeoplePerHour: {len(jobs)} projects")
        except Exception as e:
            self.logger.error(f"PeoplePerHour failed: {e}")
        
        return jobs
    
    def scrape_toptal_jobs(self, query: str, limit: int = 10) -> List[Job]:
        """Scrape Toptal job board (companjes hiring via Toptal)."""
        jobs = []
        try:
            url = "https://www.toptal.com/developers/job-listings"
            response = request_manager.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                job_listings = soup.find_all('div', class_='job-listing')[:limit]
                
                for listing in job_listings:
                    try:
                        title_elem = listing.find('h3')
                        company_elem = listing.find('span', class_='company')
                        description_elem = listing.find('div', class_='description')
                        link_elem = listing.find('a')
                        
                        if title_elem and link_elem:
                            description_text = description_elem.text.strip() if description_elem else ""
                            email = self._extract_email(description_text)
                            
                            jobs.append(Job(
                                title=title_elem.text.strip(),
                                company=company_elem.text.strip() if company_elem else "Toptal Client",
                                location="Remote",
                                job_url=f"https://www.toptal.com{link_elem['href']}",
                                apply_url=f"https://www.toptal.com{link_elem['href']}",
                                description=description_text[:1000],
                                source="Toptal",
                                date_posted="Recent",
                                contact_email=email
                            ))
                    except Exception as e:
                        self.logger.warning(f"Failed to parse Toptal job: {e}")
            
            self.logger.info(f"Toptal: {len(jobs)} jobs")
        except Exception as e:
            self.logger.error(f"Toptal failed: {e}")
        
        return jobs
    
    def scrape_all(self, query: str, limit_per_site: int = 10) -> List[Job]:
        """Run all freelance scrapers."""
        all_jobs = []
        
        self.logger.info(f"Running freelance scrapers for: {query}")
        
        all_jobs.extend(self.scrape_upwork_rss(query, limit_per_site))
        all_jobs.extend(self.scrape_freelancer(query, limit_per_site))
        all_jobs.extend(self.scrape_guru(query, limit_per_site))
        all_jobs.extend(self.scrape_peopleperhour(query, limit_per_site))
        all_jobs.extend(self.scrape_toptal_jobs(query, limit_per_site))
        
        self.logger.info(f"Freelance scrapers total: {len(all_jobs)} projects from 5 platforms")
        return all_jobs
