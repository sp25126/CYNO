"""
CYNO Interview Prep Tools - GitHub-Powered Deep Analysis
Analyzes user's actual GitHub projects to generate personalized interview Q&A.
Implements Phase 2 of 50-Tool Roadmap (Advanced Interview Prep).
"""

import os
import json
import base64
import requests
import structlog
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from tools.base import JobAgentTool
from cloud.enhanced_client import get_cloud_client

logger = structlog.get_logger(__name__)


@dataclass
class ProjectAnalysis:
    """Deep analysis of a GitHub project."""
    name: str
    description: str
    languages: List[str]
    main_language: str
    stars: int
    forks: int
    topics: List[str]
    readme_summary: str
    key_files: List[str]
    architecture_notes: str
    tech_stack: List[str]
    potential_questions: List[Dict[str, str]]


# =====================================================
# 1. Project Deep Dive
# =====================================================

class ProjectDeepDiveTool(JobAgentTool):
    """
    Tool #16: Analyze GitHub repos to generate project-specific interview Q&A.
    """
    BASE_URL = "https://api.github.com"
    
    def __init__(self, github_token: Optional[str] = None):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CynoJobAgent/1.0"
        }
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    def execute(self, username: str, repo_name: Optional[str] = None) -> Dict[str, Any]:
        log = logger.bind(tool="ProjectDeepDive", username=username)
        try:
            if repo_name:
                analysis = self._analyze_repo(username, repo_name)
                return {"success": True, "projects": [analysis]}
            else:
                repos = self._get_top_repos(username, limit=5)
                analyses = [self._analyze_repo(username, r["name"]) for r in repos]
                return {"success": True, "projects": analyses}
        except Exception as e:
            log.error("analysis_failed", error=str(e))
            return {"success": False, "error": str(e)}

    def _get_top_repos(self, username: str, limit: int = 5) -> List[Dict]:
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {"per_page": 100, "sort": "pushed"}
        response = requests.get(url, headers=self.headers, params=params, timeout=15)
        response.raise_for_status()
        repos = response.json()
        original_repos = [r for r in repos if not r.get("fork")]
        return sorted(original_repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:limit]

    def _analyze_repo(self, username: str, repo_name: str) -> Dict[str, Any]:
        repo_url = f"{self.BASE_URL}/repos/{username}/{repo_name}"
        repo_data = requests.get(repo_url, headers=self.headers).json()
        
        # Get languages
        langs = list(requests.get(f"{repo_url}/languages", headers=self.headers).json().keys())
        
        # Get README
        readme_resp = requests.get(f"{repo_url}/readme", headers=self.headers)
        readme_content = ""
        if readme_resp.status_code == 200:
            readme_content = base64.b64decode(readme_resp.json().get("content", "")).decode("utf-8", errors="ignore")
        
        # Key files
        contents = requests.get(f"{repo_url}/contents", headers=self.headers).json()
        key_files = [item["name"] for item in contents if isinstance(item, dict) and "name" in item][:20]
        
        tech_stack = self._detect_tech_stack(key_files, langs)
        
        # Generate questions using Cloud Client
        client = get_cloud_client()
        prompt = f"""
        Generate 5 interview questions for this GitHub project.
        Project: {repo_name}
        Description: {repo_data.get('description')}
        Tech Stack: {', '.join(tech_stack)}
        README Snippet: {readme_content[:1000]}
        
        Include: 2 Technical, 2 Behavioral, 1 System Design.
        Return JSON.
        """
        questions = []
        try:
            res = client.generate_text(prompt, parse_json=True)
            if res.success:
                questions = res.result
        except Exception:
            pass # Fallback to empty if LLM fails

        return {
            "name": repo_name,
            "description": repo_data.get("description"),
            "languages": langs,
            "tech_stack": tech_stack,
            "questions": questions
        }

    def _detect_tech_stack(self, files: List[str], languages: List[str]) -> List[str]:
        tech_map = {
            "package.json": "Node.js", "requirements.txt": "Python", "pom.xml": "Java",
            "Dockerfile": "Docker", "docker-compose.yml": "Docker Compose",
            ".github": "GitHub Actions", "tsconfig.json": "TypeScript",
            "next.config.js": "Next.js", "tailwind.config.js": "Tailwind"
        }
        detected = [tech_map[f] for f in files if f in tech_map]
        return list(set(detected + languages))

# =====================================================
# 2. Technical Q Generator
# =====================================================

