"""
Robust Request Manager
Centralized handler for HTTP requests with hardening features:
- TLS Fingerprint Impersonation (curl_cffi) to bypass Cloudflare
- User-Agent Rotation
- Exponential Backoff (Manual Retry)
"""
import random
import time
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)

# Try importing curl_cffi for anti-bot bypass
try:
    from curl_cffi import requests as cffi_requests
    HAS_CFFI = True
except ImportError:
    HAS_CFFI = False
    logger.warning("curl-cffi not found. Falling back to standard requests (higher chance of 403s).")

# Common User-Agents (used if cffi unavailable or for rotation)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

class RequestManager:
    """Hardened HTTP client using TLS impersonation."""
    
    def __init__(self, use_proxies: bool = False):
        self.use_proxies = use_proxies
        # Initialize session
        if HAS_CFFI:
            # Impersonate Chrome 120 to bypass Cloudflare
            self.session = cffi_requests.Session(impersonate="chrome120")
        else:
            self.session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers (CFFI handles UA/TLS natively, but we add some extras)."""
        return {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
            "Cache-Control": "max-age=0",
        }
    
    def get(self, url: str, params: Optional[Dict] = None, timeout: int = 15, retries: int = 3, **kwargs) -> Optional[requests.Response]:
        """
        Hardened GET request with retries and TLS impersonation.
        """
        attempt = 0
        while attempt <= retries:
            try:
                # Add randomized jitter
                time.sleep(random.uniform(0.5, 1.5))
                
                headers = self._get_headers()
                if "headers" in kwargs:
                    headers.update(kwargs.pop("headers"))
                
                # Use CFFI or Requests
                # Note: cffi parameters are mostly compatible with requests
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                    **kwargs
                )
                
                # Check status
                if response.status_code == 200:
                    return response
                
                elif response.status_code in [429, 500, 502, 503, 504]:
                    # Retryable errors
                    logger.warning(f"⚠️ {response.status_code} on {url}. Retrying ({attempt+1}/{retries})...")
                    time.sleep(2 ** attempt) # Exponential backoff
                    attempt += 1
                    continue
                    
                elif response.status_code == 403:
                    logger.warning(f"🚫 Access denied (403) by {url}. TLS Bypass failed or IP blocked.")
                    return None
                    
                else:
                    logger.error(f"HTTP {response.status_code} on {url}")
                    return None

            except Exception as e:
                logger.error(f"Request failed: {e}")
                attempt += 1
                time.sleep(1)
        
        return None

# Singleton instance
request_manager = RequestManager()

