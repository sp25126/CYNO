"""
Advanced Resume Generator - Cloud-Powered Professional Resume Creation
Aggregates data from multiple sources and uses Cloud GPU for generation.
"""

import os
import json
import time
import requests
import structlog
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

logger = structlog.get_logger(__name__)


@dataclass
class AggregatedProfile:
    """Container for all profile data sources."""
    
    # Base resume data
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    
    # Skills
    skills: List[str] = field(default_factory=list)
    
    # Experience
    years_experience: int = 0
    work_history: List[Dict] = field(default_factory=list)
    
    # Education
    education: str = ""
    certifications: List[str] = field(default_factory=list)
    
    # Projects (from resume + GitHub)
    projects: List[Dict] = field(default_factory=list)
    
    # GitHub enrichment
    github_username: str = ""
    github_repos: List[Dict] = field(default_factory=list)
    github_languages: List[str] = field(default_factory=list)
    github_stars: int = 0
    github_bio: str = ""
    
    # Portfolio enrichment
    portfolio_url: str = ""
    portfolio_projects: List[str] = field(default_factory=list)
    
    # Profile type
    profile_type: str = "GENERAL"
    
    # Target job (for tailoring)
    target_job_title: str = ""
    target_company: str = ""
    target_job_description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ResumeGeneratorTool:
    """
    Advanced resume generator using EnhancedCloudClient.
    Same functionality on Cloud GPU or Local Ollama - only speed differs.
    """
    
    def __init__(self):
        self._client = None
        self.timeout = 120
    
    def _get_client(self):
        """Lazy load enhanced cloud client."""
        if self._client is None:
            try:
                from cloud.enhanced_client import get_cloud_client
                self._client = get_cloud_client()
            except ImportError:
                logger.warning("enhanced_client_not_available")
        return self._client
    
    def generate_resume(
        self,
        profile: AggregatedProfile,
        style: str = "professional",
        format: str = "markdown"
    ) -> str:
        """
        Generate a professional resume using EnhancedCloudClient.
        Same prompts, same output - Cloud is faster, Local is slower.
        
        Args:
            profile: Aggregated profile data
            style: Resume style ('professional', 'modern', 'technical')
            format: Output format ('markdown', 'text')
            
        Returns:
            Generated resume as string
        """
        log = logger.bind(tool="ResumeGenerator", style=style)
        log.info("generating_resume", profile_type=profile.profile_type)
        
        client = self._get_client()
        
        if client:
            try:
                result = client.generate_resume(
                    profile=profile.to_dict(),
                    style=style,
                    format=format
                )
                
                if result.success:
                    log.info("resume_generated", backend=result.backend, time=result.time_seconds)
                    return result.result
                else:
                    log.warning("client_generation_failed", error=result.error)
            except Exception as e:
                log.warning("client_error", error=str(e))
        
        # Fallback to local template
        log.info("using_local_fallback")
        return self._generate_local(profile, style, format)
    
    def _generate_local(
        self,
        profile: AggregatedProfile,
        style: str,
        format: str
    ) -> str:
        """Generate resume using local LLM (Ollama)."""
        log = logger.bind(method="local")
        
        try:
            from langchain_ollama import ChatOllama
            
            llm = ChatOllama(
                model="gemma2:2b",
                base_url="http://localhost:11434",
                temperature=0.3
            )
            
            prompt = self._build_prompt(profile, style)
            
            log.info("invoking_local_llm")
            start_time = time.time()
            
            response = llm.invoke(prompt)
            resume = response.content.strip()
            
            elapsed = time.time() - start_time
            log.info("local_generation_success", time_seconds=elapsed)
            
            return resume
            
        except Exception as e:
            log.error("local_generation_failed", error=str(e))
            # Ultimate fallback: template-based
            return self._generate_template(profile)
    
    def _build_prompt(self, profile: AggregatedProfile, style: str) -> str:
        """Build LLM prompt for resume generation."""
        
        # Format GitHub repos
        github_section = ""
        if profile.github_repos:
            repos_text = "\n".join([
                f"- {r['name']}: {r.get('description', 'No description')} ({r.get('stars', 0)} stars, {r.get('language', 'Unknown')})"
                for r in profile.github_repos[:5]
            ])
            github_section = f"""
GitHub Profile ({profile.github_username}):
- Languages: {', '.join(profile.github_languages[:10])}
- Total Stars: {profile.github_stars}
- Top Repositories:
{repos_text}
"""
        
        # Format work history
        work_section = ""
        if profile.work_history:
            work_text = "\n".join([
                f"- {w.get('role', 'Role')} at {w.get('company', 'Company')} ({w.get('duration', '')})"
                for w in profile.work_history[:5]
            ])
            work_section = f"""
Work Experience:
{work_text}
"""
        
        # Target job tailoring
        tailoring = ""
        if profile.target_job_title:
            tailoring = f"""
*** TAILORING INSTRUCTIONS ***
This resume is being tailored for:
- Position: {profile.target_job_title}
- Company: {profile.target_company}
- Job Description: {profile.target_job_description[:500]}

Emphasize skills and experience most relevant to this position.
"""
        
        style_instructions = {
            "professional": "Use formal language, focus on achievements with metrics, clean formatting.",
            "modern": "Use action verbs, include soft skills, modern section headers.",
            "technical": "Emphasize technical skills, include GitHub projects, focus on technologies."
        }
        
        prompt = f"""You are an expert resume writer. Create a professional, ATS-friendly resume.

STYLE: {style}
INSTRUCTIONS: {style_instructions.get(style, style_instructions['professional'])}

=== CANDIDATE DATA ===

Name: {profile.name}
Email: {profile.email}
Location: {profile.location}
Profile Type: {profile.profile_type}
Years of Experience: {profile.years_experience}

Skills: {', '.join(profile.skills[:20])}

Education: {profile.education}
Certifications: {', '.join(profile.certifications) if profile.certifications else 'None'}

{work_section}

Projects: {', '.join([p.get('name', str(p)) if isinstance(p, dict) else str(p) for p in profile.projects[:5]]) if profile.projects else 'None listed'}

{github_section}

{tailoring}

=== OUTPUT REQUIREMENTS ===
1. Use Markdown format
2. Include sections: Summary, Skills, Experience, Projects, Education
3. For each experience/project, include 2-3 bullet points with achievements
4. Use action verbs (Led, Developed, Implemented, etc.)
5. Include metrics where possible (e.g., "Improved performance by 40%")
6. Keep it to 1-2 pages worth of content
7. Do NOT hallucinate - only use information provided above
8. If GitHub data is provided, integrate relevant repos into Projects section

=== RESUME ===
"""
        return prompt
    
    def _generate_template(self, profile: AggregatedProfile) -> str:
        """Ultimate fallback: template-based resume."""
        
        github_section = ""
        if profile.github_repos:
            github_section = "\n## GitHub Projects\n"
            for repo in profile.github_repos[:5]:
                github_section += f"- **{repo['name']}**: {repo.get('description', '')} ({repo.get('language', '')})\n"
        
        return f"""# {profile.name or 'Professional Resume'}

## Contact
- Email: {profile.email or 'Available upon request'}
- Location: {profile.location or 'Remote'}
{f"- GitHub: github.com/{profile.github_username}" if profile.github_username else ""}

## Summary
{profile.profile_type.replace('_', ' ').title()} with {profile.years_experience} years of experience.

## Skills
{', '.join(profile.skills[:15]) if profile.skills else 'Technical skills available upon request'}

## Experience
{profile.years_experience} years of professional experience in software development.

## Education
{profile.education or 'Details available upon request'}

{github_section}

## Certifications
{', '.join(profile.certifications) if profile.certifications else 'N/A'}

---
*Generated by Cyno Resume Generator*
"""
    
    def aggregate_from_sources(
        self,
        resume_data: Dict[str, Any],
        github_data: Optional[Dict[str, Any]] = None,
        portfolio_data: Optional[Dict[str, Any]] = None,
        target_job: Optional[Dict[str, Any]] = None
    ) -> AggregatedProfile:
        """
        Aggregate data from multiple sources into a single profile.
        
        Args:
            resume_data: Parsed resume data
            github_data: Scraped GitHub profile
            portfolio_data: Scraped portfolio data
            target_job: Target job for tailoring
            
        Returns:
            AggregatedProfile with all data combined
        """
        profile = AggregatedProfile()
        
        # From resume
        profile.name = resume_data.get('name', '')
        profile.email = resume_data.get('email', '')
        profile.location = resume_data.get('location', '')
        profile.skills = resume_data.get('skills', []) or resume_data.get('parsed_skills', [])
        profile.years_experience = resume_data.get('years_exp', 0)
        profile.education = resume_data.get('education', '') or resume_data.get('education_level', '')
        profile.certifications = resume_data.get('certifications', [])
        profile.projects = resume_data.get('projects', [])
        profile.work_history = resume_data.get('work_experience', [])
        profile.profile_type = resume_data.get('profile_type', 'GENERAL')
        
        # Enrich with GitHub
        if github_data:
            profile.github_username = github_data.get('username', '')
            profile.github_repos = github_data.get('repos', [])
            profile.github_languages = github_data.get('languages', [])
            profile.github_stars = github_data.get('total_stars', 0)
            profile.github_bio = github_data.get('bio', '')
            
            # Merge GitHub languages with skills
            for lang in profile.github_languages:
                if lang not in profile.skills:
                    profile.skills.append(lang)
            
            # Use GitHub name if resume name is empty
            if not profile.name:
                profile.name = github_data.get('name', '')
            
            # Use GitHub location if resume location is empty
            if not profile.location or profile.location == 'Unknown':
                profile.location = github_data.get('location', '')
        
        # Enrich with portfolio
        if portfolio_data:
            profile.portfolio_url = portfolio_data.get('url', '')
            profile.portfolio_projects = portfolio_data.get('headings', [])
        
        # Add target job for tailoring
        if target_job:
            profile.target_job_title = target_job.get('title', '')
            profile.target_company = target_job.get('company', '')
            profile.target_job_description = target_job.get('description', '')
        
        return profile


