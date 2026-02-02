import re
import structlog
from typing import Any, Dict, List
from models import Resume

logger = structlog.get_logger(__name__)

class ResumeParserTool:
    """
    Cloud-first resume parser with local fallback.
    Priority: Cloud Brain (Colab GPU) → Local GPU → Local CPU (Ollama)
    """

    def execute(self, text: str) -> Resume:
        """
        Parses raw resume text.
        
        Args:
            text: Raw string content of the resume.
            
        Returns:
            Resume: Structured resume object.
            
        Raises:
            ValueError: If text is too short (< 100 chars).
        """
        log = logger.bind(tool="ResumeParserTool")
        
        if not text:
            log.error("empty_input")
            raise ValueError("Resume text cannot be empty")
            
        if len(text.strip()) < 100:
            log.error("input_too_short", length=len(text))
            raise ValueError("Resume text is too short (min 100 chars required)")
            
        log.info("parsing_started", text_length=len(text))
        
        try:
            # 1. Extract Skills (regex-based, fast)
            skills = self._extract_skills(text)
            
            # 2. Extract Years of Experience
            years_exp = self._extract_years_exp(text)
            
            # 3. Extract Education Level
            education_level = self._extract_education_level(text)
            
            # 4. Extract Location
            location = self._extract_location(text)
            
            # 5. Extract Keywords (Top words)
            keywords = self._extract_keywords(text)
            
            # 6. Cloud/LLM-Enhanced Extraction (50+ fields)
            llm_data = self._llm_extract_detailed(text)
            
            resume = Resume(
                parsed_skills=skills,
                education_level=education_level,
                years_exp=years_exp,
                location=location,
                keywords=keywords,
                # LLM-enhanced fields (from Cloud or Local)
                projects=llm_data.get('projects', []),
                certifications=llm_data.get('certifications', []),
                achievements=llm_data.get('achievements', []),
                soft_skills=llm_data.get('soft_skills', []),
                languages=llm_data.get('languages', []),
                domains=llm_data.get('domains', []),
                work_experience=llm_data.get('work_experience', []),
                profile_type=llm_data.get('profile_type', 'GENERAL'),
                raw_text=text
            )
            
            log.info("parsing_success", 
                     skills_count=len(skills), 
                     years_exp=years_exp, 
                     location=location,
                     profile=llm_data.get('profile_type', 'GENERAL'))
            
            return resume
            
        except Exception as e:
            log.error("parsing_failed", error=str(e))
            raise e
    
    def _llm_extract_detailed(self, text: str) -> Dict[str, Any]:
        """
        Cloud-first LLM extraction with 3-tier fallback:
        1. Try Cloud Brain (Colab GPU)
        2. Try Local Ollama
        3. Return empty structure
        """
        # Try Cloud Brain first
        try:
            from cloud.cloud_client import get_client
            
            client = get_client()
            if client.server_url:
                try:
                    result = client.parse_resume(text)
                    logger.info("cloud_parsing_success", fields=len(result))
                    return result
                except Exception as e:
                    logger.warning("cloud_failed_fallback_local", error=str(e))
        except ImportError:
            logger.debug("cloud_client_not_available")
        
        # Fallback to local Ollama (Phase-5 logic)
        try:
            from langchain_ollama import ChatOllama
            import json
            
            llm = ChatOllama(model="gemma2:2b", base_url="http://localhost:11434", temperature=0)
            
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
{text[:3000]}

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
            logger.warning(f"LLM extraction failed: {e}. Using fallback.")
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

    def _extract_skills(self, text: str) -> List[str]:
        # Expanded skill list (from Phase-5)
        common_skills = [
            # Langs
            "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust", "Swift", "Kotlin", "PHP", "Ruby",
            # Frameworks/Libs
            "React", "Angular", "Vue", "Node.js", "Django", "FastAPI", "Flask", "Spring", "Rails", ".NET",
            # AI/ML
            "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "Pandas", "NumPy", "OpenCV", "LLM", "Generative AI",
            # Cloud/DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD",
            # DB
            "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
            # Soft
            "Leadership", "Agile", "Scrum", "Communication"
        ]
        
        found_skills = []
        for skill in common_skills:
            escaped_skill = re.escape(skill).replace(r'\ ', ' ')
            
            if re.match(r'^\w', skill):
                pattern_start = r'\b'
            else:
                pattern_start = r'(?<!\w)'
                
            if re.search(r'\w$', skill):
                pattern_end = r'\b'
            else:
                pattern_end = r'(?!\w)'
            
            pattern = rf'{pattern_start}{escaped_skill}{pattern_end}'
            
            if re.search(pattern, text, re.IGNORECASE):
                found_skills.append(skill)
        
        return list(set(found_skills)) if found_skills else ["General"]

    def _extract_years_exp(self, text: str) -> int:
        matches = re.findall(r'(\d+)\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
        if not matches:
            return 0
        
        years_list = [int(m) for m in matches]
        valid_years = [y for y in years_list if y < 60]
        
        return max(valid_years) if valid_years else 0

    def _extract_education_level(self, text: str) -> str:
        text_lower = text.lower()
        if re.search(r'\b(ph\.?d\.?|doctorates?)\b', text_lower):
            return "PHD"
        if re.search(r'\b(master\'?s?|m\.?s\.?|m\.?tech|m\.?b\.?a\.?)\b', text_lower):
            return "MASTERS"
        if re.search(r'\b(bachelor\'?s?|b\.?s\.?|b\.?a\.?|b\.?tech|b\.?eng)\b', text_lower):
            return "BACHELORS"
        if re.search(r'\b(high school|diploma)\b', text_lower):
            return "HIGH_SCHOOL"
            
        return "UNKNOWN"

    def _extract_location(self, text: str) -> str:
        loc_patterns = [
            r'Location:\s*([^\n]+)',
            r'Address:\s*([^\n]+)',
            r'City:\s*([^\n]+)',
            r'Residing in\s*([^\n]+)'
        ]
        
        for pattern in loc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                clean_loc = match.group(1).strip()
                if "http" not in clean_loc and "@" not in clean_loc:
                    return clean_loc
        
        major_cities = ["New York", "London", "San Francisco", "Bangalore", "Mumbai", "Delhi", "Berlin", "Toronto", "Remote"]
        for city in major_cities:
            if city.lower() in text.lower():
                return city
                
        return "Unknown"

    def _extract_keywords(self, text: str) -> List[str]:
        words = re.findall(r'\b\w{5,}\b', text.lower())
        stopwords = {"about", "their", "there", "would", "could", "should", "these", "those", "experience", "years", "months", "resume", "contact", "email", "phone"}
        filtered = [w for w in words if w not in stopwords]
        
        from collections import Counter
        counts = Counter(filtered)
        return [w for w, _ in counts.most_common(10)]
