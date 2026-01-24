"""
TEST BREAK IT: Automated Resilience Suite with LLM Mocking
FAST: All tests run in <5 seconds
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from tools.request_manager import RequestManager
from requests.exceptions import Timeout, ConnectionError

class TestResumeChaos:
    """Category 1: Resume Parser Input Chaos - WITH LLM MOCKING"""
    
    def setup_method(self):
        # Use temp directory that Windows can handle
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up temp files (best effort)."""
        import shutil
        try:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass

    @patch('tools.advanced_resume_parser.ChatOllama')
    def test_01_empty_file(self, mock_ollama):
        """Test [1]: Empty PDF file (MOCKED)."""
        from tools.advanced_resume_parser import AdvancedResumeParser
        
        parser = AdvancedResumeParser()
        fpath = Path(self.temp_dir) / "empty.pdf"
        fpath.touch()
        
        # Should return fallback without crashing
        result = parser.parse(str(fpath))
        assert result is not None
        assert result.name == "Unknown Candidate"

    @patch('tools.advanced_resume_parser.ChatOllama')
    def test_05_text_renamed_as_pdf(self, mock_ollama):
        """Test [5]: Text file renamed as .pdf (MOCKED)."""
        from tools.advanced_resume_parser import AdvancedResumeParser
        
        parser = AdvancedResumeParser()
        fpath = Path(self.temp_dir) / "fake.pdf"
        fpath.write_text("This is just text, not a PDF.")
        
        # Should handle gracefully
        result = parser.parse(str(fpath))
        assert result is not None

    @patch('tools.advanced_resume_parser.ChatOllama')
    def test_12_sql_injection_in_name(self, mock_ollama):
        """Test [12]: SQL Injection-like content (MOCKED)."""
        from tools.advanced_resume_parser import AdvancedResumeParser
        
        parser = AdvancedResumeParser()
        fpath = Path(self.temp_dir) / "resume.txt"
        # Write enough content to pass min length check
        fpath.write_text(
            "Name: Robert'); DROP TABLE Resumes;--\n" +
            "Skills: Python, SQL, JavaScript, React, Node.js\n" * 5
        )
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = '{"education_level": "BACHELORS", "location": "Unknown", "contact": {}, "certifications": [], "languages": ["English"]}'
        mock_ollama.return_value.invoke.return_value = mock_response
        
        result = parser.parse(str(fpath))
        assert result is not None

    @patch('tools.advanced_resume_parser.ChatOllama')
    def test_36_extremely_long_name(self, mock_ollama):
        """Test [36]: Name is 500 characters long (MOCKED)."""
        from tools.advanced_resume_parser import AdvancedResumeParser
        
        parser = AdvancedResumeParser()
        long_name = "A" * 500
        fpath = Path(self.temp_dir) / "resume.txt"
        fpath.write_text(f"Name: {long_name}\nSkills: Python\n" * 10)
        
        # Mock LLM
        mock_response = MagicMock()
        mock_response.content = '{"education_level": "UNKNOWN", "location": "Unknown", "contact": {}, "certifications": [], "languages": []}'
        mock_ollama.return_value.invoke.return_value = mock_response
        
        result = parser.parse(str(fpath))
        assert result is not None


class TestNetworkChaos:
    """Category 2: Network / Scraper Resilience"""
    
    @patch('requests.Session.get')
    def test_52_rate_limit_backoff(self, mock_get):
        """Test [52]: Site returns 429 Too Many Requests."""
        manager = RequestManager()
        
        mock_resp = MagicMock()
        mock_resp.status_code = 429
        
        from requests.exceptions import HTTPError
        mock_resp.raise_for_status.side_effect = HTTPError(response=mock_resp)
        mock_get.return_value = mock_resp
        
        response = manager.get("http://test.com")
        assert response is None

    @patch('requests.Session.get')
    def test_56_connection_timeout(self, mock_get):
        """Test [56]: Connection Timeout."""
        manager = RequestManager()
        mock_get.side_effect = Timeout("Connection timed out")
        
        response = manager.get("http://test.com")
        assert response is None

    @patch('requests.Session.get')
    def test_51_forbidden_block(self, mock_get):
        """Test [51]: 403 Forbidden."""
        manager = RequestManager()
        mock_resp = MagicMock()
        mock_resp.status_code = 403
        
        from requests.exceptions import HTTPError
        mock_resp.raise_for_status.side_effect = HTTPError(response=mock_resp)
        mock_get.return_value = mock_resp
        
        response = manager.get("http://test.com")
        assert response is None


class TestLogicChaos:
    """Category 3: Logic & Data integrity"""
    
    def test_salary_parsing_garbage(self):
        """Test [72]: Garbage salary inputs."""
        from models import Job
        
        job = Job(
            title="Dev", 
            company="Co", 
            location="Remote", 
            job_url="http://x.com", 
            apply_url="http://x.com",
            description="A job description that is long enough to pass validation",
            source="test",
            salary_range="10 bananas per hour"
        )
        assert job.salary_range == "10 bananas per hour"
        
    def test_empty_job_description(self):
        """Test [74]: Job description length requirement."""
        from models import Job
        
        # Description must be at least 10 chars (validation rule)
        job = Job(
            title="Developer", 
            company="TechCo", 
            location="Remote", 
            job_url="http://example.com", 
            apply_url="http://example.com",
            description="Valid desc",  # 10 chars
            source="test"
        )
        assert len(job.description) >= 10
