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

    def search_domains(self, query: str, domains: List[str], limit_per_domain: int = 5) -> List[Job]:
        """
        Massive scan of specific domains using DuckDuckGo.
        Efficiently groups domains into OR queries to stay within API limits.
        """
        results = []
        import time
        from duckduckgo_search import DDGS
        
        # Chunk domains to avoid query too long errors (e.g. 3 at a time)
        # Using 3 per batch is safer for DDG API limits
        chunk_size = 3
        domain_chunks = [domains[i:i + chunk_size] for i in range(0, len(domains), chunk_size)]
        
        self.logger.info(f"Hybrid Search: Scanning {len(domains)} sites in {len(domain_chunks)} batches...")
        
        with DDGS() as ddgs:
            for i, chunk in enumerate(domain_chunks):
                try:
                    site_query = " OR ".join([f"site:{d}" for d in chunk])
                    full_query = f"{query} ({site_query})"
                    
                    # We want enough results to cover the chunk
                    max_res = limit_per_domain * len(chunk)
                    
                    # Exponential backoff retry
                    for attempt in range(3):
                        try:
                            ddg_gen = ddgs.text(full_query, region='us-en', max_results=max_res)
                            if ddg_gen:
                                found_in_batch = 0
                                for r in ddg_gen:
                                    url = r.get('href', '')
                                    # Basic verification it belongs to one of our sites
                                    if any(d in url for d in chunk):
                                        
                                        # Deduce company/source from URL
                                        source_domain = "Unknown"
                                        for d in chunk:
                                            if d in url:
                                                source_domain = d
                                                break
                                        
                                        results.append(Job(
                                            title=r.get('title', 'Unknown Role'),
                                            company=source_domain.split('.')[0].capitalize(),
                                            location="Remote / Listed",
                                            job_url=url,
                                            apply_url=url,
                                            description=r.get('body', '')[:500],
                                            source=f"Direct ({source_domain})",
                                            date_posted="Recent"
                                        ))
                                        found_in_batch += 1
                                
                            break # Success
                        except Exception as e:
                            # 202 Ratelimits need a cooldown
                            wait_time = 5 + (2 ** attempt)
                            self.logger.warning(f"Batch {i+1} warning: {e}. Sleeping {wait_time}s...")
                            time.sleep(wait_time)
                    
                    time.sleep(0.5) # Politeness delay
                    
                except Exception as e:
                    continue

        self.logger.info(f"Hybrid Search found {len(results)} matches from {len(domains)} sites.")
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
