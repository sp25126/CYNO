"""
CYNO Enhanced Resume Parser v2.0
Deep LLM-Powered Resume Analysis with Cloud GPU
"""

import os
import re
import json
import structlog
import requests
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from models import Resume

logger = structlog.get_logger(__name__)


@dataclass
class ResumeAnalysis:
    """Comprehensive resume analysis result."""
    # Basic Info
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    
    # Professional Summary
    summary: str = ""
    years_experience: int = 0
    profile_type: str = "GENERAL"
    seniority_level: str = "MID"  # INTERN, JUNIOR, MID, SENIOR, LEAD, PRINCIPAL
    
    # Skills
    technical_skills: List[str] = field(default_factory=list)
    soft_skills: List[str] = field(default_factory=list)
    languages_spoken: List[str] = field(default_factory=list)
    
    # Experience
    work_experience: List[Dict] = field(default_factory=list)
    total_companies: int = 0
    industries: List[str] = field(default_factory=list)
    
    # Education
    education: List[Dict] = field(default_factory=list)
    highest_degree: str = ""
    
    # Projects & Achievements
    projects: List[Dict] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    publications: List[str] = field(default_factory=list)
    
    # Technical Analysis
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)
    domains: List[str] = field(default_factory=list)
    
    # AI-Generated Insights
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    career_trajectory: str = ""
    ideal_roles: List[str] = field(default_factory=list)
    salary_estimate: str = ""
    
    # Raw data
    keywords: List[str] = field(default_factory=list)
    raw_text: str = ""
    parsing_method: str = "regex"  # "cloud_llm", "local_llm", "regex"
    confidence_score: float = 0.0


