"""
Lead generation tool using advanced search techniques (dorking) and scraping.
Focuses on finding direct email contacts and recent needs based on resume skills.
"""
import logging
import requests
import re
import random
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup
from ddgs import DDGS
from models import Lead

class LeadScraperTool:
    def __init__(self):
        self.logger = logging.getLogger("LeadScraperTool")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def _extract_emails(self, text: str) -> List[str]:
        """Extract valid emails from text."""
        if not text: return []
        # Regex for standard emails, avoiding some common false positives
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(pattern, text)))

    def _determine_pain_points(self, text: str, skills: List[str]) -> str:
        """Analyze text to guess what they need help with."""
        text_lower = text.lower()
        needs = []
        if "urgent" in text_lower or "asap" in text_lower:
            needs.append("Immediate assistance needed")
        if "bug" in text_lower or "fix" in text_lower:
            needs.append("Debugging/Fixing existing code")
        if "build" in text_lower or "create" in text_lower:
            needs.append("New development")
        
        # Skill gaps
        for skill in skills[:3]: # Check top 3 skills
            if f"looking for {skill.lower()}" in text_lower:
                needs.append(f"Needs specific {skill} expertise")
                
        return ", ".join(needs) if needs else "General development help"

    def generate_dorks(self, skills: List[str]) -> List[str]:
        """Generate Google/DDG advanced search queries (dorks)."""
        dorks = []
        base_intent = [
            '"looking for a developer"', 
            '"looking for a freelancer"', 
            '"hiring" "email me"', 
            '"send your resume to"',
            '"looking for"',
            '"we are hiring"'
        ]
        
        # Combine skills with intent
        for skill in skills:
            for intent in base_intent:
                # Targeted dorks
                dorks.append(f'{intent} "{skill}" "@gmail.com" -job -apply') # Finding gmail contacts (often smaller leads)
                dorks.append(f'{intent} "{skill}" "@protonmail.com" -job')
                dorks.append(f'site:twitter.com {intent} "{skill}"') # Twitter leads
                dorks.append(f'site:linkedin.com/posts {intent} "{skill}" "@gmail.com"') # LinkedIn posts with personal emails
                
                # NEW: Freelance specific dorks
                dorks.append(f'"hiring freelance {skill}" "@gmail.com"')
                dorks.append(f'"looking for freelance {skill}" email me')
                dorks.append(f'site:reddit.com "hiring" "{skill}" "email me"')
                dorks.append(f'site:facebook.com "looking for {skill} developer" "email me"')
                
                # --- 15+ NEW SOURCES ADDED (Freelance & Communities) ---
                # 1. Communities
                dorks.append(f'site:discord.com "looking for {skill} developer" "dm me"')
                dorks.append(f'site:slack.com "hiring" "{skill}"') 
                dorks.append(f'site:indiehackers.com "hiring" "{skill}"')
                dorks.append(f'site:news.ycombinator.com "hiring" "{skill}"') # HackerNews
                dorks.append(f'site:dev.to "looking for {skill}" "contact"')
                
                # 2. Tech Blogs/Platforms
                dorks.append(f'site:medium.com "hiring" "{skill} developer" email')
                dorks.append(f'site:hashnode.com "hiring" "{skill}"')
                dorks.append(f'site:substack.com "hiring" "{skill}"')
                
                # 3. Creator Economy
                dorks.append(f'site:gumroad.com "looking for {skill}"')
                dorks.append(f'site:patreon.com "hiring" "{skill}"')
                
                # 4. Startup & Co-founder
                dorks.append(f'site:cofounderslab.com "looking for {skill}"')
                dorks.append(f'site:wellfound.com "hiring" "{skill}"')
                
                # 5. Remote Boards (Targeted)
                dorks.append(f'site:remoteok.com "hiring" "{skill}"')
                dorks.append(f'site:workingnomads.com "hiring" "{skill}"')
                dorks.append(f'site:weworkremotely.com "hiring" "{skill}"')
                
                # 6. Design/Frontend (if applicable)
                if any(x in skill.lower() for x in ['design', 'ui', 'ux', 'frontend', 'react', 'css']):
                    dorks.append(f'site:behance.net "hiring" "{skill}"')
                    dorks.append(f'site:dribbble.com "hiring" "{skill}"')

        return list(set(dorks)) # Deduplicate

    def scrape_leads(self, resume_skills: List[str], limit: int = 25) -> List[Lead]:
        """
        Main method to find leads using resume skills.
        """
        self.logger.info(f"Generating leads for skills: {resume_skills[:5]}...")
        leads = []
        dorks = self.generate_dorks(resume_skills)
        random.shuffle(dorks) # Mix it up
        
        # Use DDGS for dorking
        with DDGS() as ddgs:
            for dork in dorks[:10]: # Run top 10 generated dorks
                if len(leads) >= limit: break
                
                try:
                    self.logger.info(f"Running dork: {dork}")
                    results = ddgs.text(dork, max_results=10)
                    if results:
                        for r in results:
                            body = r.get('body', '') + " " + r.get('title', '')
                            emails = self._extract_emails(body)
                            
                            # Valid Lead if we found an email and it looks relevant
                            if emails:
                                email = emails[0]
                                # Basic filtering to avoid junk
                                if any(x in email for x in ['example.com', 'domain.com', 'wix']): continue
                                
                                pain_points = self._determine_pain_points(body, resume_skills)
                                
                                lead = Lead(
                                    company="Unknown / Independent",
                                    source=f"Web Search ({dork})",
                                    role_needed=f"Developer ({resume_skills[0]})",
                                    contact_email=email,
                                    pain_points=pain_points,
                                    profile_match=f"Matched on keywords found in search",
                                    url=r.get('href'),
                                    confidence_score=0.75 # Decent since email found in "hiring" context
                                )
                                leads.append(lead)
                                
                except Exception as e:
                    self.logger.warning(f"Dork search failed: {e}")
                    
        self.logger.info(f"Generated {len(leads)} leads via dorking.")
        return leads

    def scrape_product_hunt(self, limit: int = 10) -> List[Lead]:
        """Scrape new launches on Product Hunt (potential tech leads)."""
        leads = []
        try:
            url = "https://www.producthunt.com/posts/newest" # Or use an RSS feed if available
            # Note: PH is hard to scrape directly due to SPA (Single Page App) nature without browser.
            # Using a public RSS feed or simple parse if possible. 
            # Fallback: Use DDGS with site:producthunt.com
            
            with DDGS() as ddgs:
                query = 'site:producthunt.com/posts "hiring" "developer" after:2024-01-01'
                results = ddgs.text(query, max_results=limit)
                for r in results:
                     leads.append(Lead(
                        company=r.get('title').split('-')[0].strip(),
                        source="Product Hunt",
                        role_needed="Tech Support / Developer",
                        pain_points="New Product Launch - likely needs scaling/fixing",
                        url=r.get('href'),
                        confidence_score=0.60
                    ))
        except Exception as e:
             self.logger.error(f"Product Hunt scrape failed: {e}")
             
        return leads

