import logging
import requests
import re
import random
import time
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
                
                # 2. Tech Blogs/Platforms (Expanded)
                dorks.append(f'site:medium.com "hiring" "{skill} developer" email')
                dorks.append(f'site:hashnode.com "hiring" "{skill}"')
                dorks.append(f'site:substack.com "hiring" "{skill}"')
                dorks.append(f'site:dev.to "looking for {skill}" "contact"')
                
                # 3. Creator Economy & Crowdfunding
                dorks.append(f'site:gumroad.com "looking for {skill}"')
                dorks.append(f'site:patreon.com "hiring" "{skill}"')
                dorks.append(f'site:kickstarter.com "hiring" "{skill}"')
                dorks.append(f'site:indiegogo.com "hiring" "{skill}"')
                
                # 4. Startup & Co-founder (Expanded)
                dorks.append(f'site:cofounderslab.com "looking for {skill}"')
                dorks.append(f'site:wellfound.com "hiring" "{skill}"')
                dorks.append(f'site:ycombinator.com "hiring" "{skill}"')
                dorks.append(f'site:producthunt.com "hiring" "{skill}"')
                dorks.append(f'site:betalist.com "hiring" "{skill}"')
                
                # 5. Remote Boards (Targeted)
                dorks.append(f'site:remoteok.com "hiring" "{skill}"')
                dorks.append(f'site:workingnomads.com "hiring" "{skill}"')
                dorks.append(f'site:weworkremotely.com "hiring" "{skill}"')
                dorks.append(f'site:upwork.com "looking for {skill}"')
                dorks.append(f'site:freelancer.com "looking for {skill}"')
                
                # 6. Social Media Deep Dives
                dorks.append(f'site:twitter.com "hiring {skill}" "dm open"')
                dorks.append(f'site:twitter.com "looking for {skill}" "email me"')
                dorks.append(f'site:linkedin.com/in "hiring {skill}" "email me"') # Profiles
                dorks.append(f'site:linkedin.com/posts "hiring {skill}" "@gmail.com"') # Posts
                dorks.append(f'site:facebook.com "hiring {skill} developer"')
                dorks.append(f'site:instagram.com "hiring {skill}" "dm"')
                dorks.append(f'site:threads.net "hiring {skill}"')
                
                # 7. Code Repos & Issues
                dorks.append(f'site:github.com "looking for contributors" "{skill}"')
                dorks.append(f'site:github.com "hiring" "{skill}"')
                dorks.append(f'site:gitlab.com "hiring" "{skill}"')
                
                # 8. Unconventional
                dorks.append(f'site:craigslist.org "hiring" "{skill}"')
                dorks.append(f'site:gumtree.com "hiring" "{skill}"')
                dorks.append(f'site:notion.site "hiring" "{skill}"') # Public notion pages
                
                # 9. Design/Frontend specifics
                if any(x in skill.lower() for x in ['design', 'ui', 'ux', 'frontend', 'react', 'css']):
                    dorks.append(f'site:behance.net "hiring" "{skill}"')
                    dorks.append(f'site:dribbble.com "hiring" "{skill}"')
                    dorks.append(f'site:awwwards.com "hiring" "{skill}"')

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
            # Boosted limits: Check up to 50 dorks, targeting 30 results each
            for i, dork in enumerate(dorks[:50]): 
                if len(leads) >= limit: break
                
                # Retry logic for rate limits
                for attempt in range(3):
                    try:
                        self.logger.info(f"Running dork ({i+1}): {dork}")
                        # Increased max_results to 30
                        results = ddgs.text(dork, max_results=30)
                        if results:
                            found_in_dork = 0
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
                                        confidence_score=0.75 
                                    )
                                    leads.append(lead)
                                    found_in_dork += 1
                            
                            self.logger.debug(f"Dork yielded {found_in_dork} leads.")
                        
                        break # Success, move to next dork
                        
                    except Exception as e:
                        # Handle Rate Limits
                        wait = 5 + (2 ** attempt)
                        self.logger.warning(f"Dork failed: {e}. Sleeping {wait}s...")
                        time.sleep(wait)
                
                # Politeness delay between dorks
                time.sleep(1)
                    
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