class EnhancedResumeParser:
    """
    Advanced LLM-powered resume parser.
    Uses Cloud GPU for deep analysis with intelligent fallbacks.
    """
    
    def __init__(self):
        self.cloud_url = os.getenv("COLAB_SERVER_URL")
        self.log = logger.bind(tool="EnhancedResumeParser")
    
    def parse(self, text: str, deep_analysis: bool = True) -> ResumeAnalysis:
        """
        Parse resume with optional deep LLM analysis.
        
        Args:
            text: Raw resume text
            deep_analysis: If True, use Cloud GPU for comprehensive analysis
            
        Returns:
            ResumeAnalysis with all extracted fields
        """
        if not text or len(text.strip()) < 100:
            raise ValueError("Resume text is too short (min 100 chars)")
        
        self.log.info("parsing_started", text_length=len(text), deep=deep_analysis)
        
        # Start with basic regex extraction
        analysis = self._extract_basic_info(text)
        
        # If deep analysis requested, use Cloud LLM
        if deep_analysis:
            try:
                llm_result = self._deep_llm_analysis(text)
                analysis = self._merge_results(analysis, llm_result)
                analysis.parsing_method = "cloud_llm"
                analysis.confidence_score = 0.95
            except Exception as e:
                self.log.warning("cloud_analysis_failed", error=str(e))
                # Try local LLM
                try:
                    llm_result = self._local_llm_analysis(text)
                    analysis = self._merge_results(analysis, llm_result)
                    analysis.parsing_method = "local_llm"
                    analysis.confidence_score = 0.75
                except Exception as e2:
                    self.log.warning("local_llm_failed", error=str(e2))
                    analysis.parsing_method = "regex"
                    analysis.confidence_score = 0.5
        
        analysis.raw_text = text
        self.log.info("parsing_complete", method=analysis.parsing_method, confidence=analysis.confidence_score)
        
        return analysis
    
    def _deep_llm_analysis(self, text: str) -> Dict[str, Any]:
        """
        Use Cloud GPU for comprehensive resume analysis.
        Extracts 50+ fields with AI-generated insights.
        """
        if not self.cloud_url:
            raise RuntimeError("Cloud server not configured")
        
        # Comprehensive prompt for deep analysis
        prompt = f"""You are an expert HR analyst and resume parser with 20 years of experience.
Analyze this resume THOROUGHLY and extract ALL information.

RESUME TEXT:
{text[:4000]}

Extract and return VALID JSON with these EXACT keys:

{{
    "personal_info": {{
        "name": "full name",
        "email": "email if found",
        "phone": "phone if found",
        "location": "city, state/country",
        "linkedin": "linkedin url if found",
        "github": "github url if found",
        "portfolio": "portfolio/website if found"
    }},
    "professional_summary": {{
        "summary": "2-3 sentence professional summary",
        "years_experience": number,
        "profile_type": "AI_ML_ENGINEER|DATA_SCIENTIST|WEB_DEVELOPER|BACKEND_ENGINEER|FRONTEND_ENGINEER|FULLSTACK_ENGINEER|DEVOPS_ENGINEER|MOBILE_DEVELOPER|CLOUD_ARCHITECT|SOFTWARE_ENGINEER|GENERAL",
        "seniority_level": "INTERN|JUNIOR|MID|SENIOR|LEAD|PRINCIPAL",
        "career_trajectory": "description of career path"
    }},
    "skills": {{
        "technical": ["list of all technical skills"],
        "soft_skills": ["communication", "leadership", etc.],
        "languages_spoken": ["English", etc.],
        "tech_stack": {{
            "languages": ["Python", "JavaScript"],
            "frameworks": ["React", "Django"],
            "databases": ["PostgreSQL", "MongoDB"],
            "cloud": ["AWS", "GCP"],
            "devops": ["Docker", "Kubernetes"],
            "ai_ml": ["TensorFlow", "PyTorch"],
            "other": ["Git", "Linux"]
        }}
    }},
    "work_experience": [
        {{
            "role": "job title",
            "company": "company name",
            "duration": "Jan 2022 - Present",
            "location": "city",
            "responsibilities": ["key responsibility 1", "key responsibility 2"],
            "technologies": ["tech used"],
            "achievements": ["quantified achievement if available"]
        }}
    ],
    "education": [
        {{
            "degree": "Bachelor of Science in Computer Science",
            "institution": "University Name",
            "year": "2020",
            "gpa": "3.8/4.0 if mentioned"
        }}
    ],
    "projects": [
        {{
            "name": "project name",
            "description": "what it does",
            "technologies": ["tech used"],
            "impact": "metrics/results if available"
        }}
    ],
    "certifications": ["AWS Certified", etc.],
    "achievements": ["quantified achievements"],
    "publications": ["papers, articles if any"],
    "domains": ["AI/ML", "Web Development", "Cloud Computing", etc.],
    "industries": ["FinTech", "HealthTech", etc.],
    "ai_insights": {{
        "strengths": ["top 3-5 strengths based on resume"],
        "weaknesses": ["potential gaps or areas for improvement"],
        "ideal_roles": ["best-fit job titles"],
        "salary_estimate": "estimated salary range based on experience",
        "interview_topics": ["likely interview topics based on background"]
    }},
    "keywords": ["important keywords for ATS"]
}}

CRITICAL RULES:
1. Extract ONLY information that is ACTUALLY in the resume
2. For missing fields, use empty strings "" or empty arrays []
3. years_experience must be a NUMBER, not a string
4. Be specific with profile_type - don't default to GENERAL if there's evidence
5. Return PURE JSON only, no markdown, no explanation
6. Quantify achievements where possible (%, $, numbers)

JSON:"""

        # Execute on Cloud GPU
        url = f"{self.cloud_url.rstrip('/')}/exec"
        exec_code = f"""
prompt = '''{prompt}'''
inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to(model.device)
with torch.no_grad():
    outputs = model.generate(
        **inputs, 
        max_new_tokens=1500, 
        temperature=0.1, 
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id
    )
result = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(result)
"""
        
        response = requests.post(url, json={"code": exec_code}, timeout=90)
        if response.status_code != 200:
            raise RuntimeError(f"Cloud request failed: {response.status_code}")
        
        result = response.json()
        if not result.get("success"):
            raise RuntimeError(result.get("error", "Unknown error"))
        
        output = result.get("output", "")
        
        # Parse JSON from response
        try:
            start = output.find("{")
            end = output.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(output[start:end])
        except json.JSONDecodeError:
            pass
        
        raise RuntimeError("Failed to parse LLM output as JSON")
    
    def _local_llm_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback to local Ollama for analysis."""
        try:
            from langchain_ollama import ChatOllama
            
            llm = ChatOllama(model="gemma2:2b", base_url="http://localhost:11434", temperature=0)
            
            prompt = f"""Analyze this resume and extract information as JSON:

