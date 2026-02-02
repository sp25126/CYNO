import logging
from ddgs import DDGS
from bs4 import BeautifulSoup
import requests
import asyncio
from models import Job
from typing import List, Optional

class SiteSearchTool:
    def __init__(self):
        self.logger = logging.getLogger("SiteSearchTool")
        # Generic headers to look like a browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def search_domains(self, query: str, domains: List[str], limit_per_domain: int = 2) -> List[Job]:
        """
        Meta-search loop: For each domain, run `site:domain.com {query}` via DDGS.
        """
        results = []
        self.logger.info(f"Hybrid Search: Scanning {len(domains)} domains for '{query}'...")
        
        # We can't hit 500 domains in one go without being banned or taking forever.
        # Strategy: Randomly sample 20 domains OR search relevant ones.
        # For now, we will query them in batches or use a unified "site:A OR site:B" query if query length permits.
        
        # Better Strategy: Combined Query for groups of 10 domains
        # "python job (site:a.com OR site:b.com OR ...)"
        
        chunk_size = 10
        chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]
        
        # Limit total batches to avoid 5 min search
        max_batches = 5 
        
        with DDGS() as ddgs:
            count = 0
            for chunk in chunks[:max_batches]:
                site_query = " OR ".join([f"site:{d}" for d in chunk])
                full_query = f"{query} ({site_query})"
                
                try:
                    # search
                    gen = ddgs.text(full_query, region='us-en', max_results=10)
                    if gen:
                        for r in gen:
                            title = r.get('title', 'Unknown Role')
                            link = r.get('href', '')
                            snippet = r.get('body', '')
                            
                            # Simple filter: Link must look like a job
                            if any(k in link.lower() for k in ["job", "career", "legacy", "openings", "apply", "work"]):
                                
                                # Try to extract Company from domain
                                domain = link.split('/')[2].replace('www.', '')
                                
                                results.append(Job(
                                    title=title,
                                    company=domain.split('.')[0].capitalize(), # Rough guess
                                    location="Remote (Assumed from Source)",
                                    job_url=link,
                                    apply_url=link,
                                    description=f"Source: {domain}\nSnippet: {snippet}",
                                    source=f"Direct ({domain})",
                                    date_posted="Recent"
                                ))
                except Exception as e:
                    self.logger.warning(f"Batch search failed: {e}")
                
        self.logger.info(f"Hybrid Search found {len(results)} raw results.")
        return results

    def fetch_page_details(self, url: str) -> Optional[str]:
        """
        Uses BS4 to get the main text from a page.
        """
        try:
            resp = requests.get(url, headers=self.headers, timeout=5)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")
                # Remove scripts and styles
                for s in soup(["script", "style", "nav", "footer"]):
                    s.decompose()
                return soup.get_text(separator="\n", strip=True)[:3000] # Limit length
        except Exception:
            return None
        return None
