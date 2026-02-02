"""
CYNO Application Enhancement Tools
Cover Letter Generator, ATS Scorer, Skill Gap Analyzer
"""

import os
import json
import re
import requests
import structlog
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


class CoverLetterGeneratorTool:
    """
    Tool #6: Generate personalized cover letters using Cloud GPU.
    """
    
    def __init__(self):
        pass  # Uses unified LLM Brain
    
    def execute(
        self,
        job_title: str,
        company: str,
        job_description: str,
        resume_data: Dict[str, Any],
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """
        Generate a personalized cover letter.
        Uses unified LLM Brain (Cloud GPU or Local Ollama - same prompts).
        
        Args:
            job_title: Target job title
            company: Company name
            job_description: Full job description
            resume_data: Parsed resume data
            tone: 'professional', 'enthusiastic', 'formal'
            
        Returns:
            Dictionary with cover letter content
        """
        log = logger.bind(tool="CoverLetterGenerator", company=company)
        log.info("generating_cover_letter")
        
        # Extract key info from resume
        skills = resume_data.get("skills", []) or resume_data.get("parsed_skills", [])
        experience = resume_data.get("years_exp", 0)
        projects = resume_data.get("projects", [])
        
        # Try LLM Brain (Cloud or Local)
        try:
            return self._generate_llm(
                job_title, company, job_description,
                skills, experience, projects, tone
            )
        except Exception as e:
            log.warning("llm_failed", error=str(e))
        
        # Fallback to template
        return self._generate_template(
            job_title, company, job_description,
            skills, experience, projects, tone
        )
    
    def _generate_llm(
        self,
        job_title: str,
        company: str,
        job_description: str,
        skills: List[str],
        experience: int,
        projects: List,
        tone: str
    ) -> Dict[str, Any]:
        """Generate cover letter using LLM Brain (Cloud or Local)."""
        try:
            from agent.llm_brain import get_brain
            brain = get_brain()
        except ImportError:
            raise RuntimeError("LLM Brain not available")
        
        prompt = f"""Write a compelling cover letter for this job application.

JOB DETAILS:
- Position: {job_title}
- Company: {company}
- Description: {job_description[:500]}

CANDIDATE:
- Skills: {', '.join(skills[:10])}
- Experience: {experience} years
- Notable Projects: {', '.join(str(p) for p in projects[:3]) if projects else 'Various projects'}

TONE: {tone}

REQUIREMENTS:
1. Address to "Dear Hiring Manager" or "Dear [Company] Team"
2. Opening: Express genuine interest in the specific role
3. Body: Connect 2-3 specific skills to job requirements
4. Include a brief achievement or project mention
5. Closing: Express enthusiasm for interview opportunity
6. Keep it under 350 words
7. Do NOT include placeholders like [Your Name]

COVER LETTER:"""

        result = brain.generate(prompt, max_tokens=600, temperature=0.4, output_format="text")
        
        if result.get("success"):
            cover_letter = result.get("result", "").strip()
            return {
                "success": True,
                "cover_letter": cover_letter,
                "word_count": len(cover_letter.split()),
                "generated_by": result.get("backend", "llm"),
                "time_seconds": result.get("time_seconds", 0)
            }
        
        raise RuntimeError("LLM generation failed")
    
    def _generate_template(
        self,
        job_title: str,
        company: str,
        job_description: str,
        skills: List[str],
        experience: int,
        projects: List,
        tone: str
    ) -> Dict[str, Any]:
        """Generate cover letter using template."""
        
        # Match skills to job description
        jd_lower = job_description.lower()
        matched_skills = [s for s in skills if s.lower() in jd_lower][:3]
        
        cover_letter = f"""Dear {company} Hiring Team,

I am writing to express my strong interest in the {job_title} position at {company}. With {experience} years of experience and expertise in {', '.join(matched_skills) if matched_skills else ', '.join(skills[:3])}, I am confident in my ability to contribute meaningfully to your team.

Throughout my career, I have developed strong skills in {', '.join(skills[:5])}. {"I have worked on projects including " + ', '.join(str(p) for p in projects[:2]) + ", which have given me practical experience in solving real-world challenges." if projects else "I have consistently delivered high-quality work while collaborating effectively with cross-functional teams."}

I am particularly drawn to {company} because of its reputation for innovation and excellence. I am excited about the opportunity to bring my skills and passion to your team and contribute to your continued success.

I would welcome the opportunity to discuss how my background and skills would be a strong fit for this role. Thank you for considering my application.

Best regards"""

        return {
            "success": True,
            "cover_letter": cover_letter,
            "word_count": len(cover_letter.split()),
            "generated_by": "template",
            "matched_skills": matched_skills
        }


class ATSScorerTool:
    """
    Tool #8: Score resume against job description for ATS compatibility.
    """
    
    def execute(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        """
        Score resume against job description.
        
        Args:
            resume_text: Full resume text
            job_description: Job description text
            
        Returns:
            ATS compatibility score and recommendations
        """
        log = logger.bind(tool="ATSScorer")
        log.info("scoring_resume")
        
        # Extract keywords from job description
        jd_keywords = self._extract_keywords(job_description)
        resume_keywords = self._extract_keywords(resume_text)
        
        # Calculate match
        matched = [kw for kw in jd_keywords if kw in resume_keywords]
        missing = [kw for kw in jd_keywords if kw not in resume_keywords]
        
        # Calculate scores
        keyword_match_rate = len(matched) / len(jd_keywords) if jd_keywords else 0
        
        # Check formatting issues
        formatting_issues = self._check_formatting(resume_text)
        
        # Calculate final score
        base_score = keyword_match_rate * 70  # 70% weight on keywords
        formatting_penalty = len(formatting_issues) * 5  # -5 per issue
        final_score = max(0, min(100, base_score + 30 - formatting_penalty))
        
        return {
            "success": True,
            "score": round(final_score, 1),
            "keyword_match_rate": round(keyword_match_rate * 100, 1),
            "matched_keywords": matched[:15],
            "missing_keywords": missing[:10],
            "formatting_issues": formatting_issues,
            "recommendations": self._generate_recommendations(missing, formatting_issues, final_score),
            "grade": self._get_grade(final_score)
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Common tech skills and keywords
        tech_keywords = [
            "python", "javascript", "typescript", "java", "c++", "go", "rust",
            "react", "angular", "vue", "node", "django", "flask", "fastapi",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "sql", "nosql", "mongodb", "postgresql", "redis",
            "machine learning", "deep learning", "nlp", "ai", "data science",
            "agile", "scrum", "ci/cd", "devops", "microservices",
            "leadership", "communication", "teamwork", "problem solving"
        ]
        
        text_lower = text.lower()
        found = []
        
        for kw in tech_keywords:
            if kw in text_lower:
                found.append(kw)
        
        # Also extract capitalized words (likely proper nouns/tech)
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        for word in words:
            if len(word) > 2 and word.lower() not in ['the', 'and', 'for', 'with']:
                found.append(word.lower())
        
        return list(set(found))
    
    def _check_formatting(self, resume_text: str) -> List[str]:
        """Check for ATS formatting issues."""
        issues = []
        
        # Check for tables (ATS often can't parse)
        if "|" in resume_text and resume_text.count("|") > 10:
            issues.append("Tables detected - ATS may not parse correctly")
        
        # Check for unusual characters
        if re.search(r'[■●◆★►]', resume_text):
            issues.append("Special bullet characters detected - use standard bullets")
        
        # Check for images (text representation)
        if "[image]" in resume_text.lower() or "logo" in resume_text.lower():
            issues.append("Images detected - ATS cannot read images")
        
        # Check for headers/sections
        standard_sections = ["experience", "education", "skills", "summary", "work"]
        found_sections = [s for s in standard_sections if s in resume_text.lower()]
        if len(found_sections) < 3:
            issues.append("Missing standard section headers (Experience, Education, Skills)")
        
        # Check length
        word_count = len(resume_text.split())
        if word_count < 200:
            issues.append("Resume too short - add more detail")
        elif word_count > 1500:
            issues.append("Resume too long - keep to 1-2 pages")
        
        return issues
    
    def _generate_recommendations(
        self,
        missing: List[str],
        formatting_issues: List[str],
        score: float
    ) -> List[str]:
        """Generate improvement recommendations."""
        recs = []
        
        if missing:
            recs.append(f"Add these missing keywords: {', '.join(missing[:5])}")
        
        for issue in formatting_issues[:3]:
            if "tables" in issue.lower():
                recs.append("Replace tables with plain text formatting")
            elif "bullet" in issue.lower():
                recs.append("Use standard bullet points (-, *)")
            elif "images" in issue.lower():
                recs.append("Remove images and include text descriptions")
            elif "headers" in issue.lower():
                recs.append("Add clear section headers: Experience, Education, Skills")
        
        if score < 50:
            recs.append("Consider tailoring your resume more specifically to this job")
        
        return recs
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"


class SkillGapAnalyzerTool:
    """
    Tool #34: Compare skills vs job requirements, suggest courses.
    """
    
    # Course recommendations database
    COURSE_DB = {
        "python": [
            {"name": "Python for Everybody", "platform": "Coursera", "free": True},
            {"name": "Complete Python Developer", "platform": "Udemy", "free": False}
        ],
        "javascript": [
            {"name": "JavaScript: Understanding the Weird Parts", "platform": "Udemy", "free": False},
            {"name": "The Odin Project", "platform": "TheOdinProject", "free": True}
        ],
        "react": [
            {"name": "React - The Complete Guide", "platform": "Udemy", "free": False},
            {"name": "Full Stack Open", "platform": "Helsinki University", "free": True}
        ],
        "machine learning": [
            {"name": "Machine Learning by Andrew Ng", "platform": "Coursera", "free": True},
            {"name": "Fast.ai Practical Deep Learning", "platform": "Fast.ai", "free": True}
        ],
        "aws": [
            {"name": "AWS Certified Solutions Architect", "platform": "A Cloud Guru", "free": False},
            {"name": "AWS Free Tier Tutorials", "platform": "AWS", "free": True}
        ],
        "docker": [
            {"name": "Docker Mastery", "platform": "Udemy", "free": False},
            {"name": "Play with Docker", "platform": "Docker", "free": True}
        ],
        "kubernetes": [
            {"name": "Kubernetes for Developers", "platform": "Udemy", "free": False},
            {"name": "Kubernetes Basics", "platform": "Kubernetes.io", "free": True}
        ],
        "sql": [
            {"name": "SQL for Data Science", "platform": "Coursera", "free": True},
            {"name": "Mode SQL Tutorial", "platform": "Mode Analytics", "free": True}
        ]
    }
    
    def execute(
        self,
        resume_skills: List[str],
        job_requirements: List[str],
        job_title: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze skill gaps and recommend learning paths.
        
        Args:
            resume_skills: Skills from user's resume
            job_requirements: Required skills from job description
            job_title: Target job title
            
        Returns:
            Skill gap analysis with course recommendations
        """
        log = logger.bind(tool="SkillGapAnalyzer")
        log.info("analyzing_skills", resume_count=len(resume_skills), job_count=len(job_requirements))
        
        # Normalize skills
        resume_normalized = [s.lower().strip() for s in resume_skills]
        job_normalized = [s.lower().strip() for s in job_requirements]
        
        # Find matches and gaps
        matched = [s for s in job_normalized if any(s in r or r in s for r in resume_normalized)]
        gaps = [s for s in job_normalized if s not in matched]
        extra = [s for s in resume_normalized if not any(s in j or j in s for j in job_normalized)]
        
        # Calculate match percentage
        match_rate = len(matched) / len(job_normalized) if job_normalized else 0
        
        # Get course recommendations for gaps
        recommendations = []
        for gap in gaps[:5]:
            courses = self._get_courses(gap)
            if courses:
                recommendations.append({
                    "skill": gap,
                    "courses": courses
                })
        
        # Prioritize gaps
        priority_gaps = self._prioritize_gaps(gaps, job_title)
        
        return {
            "success": True,
            "match_rate": round(match_rate * 100, 1),
            "matched_skills": matched,
            "skill_gaps": gaps,
            "extra_skills": extra[:10],
            "priority_gaps": priority_gaps,
            "course_recommendations": recommendations,
            "summary": self._generate_summary(match_rate, gaps, job_title)
        }
    
    def _get_courses(self, skill: str) -> List[Dict]:
        """Get course recommendations for a skill."""
        skill_lower = skill.lower()
        
        # Direct match
        if skill_lower in self.COURSE_DB:
            return self.COURSE_DB[skill_lower]
        
        # Partial match
        for key, courses in self.COURSE_DB.items():
            if key in skill_lower or skill_lower in key:
                return courses
        
        return []
    
    def _prioritize_gaps(self, gaps: List[str], job_title: str) -> List[Dict]:
        """Prioritize skill gaps by importance."""
        # High priority keywords based on common job patterns
        high_priority = ["python", "javascript", "sql", "aws", "react", "machine learning", "docker"]
        
        prioritized = []
        for gap in gaps:
            priority = "high" if any(hp in gap.lower() for hp in high_priority) else "medium"
            prioritized.append({"skill": gap, "priority": priority})
        
        # Sort by priority
        prioritized.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
        
        return prioritized[:7]
    
    def _generate_summary(self, match_rate: float, gaps: List[str], job_title: str) -> str:
        """Generate a human-readable summary."""
        if match_rate >= 80:
            return f"Excellent! You're a strong match for this {job_title or 'role'}. Focus on showcasing your existing skills."
        elif match_rate >= 60:
            return f"Good foundation! Consider brushing up on: {', '.join(gaps[:3])}."
        elif match_rate >= 40:
            return f"Moderate match. Key skills to develop: {', '.join(gaps[:4])}. Consider taking courses or building projects."
        else:
            return f"Significant skill gap. Priority learning: {', '.join(gaps[:5])}. Consider a structured learning path."


class CompanyStalkerTool:
    """
    Tool #1: Research company info from public sources.
    """
    
    def execute(self, company_name: str) -> Dict[str, Any]:
        """
        Research a company.
        
        Args:
            company_name: Company to research
            
        Returns:
            Company information
        """
        log = logger.bind(tool="CompanyStalker", company=company_name)
        log.info("researching_company")
        
        # Note: In production, this would integrate with APIs like:
        # - Glassdoor API
        # - LinkedIn Company API
        # - Crunchbase API
        # For now, return structured placeholder that can be enhanced
        
        return {
            "success": True,
            "company": company_name,
            "data_sources": ["glassdoor", "linkedin", "crunchbase"],
            "note": "Company research feature - connect to Glassdoor/LinkedIn APIs for full data",
            "suggestions": [
                f"Search Glassdoor for '{company_name}' reviews",
                f"Check LinkedIn for '{company_name}' company page",
                f"Look up '{company_name}' on Crunchbase for funding info"
            ]
        }


# Tool Registration
def register_application_tools():
    """Register all application enhancement tools."""
    from tools.registry import ToolRegistry
    
    ToolRegistry.register_instance("cover_letter_generator", CoverLetterGeneratorTool)
    ToolRegistry.register_instance("ats_scorer", ATSScorerTool)
    ToolRegistry.register_instance("skill_gap_analyzer", SkillGapAnalyzerTool)
    ToolRegistry.register_instance("company_stalker", CompanyStalkerTool)