{text[:3000]}

Return JSON with: name, email, skills (list), years_experience (number), education, work_experience (list), projects (list), profile_type, summary.

JSON:"""
            
            response = llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
            
            return {}
        except Exception as e:
            self.log.error("local_llm_error", error=str(e))
            raise
    
    def _extract_basic_info(self, text: str) -> ResumeAnalysis:
        """Basic regex-based extraction."""
        analysis = ResumeAnalysis()
        
        # Email
        email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
        if email_match:
            analysis.email = email_match.group()
        
        # Phone
        phone_match = re.search(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', text)
        if phone_match:
            analysis.phone = phone_match.group()
        
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text, re.I)
        if linkedin_match:
            analysis.linkedin = linkedin_match.group()
        
        # GitHub
        github_match = re.search(r'github\.com/[\w-]+', text, re.I)
        if github_match:
            analysis.github = github_match.group()
        
        # Years of experience
        exp_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp|work)',
            r'(?:experience|exp|work)\s*[:\-]?\s*(\d+)\+?\s*years?',
        ]
        for pattern in exp_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                analysis.years_experience = int(match.group(1))
                break
        
        # Skills (comprehensive list)
        skill_keywords = [
            # Languages
            "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab",
            # Web
            "react", "vue", "angular", "next.js", "node.js", "express", "django", "flask", "fastapi", "spring", "rails",
            # Data/ML
            "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy", "spark", "hadoop", "airflow", "mlflow",
            # Cloud
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
            # Databases
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb", "cassandra",
            # Other
            "git", "linux", "api", "rest", "graphql", "microservices", "agile", "scrum"
        ]
        
        text_lower = text.lower()
        found_skills = []
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        analysis.technical_skills = found_skills
        
        # Education level
        if re.search(r'\b(ph\.?d|doctorate|doctoral)\b', text, re.I):
            analysis.highest_degree = "PhD"
        elif re.search(r'\b(master|m\.?s\.?|mba|m\.tech)\b', text, re.I):
            analysis.highest_degree = "Masters"
        elif re.search(r'\b(bachelor|b\.?s\.?|b\.?tech|b\.?e\.?)\b', text, re.I):
            analysis.highest_degree = "Bachelors"
        
        # Location
        location_patterns = [
            r'(?:located in|based in|location[:\s]+)([A-Za-z\s,]+)',
            r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, STATE
        ]
        for pattern in location_patterns:
            match = re.search(pattern, text)
            if match:
                analysis.location = match.group(1).strip()
                break
        
        # Extract keywords (top words)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text)
        word_freq = {}
        for word in words:
            w = word.lower()
            word_freq[w] = word_freq.get(w, 0) + 1
        
        # Sort by frequency, exclude common words
        common = {"that", "this", "with", "from", "have", "been", "were", "will", "your", "more", "about", "which"}
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        analysis.keywords = [w for w, c in sorted_words[:20] if w not in common]
        
        return analysis
    
    def _merge_results(self, base: ResumeAnalysis, llm_data: Dict) -> ResumeAnalysis:
        """Merge LLM results into base analysis."""
        if not llm_data:
            return base
        
        # Personal info
        personal = llm_data.get("personal_info", {})
        if personal.get("name"):
            base.name = personal["name"]
        if personal.get("email"):
            base.email = personal["email"]
        if personal.get("location"):
            base.location = personal["location"]
        if personal.get("linkedin"):
            base.linkedin = personal["linkedin"]
        if personal.get("github"):
            base.github = personal["github"]
        if personal.get("portfolio"):
            base.portfolio = personal["portfolio"]
        
        # Professional summary
        prof = llm_data.get("professional_summary", {})
        if prof.get("summary"):
            base.summary = prof["summary"]
        if prof.get("years_experience"):
            try:
                base.years_experience = int(prof["years_experience"])
            except:
                pass
        if prof.get("profile_type"):
            base.profile_type = prof["profile_type"]
        if prof.get("seniority_level"):
            base.seniority_level = prof["seniority_level"]
        if prof.get("career_trajectory"):
            base.career_trajectory = prof["career_trajectory"]
        
        # Skills
        skills = llm_data.get("skills", {})
        if skills.get("technical"):
            base.technical_skills = list(set(base.technical_skills + skills["technical"]))
        if skills.get("soft_skills"):
            base.soft_skills = skills["soft_skills"]
        if skills.get("languages_spoken"):
            base.languages_spoken = skills["languages_spoken"]
        if skills.get("tech_stack"):
            base.tech_stack = skills["tech_stack"]
        
        # Experience
        if llm_data.get("work_experience"):
            base.work_experience = llm_data["work_experience"]
            base.total_companies = len(llm_data["work_experience"])
        
        # Education
        if llm_data.get("education"):
            base.education = llm_data["education"]
            if llm_data["education"] and llm_data["education"][0].get("degree"):
                base.highest_degree = llm_data["education"][0]["degree"]
        
        # Projects & achievements
        if llm_data.get("projects"):
            base.projects = llm_data["projects"]
        if llm_data.get("certifications"):
            base.certifications = llm_data["certifications"]
        if llm_data.get("achievements"):
            base.achievements = llm_data["achievements"]
        if llm_data.get("publications"):
            base.publications = llm_data["publications"]
        
        # Domains & industries
        if llm_data.get("domains"):
            base.domains = llm_data["domains"]
        if llm_data.get("industries"):
            base.industries = llm_data["industries"]
        
        # AI insights
        insights = llm_data.get("ai_insights", {})
        if insights.get("strengths"):
            base.strengths = insights["strengths"]
        if insights.get("weaknesses"):
            base.weaknesses = insights["weaknesses"]
        if insights.get("ideal_roles"):
            base.ideal_roles = insights["ideal_roles"]
        if insights.get("salary_estimate"):
            base.salary_estimate = insights["salary_estimate"]
        
        # Keywords
        if llm_data.get("keywords"):
            base.keywords = list(set(base.keywords + llm_data["keywords"]))
        
        return base
    
    def to_resume_model(self, analysis: ResumeAnalysis) -> Resume:
        """Convert ResumeAnalysis to Resume model for compatibility."""
        return Resume(
            parsed_skills=analysis.technical_skills,
            education_level=analysis.highest_degree,
            years_exp=analysis.years_experience,
            location=analysis.location,
            keywords=analysis.keywords,
            projects=[p.get("name", "") for p in analysis.projects],
            certifications=analysis.certifications,
            achievements=analysis.achievements,
            soft_skills=analysis.soft_skills,
            languages=analysis.languages_spoken,
            domains=analysis.domains,
            work_experience=analysis.work_experience,
            profile_type=analysis.profile_type,
            raw_text=analysis.raw_text
        )


class LLMPoweredAnalyzer:
    """
    General-purpose LLM analyzer for any text analysis task.
    Uses Cloud GPU for fast inference.
    """
    
    def __init__(self):
        self.cloud_url = os.getenv("COLAB_SERVER_URL")
        self.log = logger.bind(tool="LLMAnalyzer")
    
    def analyze(
        self,
        text: str,
        task: str,
        output_format: str = "json",
        max_tokens: int = 1000,
        temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        General-purpose text analysis with Cloud GPU.
        
        Args:
            text: Text to analyze
            task: Description of what to extract/analyze
            output_format: "json", "text", or "list"
            max_tokens: Maximum tokens to generate
            temperature: Creativity (0.0-1.0)
            
        Returns:
            Analysis result
        """
        self.log.info("analyzing", task=task[:50], text_length=len(text))
        
        if output_format == "json":
            format_instruction = "Return ONLY valid JSON, no markdown, no explanation."
        elif output_format == "list":
            format_instruction = "Return results as a numbered list."
        else:
            format_instruction = "Return plain text response."
        
        prompt = f"""Task: {task}

{format_instruction}

TEXT TO ANALYZE:
{text[:5000]}

RESPONSE:"""

        # Try Cloud GPU
        if self.cloud_url:
            try:
                return self._cloud_analyze(prompt, max_tokens, temperature, output_format)
            except Exception as e:
                self.log.warning("cloud_failed", error=str(e))
        
        # Fallback to local
        try:
            return self._local_analyze(prompt, output_format)
        except Exception as e:
            self.log.error("analysis_failed", error=str(e))
            return {"success": False, "error": str(e)}
    
    def _cloud_analyze(self, prompt: str, max_tokens: int, temperature: float, output_format: str) -> Dict:
        """Execute analysis on Cloud GPU."""
        url = f"{self.cloud_url.rstrip('/')}/exec"
        
        exec_code = f"""
prompt = '''{prompt}'''
inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=5000).to(model.device)
with torch.no_grad():
    outputs = model.generate(
        **inputs, 
        max_new_tokens={max_tokens}, 
        temperature={temperature}, 
        do_sample=True,
        pad_token_id=tokenizer.pad_token_id
    )
result = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(result)
"""
        
        response = requests.post(url, json={"code": exec_code}, timeout=60)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                output = result.get("output", "").strip()
                
                if output_format == "json":
                    try:
                        start = output.find("{")
                        end = output.rfind("}") + 1
                        if start != -1 and end > start:
                            return {"success": True, "result": json.loads(output[start:end])}
                        
                        # Try array
                        start = output.find("[")
                        end = output.rfind("]") + 1
                        if start != -1 and end > start:
                            return {"success": True, "result": json.loads(output[start:end])}
                    except json.JSONDecodeError:
                        pass
                
                return {"success": True, "result": output}
            else:
                raise RuntimeError(result.get("error", "Unknown error"))
        
        raise RuntimeError(f"Cloud request failed: {response.status_code}")
    
    def _local_analyze(self, prompt: str, output_format: str) -> Dict:
        """Fallback to local Ollama."""
        from langchain_ollama import ChatOllama
        
        llm = ChatOllama(model="gemma2:2b", base_url="http://localhost:11434", temperature=0)
        response = llm.invoke(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        if output_format == "json":
            try:
                start = content.find("{")
                end = content.rfind("}") + 1
                if start != -1 and end > start:
                    return {"success": True, "result": json.loads(content[start:end])}
            except:
                pass
        
        return {"success": True, "result": content}
    
    def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize text concisely."""
        result = self.analyze(
            text,
            f"Summarize this text in {max_length} words or less. Be concise and capture key points.",
            output_format="text",
            max_tokens=max_length * 2
        )
        return result.get("result", "")
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        result = self.analyze(
            text,
            "Extract all named entities and return JSON with keys: people, organizations, locations, technologies, dates",
            output_format="json"
        )
        return result.get("result", {})
    
    def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text."""
        result = self.analyze(
            text,
            "Analyze the sentiment of this text. Return JSON with: sentiment (positive/negative/neutral), score (0.0-1.0), key_phrases (list of important phrases)",
            output_format="json"
        )
        return result.get("result", {})
    
    def compare_texts(self, text1: str, text2: str) -> Dict[str, Any]:
        """Compare two texts (e.g., resume vs job description)."""
        combined = f"TEXT 1:\n{text1[:2000]}\n\nTEXT 2:\n{text2[:2000]}"
        result = self.analyze(
            combined,
            """Compare these two texts and return JSON with:
            - similarity_score (0.0-1.0)
            - matching_keywords (list)
            - missing_from_text1 (list of things in text2 but not text1)
            - recommendations (list of suggestions)""",
            output_format="json"
        )
        return result.get("result", {})


# Convenience functions
def parse_resume(text: str, deep: bool = True) -> ResumeAnalysis:
    """Quick function to parse a resume."""
    parser = EnhancedResumeParser()
    return parser.parse(text, deep_analysis=deep)


def analyze_text(text: str, task: str) -> Dict:
    """Quick function for general text analysis."""
    analyzer = LLMPoweredAnalyzer()
    return analyzer.analyze(text, task)


# Registration
def register_enhanced_parsers():
    """Register enhanced parsers in the tool registry."""
    from tools.registry import ToolRegistry
    ToolRegistry.register_instance("enhanced_resume_parser", EnhancedResumeParser)
    ToolRegistry.register_instance("llm_analyzer", LLMPoweredAnalyzer)
