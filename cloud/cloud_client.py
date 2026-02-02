"""
Cloud Client for Resume Parsing
Connects to remote GPU server (Colab) with automatic fallback to local Ollama.

USAGE:
    from cloud.cloud_client import CloudClient
    
    client = CloudClient(server_url="https://your-ngrok-url.ngrok.io")
    result = client.parse_resume(resume_text)
"""

import os
import time
import requests
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger(__name__)


class CloudClient:
    """
    Client for remote GPU resume parsing with intelligent fallback
    """
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        timeout: int = 60,  # Increased for slow model generation
        max_retries: int = 2,
        enable_fallback: bool = True
    ):
        """
        Initialize cloud client
        
        Args:
            server_url: URL of the Colab GPU server (e.g., https://xxxx.ngrok.io)
                       If None, will read from environment variable COLAB_SERVER_URL
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts before fallback
            enable_fallback: If True, falls back to local Ollama on failure
        """
        self.server_url = server_url or os.getenv("COLAB_SERVER_URL")
        self.timeout = timeout
        self.max_retries = max_retries
        self.enable_fallback = enable_fallback
        
        # Track performance
        self._stats = {
            'cloud_success': 0,
            'cloud_failures': 0,
            'fallback_used': 0,
            'avg_cloud_time': 0.0,
            'avg_fallback_time': 0.0
        }
        
        logger.info(
            "cloud_client_initialized",
            server_url=self.server_url,
            fallback_enabled=self.enable_fallback
        )
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume using cloud GPU (with local fallback)
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Dictionary with extracted fields:
            {
                'projects': [...],
                'certifications': [...],
                'achievements': [...],
                'soft_skills': [...],
                'languages': [...],
                'domains': [...],
                'work_experience': [...],
                'profile_type': 'AI_ML_ENGINEER'
            }
        """
        log = logger.bind(method="parse_resume", text_length=len(resume_text))
        
        # Validate input
        if not resume_text or len(resume_text.strip()) < 100:
            log.error("input_too_short")
            raise ValueError("Resume text too short (min 100 chars)")
        
        # Try cloud first
        if self.server_url:
            try:
                return self._parse_cloud(resume_text)
            except Exception as e:
                log.warning("cloud_parsing_failed", error=str(e))
                self._stats['cloud_failures'] += 1
        else:
            log.warning("no_cloud_url", fallback="local")
        
        if self.enable_fallback:
            log.info("using_local_fallback")
            
            # Check if user has local GPU
            local_gpu_available = self._check_local_gpu()
            
            if local_gpu_available:
                print("\n🔄 Cloud OCR processing failed. Using Local GPU Brain...")
                print("   (Fast local processing with your GPU)")
            else:
                print("\n🔄 Cloud processing failed. Using Local CPU Brain (Ollama)...")
                print("   (Local AI fallback - this may take a moment)")
                
            self._stats['fallback_used'] += 1
            return self._parse_local(resume_text)
        else:
            raise RuntimeError("Cloud parsing failed and fallback is disabled")
    
    def _check_local_gpu(self) -> bool:
        """Check if local GPU is available for acceleration."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                logger.info("local_gpu_detected", gpu_name=gpu_name)
                return True
        except ImportError:
            pass
        except Exception as e:
            logger.warning("gpu_check_failed", error=str(e))
        return False
    
    def parse_resume_pdf(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """
        Parse resume PDF using cloud GPU with OCR
        
        Args:
            pdf_bytes: Raw PDF file bytes
            
        Returns:
            Dictionary with extracted fields (same as parse_resume)
            
        Raises:
            RuntimeError: If cloud parsing fails
        """
        import base64
        log = logger.bind(method="parse_resume_pdf", pdf_size=len(pdf_bytes))
        
        if not self.server_url:
            log.warning("no_cloud_url_for_pdf")
            raise RuntimeError("Cloud server URL not configured. Cannot process PDF without cloud.")
        
        start_time = time.time()
        url = f"{self.server_url.rstrip('/')}/parse_resume_pdf"
        
        # Encode PDF as base64
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        payload = {"pdf_base64": pdf_base64}
        
        # Retry logic
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                log.info("cloud_pdf_request_attempt", attempt=attempt)
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=120,  # Longer timeout for OCR
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
                
                result = response.json()
                
                if not result.get('success'):
                    raise RuntimeError(f"Server error: {result.get('error')}")
                
                processing_time = time.time() - start_time
                
                log.info(
                    "cloud_pdf_parsing_success",
                    total_time_seconds=processing_time,
                    ocr_used=result.get('ocr_used', False),
                    profile_type=result['data'].get('profile_type')
                )
                
                self._stats['cloud_success'] += 1
                return result['data']
            
            except requests.exceptions.Timeout:
                last_error = f"Timeout (attempt {attempt}/{self.max_retries})"
                log.warning("cloud_pdf_timeout", attempt=attempt)
                time.sleep(2)
            
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                log.warning("cloud_pdf_connection_error", attempt=attempt)
                time.sleep(2)
            
            except Exception as e:
                last_error = str(e)
                log.error("cloud_pdf_request_failed", attempt=attempt, error=str(e))
                break
        
        raise RuntimeError(f"Cloud PDF parsing failed: {last_error}")
    
    def _parse_cloud(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse using remote GPU server
        """
        log = logger.bind(method="_parse_cloud")
        start_time = time.time()
        
        url = f"{self.server_url.rstrip('/')}/parse_resume"
        payload = {"resume_text": resume_text}
        
        # Retry logic
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                log.info("cloud_request_attempt", attempt=attempt, url=url)
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                # Check HTTP status
                if response.status_code != 200:
                    raise RuntimeError(
                        f"HTTP {response.status_code}: {response.text}"
                    )
                
                # Parse response
                result = response.json()
                
                if not result.get('success'):
                    raise RuntimeError(f"Server error: {result.get('error')}")
                
                processing_time = time.time() - start_time
                server_time = result.get('processing_time_seconds', 0)
                
                # Update stats
                self._stats['cloud_success'] += 1
                self._update_avg('avg_cloud_time', processing_time)
                
                log.info(
                    "cloud_parsing_success",
                    total_time_seconds=processing_time,
                    server_time_seconds=server_time,
                    profile_type=result['data'].get('profile_type')
                )
                
                # Normalize: Flatten any nested objects to strings
                data = result['data']
                for key in ['projects', 'certifications', 'achievements', 'work_experience']:
                    if key in data and isinstance(data[key], list):
                        data[key] = [
                            str(item) if isinstance(item, dict) else item
                            for item in data[key]
                        ]
                
                return data
            
            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.timeout}s (attempt {attempt}/{self.max_retries})"
                log.warning("cloud_timeout", attempt=attempt)
                time.sleep(1)  # Brief pause before retry
            
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                log.warning("cloud_connection_error", attempt=attempt, error=str(e))
                time.sleep(1)
            
            except Exception as e:
                last_error = str(e)
                log.error("cloud_request_failed", attempt=attempt, error=str(e))
                break  # Don't retry on unexpected errors
        
        # All retries exhausted
        raise RuntimeError(f"Cloud parsing failed after {self.max_retries} attempts: {last_error}")
    
    def _parse_local(self, resume_text: str) -> Dict[str, Any]:
        """
        Fallback: Parse using local Ollama (gemma2:2b)
        """
        log = logger.bind(method="_parse_local")
        start_time = time.time()
        
        try:
            from langchain_ollama import ChatOllama
            import json
            
            log.info("local_ollama_started")
            
            llm = ChatOllama(
                model="gemma2:2b",
                base_url="http://localhost:11434",
                temperature=0
            )
            
            prompt = f"""You are an expert resume analyzer. Extract detailed information and return ONLY valid JSON with these exact keys:

{{
  "projects": ["list of notable projects with tech used"],
  "certifications": ["list of certifications/credentials"],
  "achievements": ["key accomplishments with metrics if available"],
  "soft_skills": ["leadership, communication, teamwork, etc."],
  "languages": ["English", "Spanish", etc.],
  "domains": ["SPECIFIC technical domains: AI/ML, Web Development, Cloud, DevOps, Mobile, Data Science, etc."],
  "work_experience": [
    {{
      "role": "job title",
      "company": "company name",
      "duration": "timeframe",
      "key_tech": ["main technologies used"]
    }}
  ],
  "profile_type": "MOST SPECIFIC: AI_ML_ENGINEER, WEB_DEVELOPER, FULLSTACK_ENGINEER, DATA_SCIENTIST, DEVOPS_ENGINEER, SOFTWARE_ENGINEER, or GENERAL"
}}

CRITICAL RULES:
1. Extract ONLY information explicitly stated in the resume
2. For "domains": List ALL technical specializations found (AI, Web Dev, Cloud, etc.)
3. For "work_experience": Extract up to 3 most recent roles with technologies
4. For "profile_type": Choose the MOST SPECIFIC category based on skills and experience
5. Do NOT hallucinate - if unsure, use empty list []
6. Return pure JSON only, no markdown

Resume Text:
{resume_text[:3000]}

JSON:"""

            response = llm.invoke(prompt)
            content = response.content.strip()
            
            # Clean potential markdown formatting
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            parsed = json.loads(content.strip())
            
            processing_time = time.time() - start_time
            self._update_avg('avg_fallback_time', processing_time)
            
            log.info(
                "local_parsing_success",
                processing_time_seconds=processing_time,
                profile_type=parsed.get('profile_type')
            )
            
            # Validate and normalize structure
            return {
                'projects': parsed.get('projects', [])[:5],
                'certifications': parsed.get('certifications', [])[:5],
                'achievements': parsed.get('achievements', [])[:5],
                'soft_skills': parsed.get('soft_skills', [])[:5],
                'languages': parsed.get('languages', [])[:3],
                'domains': parsed.get('domains', [])[:10],
                'work_experience': parsed.get('work_experience', [])[:3],
                'profile_type': parsed.get('profile_type', 'GENERAL')
            }
        
        except Exception as e:
            log.error("local_parsing_failed", error=str(e))
            # Return empty structure as last resort
            return {
                'projects': [],
                'certifications': [],
                'achievements': [],
                'soft_skills': [],
                'languages': [],
                'domains': [],
                'work_experience': [],
                'profile_type': 'GENERAL'
            }
    
    def _update_avg(self, stat_key: str, new_value: float):
        """Update rolling average for performance stats"""
        current = self._stats[stat_key]
        count = self._stats['cloud_success'] if 'cloud' in stat_key else self._stats['fallback_used']
        
        if count == 0:
            self._stats[stat_key] = new_value
        else:
            self._stats[stat_key] = (current * (count - 1) + new_value) / count
    
    def draft_email(self, job_title: str, company: str, job_description: str, 
                    resume_skills: list, resume_experience: int) -> Dict[str, str]:
        """
        Generate email draft using cloud GPU
        
        Args:
            job_title: Job title
            company: Company name
            job_description: Job description text
            resume_skills: List of candidate skills
            resume_experience: Years of experience
            
        Returns:
            Dictionary with 'subject' and 'body' keys
            
        Raises:
            RuntimeError: If cloud drafting fails
        """
        log = logger.bind(method="draft_email")
        
        if not self.server_url:
            raise RuntimeError("Cloud server URL not configured. Cannot draft email without cloud.")
        
        start_time = time.time()
        url = f"{self.server_url.rstrip('/')}/draft_email"
        payload = {
            "job_title": job_title,
            "company": company,
            "job_description": job_description,
            "resume_skills": resume_skills,
            "resume_experience": resume_experience
        }
        
        # Retry logic
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                log.info("cloud_email_request", attempt=attempt, company=company)
                
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"HTTP {response.status_code}: {response.text}")
                
                result = response.json()
                
                if not result.get('success'):
                    raise RuntimeError(f"Server error: {result.get('error')}")
                
                processing_time = time.time() - start_time
                
                log.info(
                    "cloud_email_success",
                    total_time_seconds=processing_time,
                    subject_length=len(result.get('subject', ''))
                )
                
                return {
                    'subject': result.get('subject', f'Application for {job_title}'),
                    'body': result.get('body', '')
                }
            
            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.timeout}s (attempt {attempt}/{self.max_retries})"
                log.warning("cloud_email_timeout", attempt=attempt)
                time.sleep(1)
            
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)}"
                log.warning("cloud_email_connection_error", attempt=attempt, error=str(e))
                time.sleep(1)
            
            except Exception as e:
                last_error = str(e)
                log.error("cloud_email_failed", attempt=attempt, error=str(e))
                break
        
        raise RuntimeError(f"Cloud email drafting failed after {self.max_retries} attempts: {last_error}")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if cloud server is reachable
        
        Returns:
            {
                'cloud_available': bool,
                'response_time_ms': float,
                'gpu_available': bool,
                'error': str or None
            }
        """
        if not self.server_url:
            return {
                'cloud_available': False,
                'response_time_ms': 0,
                'gpu_available': False,
                'error': 'No server URL configured'
            }
        
        try:
            start = time.time()
            response = requests.get(
                f"{self.server_url.rstrip('/')}/",
                timeout=5
            )
            response_time = (time.time() - start) * 1000
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'cloud_available': data.get('status') == 'online',
                    'response_time_ms': response_time,
                    'gpu_available': data.get('gpu_available', False),
                    'error': None
                }
            else:
                return {
                    'cloud_available': False,
                    'response_time_ms': response_time,
                    'gpu_available': False,
                    'error': f"HTTP {response.status_code}"
                }
        
        except Exception as e:
            return {
                'cloud_available': False,
                'response_time_ms': 0,
                'gpu_available': False,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics
        
        Returns:
            Dictionary with cloud/fallback usage stats
        """
        total = self._stats['cloud_success'] + self._stats['cloud_failures']
        return {
            **self._stats,
            'total_requests': total,
            'cloud_success_rate': (self._stats['cloud_success'] / total * 100) if total > 0 else 0,
            'speedup_factor': (
                self._stats['avg_fallback_time'] / self._stats['avg_cloud_time']
                if self._stats['avg_cloud_time'] > 0 else 0
            )
        }
    
    def _update_avg(self, key: str, new_value: float):
        """Update running average"""
        count_key = 'cloud_success' if 'cloud' in key else 'fallback_used'
        count = self._stats[count_key]
        
        if count == 1:
            self._stats[key] = new_value
        else:
            self._stats[key] = (
                (self._stats[key] * (count - 1) + new_value) / count
            )


# ==========================================
# Module-level convenience functions
# ==========================================

_default_client: Optional[CloudClient] = None


def get_client() -> CloudClient:
    """Get or create default CloudClient instance"""
    global _default_client
    if _default_client is None:
        _default_client = CloudClient()
    return _default_client


def parse_resume(resume_text: str, server_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for one-off parsing
    
    Args:
        resume_text: Raw resume text
        server_url: Optional server URL (overrides default)
        
    Returns:
        Extracted resume data
    """
    if server_url:
        client = CloudClient(server_url=server_url)
    else:
        client = get_client()
    
    return client.parse_resume(resume_text)