# Convenience function
def generate_resume(
    resume_data: Dict[str, Any],
    github_username: Optional[str] = None,
    portfolio_url: Optional[str] = None,
    target_job: Optional[Dict[str, Any]] = None,
    style: str = "professional"
) -> str:
    """
    One-liner to generate a professional resume.
    
    Args:
        resume_data: Parsed resume dictionary
        github_username: Optional GitHub username for enrichment
        portfolio_url: Optional portfolio URL for enrichment
        target_job: Optional target job for tailoring
        style: Resume style ('professional', 'modern', 'technical')
        
    Returns:
        Generated resume as Markdown string
    """
    from tools.profile_scrapers import scrape_github, scrape_portfolio
    
    generator = ResumeGeneratorTool()
    
    # Fetch external data if provided
    github_data = None
    portfolio_data = None
    
    if github_username:
        try:
            github_data = scrape_github(github_username)
        except Exception as e:
            logger.warning("github_fetch_failed", error=str(e))
    
    if portfolio_url:
        try:
            portfolio_data = scrape_portfolio(portfolio_url)
        except Exception as e:
            logger.warning("portfolio_fetch_failed", error=str(e))
    
    # Aggregate
    profile = generator.aggregate_from_sources(
        resume_data=resume_data,
        github_data=github_data,
        portfolio_data=portfolio_data,
        target_job=target_job
    )
    
    # Generate
    return generator.generate_resume(profile, style=style)