class TechnicalQGeneratorTool(JobAgentTool):
    """Tool #17: Generate questions from code snippets."""
    
    def execute(self, code_snippet: str, language: str, context: str = "") -> Dict[str, Any]:
        client = get_cloud_client()
        prompt = f"""
        Generate 5 technical interview questions for this {language} code.
        Code:
        {code_snippet[:2000]}
        
        Context: {context}
        
        For each, provide: Question, What it tests, Model Answer.
        Return JSON.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"questions": res.result} if res.success else {"error": "Generation failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# 3. Behavioral Answer Bank
# =====================================================

class BehavioralAnswerBankTool(JobAgentTool):
    """Tool #18: Generate STAR answers."""
    
    def execute(self, question: str, project_context: Dict[str, Any]) -> Dict[str, Any]:
        client = get_cloud_client()
        prompt = f"""
        Generate a STAR Method answer for: "{question}"
        Based on Project: {project_context.get('name')}
        Context: {project_context}
        
        Return JSON with keys: 'situation', 'task', 'action', 'result'.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"star_answer": res.result} if res.success else {"error": "Generation failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# 4. System Design Simulator (NEW)
# =====================================================

class SystemDesignSimulatorTool(JobAgentTool):
    """Tool #19: Ask 'How would you design X?' based on real projects."""
    
    def execute(self, project_summary: Dict) -> Dict[str, Any]:
        client = get_cloud_client()
        project_name = project_summary.get('name', 'Project')
        prompt = f"""
        Create a System Design Interview Prompt based on this project: {project_name}
        Description: {project_summary.get('description')}
        Tech: {project_summary.get('tech_stack')}
        
        Scenario: "Imagine {project_name} needs to scale to 10M users."
        
        Provide:
        1. The Prompt
        2. Key Challenges (Data, Traffic, DB)
        3. Expected High-Level Architecture
        4. Follow-up probing questions
        
        Return JSON.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"design_challenge": res.result} if res.success else {"error": "Failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# 5. Code Walkthrough Coach (NEW)
# =====================================================

class CodeWalkthroughCoachTool(JobAgentTool):
    """Tool #20: Practice explaining code line-by-line."""
    
    def execute(self, code_snippet: str) -> Dict[str, Any]:
        client = get_cloud_client()
        prompt = f"""
        Customer wants to practice explaining this code line-by-line.
        Generate a "Walkthrough Script" for them to practice.
        
        Code: {code_snippet[:1000]}
        
        Provide:
        1. A high-level summary paragraph.
        2. A structured explanation block for key sections (lines X-Y).
        3. Key technical terms to use (e.g. "Recursion", "Complexity").
        
        Return JSON.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"walkthrough_guide": res.result} if res.success else {"error": "Failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# 6. Why This Tech (Existing)
# =====================================================

class WhyThisTechAnswerGenTool(JobAgentTool):
    """Tool #21: Why did you use X over Y?"""
    
    def execute(self, tech_used: str, alternatives: List[str], project_context: Dict) -> Dict[str, Any]:
        client = get_cloud_client()
        prompt = f"""
        Generate an interview answer for: "Why did you use {tech_used} instead of {', '.join(alternatives)}?"
        Project: {project_context.get('name')}
        
        Provide:
        1. Pros of {tech_used} relevant to project.
        2. Comparative analysis vs alternatives.
        3. Final justification statement.
        
        Return JSON.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"answer_guide": res.result} if res.success else {"error": "Failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# 7. Challenge Story Builder (NEW)
# =====================================================

class ChallengeStoryBuilderTool(JobAgentTool):
    """Tool #22: Create 'biggest challenge' stories."""
    
    def execute(self, project_details: Dict) -> Dict[str, Any]:
        client = get_cloud_client()
        prompt = f"""
        Based on this project, invent a realistic "Technical Challenge" story.
        Project: {project_details.get('name')}
        Stack: {project_details.get('tech_stack')}
        
        Create a narrative about:
        - A specific bug, performance issue, or integration problem likely for this stack.
        - The investigation process.
        - The solution.
        
        Return JSON.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"challenge_story": res.result} if res.success else {"error": "Failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# 8. Architecture Defender (NEW)
# =====================================================

class ArchitectureDefenderTool(JobAgentTool):
    """Tool #25: Practice defending decisions."""
    
    def execute(self, architecture_desc: str) -> Dict[str, Any]:
        client = get_cloud_client()
        prompt = f"""
        Play Devil's Advocate against this architecture.
        Architecture: {architecture_desc}
        
        Provide 5 tough probing questions (e.g. "Why simple monolithic? Why not microservices?", "Single point of failure?")
        And for each, provide a "Defense Strategy".
        
        Return JSON.
        """
        try:
            res = client.generate_text(prompt, parse_json=True)
            return {"defense_prep": res.result} if res.success else {"error": "Failed"}
        except Exception as e:
            return {"error": str(e)}

# =====================================================
# Registration
# =====================================================

def register_interview_tools():
    """Register all interview prep tools."""
    from tools.registry import ToolRegistry
    
    ToolRegistry.register_instance("project_deep_dive", ProjectDeepDiveTool)
    ToolRegistry.register_instance("technical_q_generator", TechnicalQGeneratorTool)
    ToolRegistry.register_instance("behavioral_answer_bank", BehavioralAnswerBankTool)
    ToolRegistry.register_instance("system_design_simulator", SystemDesignSimulatorTool)
    ToolRegistry.register_instance("code_walkthrough_coach", CodeWalkthroughCoachTool)
    ToolRegistry.register_instance("why_this_tech", WhyThisTechAnswerGenTool)
    ToolRegistry.register_instance("challenge_story_builder", ChallengeStoryBuilderTool)
    ToolRegistry.register_instance("architecture_defender", ArchitectureDefenderTool)
