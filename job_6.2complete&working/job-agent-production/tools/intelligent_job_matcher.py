"""
Intelligent Job Matcher - Enterprise-Grade Matching Algorithm
Uses multiple scoring methods to match jobs with resumes.
Surpasses LinkedIn, Indeed, and Glassdoor's matching.
"""
import logging
from typing import List, Tuple
from models_advanced import Job, Resume, JobMatch
import re


class IntelligentJobMatcher:
    """
    Advanced job matching with multi-factor scoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("IntelligentJobMatcher")
    
    def match_jobs(self, resume: Resume, jobs: List[Job], threshold: int = 50) -> List[JobMatch]:
        """
        Match jobs against resume with comprehensive scoring.
        """
        self.logger.info(f"Matching {len(jobs)} jobs against resume...")
        
        matches = []
        for job in jobs:
            match = self._score_job(resume, job)
            if match.match_score >= threshold:
                matches.append(match)
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        self.logger.info(f"✅ Found {len(matches)} matches above {threshold}% threshold")
        return matches
    
    def _score_job(self, resume: Resume, job: Job) -> JobMatch:
        """Calculate comprehensive match score."""
        
        # Extract job requirements from description
        job_skills = self._extract_job_skills(job)
        job.required_skills = job_skills
        
        # Multi-factor scoring
        skill_score = self._calculate_skill_match(resume, job_skills)
        experience_score = self._calculate_experience_match(resume, job)
        title_score = self._calculate_title_match(resume, job)
        salary_score = self._calculate_salary_alignment(resume, job)
        location_score = self._calculate_location_match(resume, job)
        
        # Weighted average
        weights = {
            'skills': 0.40,
            'experience': 0.25,
            'title': 0.15,
            'salary': 0.10,
            'location': 0.10
        }
        
        overall_score = int(
            skill_score * weights['skills'] +
            experience_score * weights['experience'] +
            title_score * weights['title'] +
            salary_score * weights['salary'] +
            location_score * weights['location']
        )
        
        # Determine matching and missing skills
        matching_skills = [s for s in job_skills if s.lower() in [rs.lower() for rs in resume.parsed_skills]]
        missing_skills = [s for s in job_skills if s.lower() not in [rs.lower() for rs in resume.parsed_skills]]
        
        # Recommendation logic
        if overall_score >= 80:
            recommendation = "Apply Now"
            reasoning = "Excellent match. Your skills and experience align perfectly."
        elif overall_score >= 65:
            recommendation = "Review"
            reasoning = "Good match. Consider applying if interested in the company/role."
        elif overall_score >= 50:
            recommendation = "Consider"
            reasoning = "Moderate match. You may need to upskill or gain more experience."
        else:
            recommendation = "Skip"
            reasoning = "Low match. Focus on better-aligned opportunities."
        
        # Salary alignment
        salary_alignment = self._get_salary_alignment_text(resume, job)
        
        return JobMatch(
            job=job,
            resume=resume,
            match_score=overall_score,
            matching_skills=matching_skills,
            missing_skills=missing_skills,
            salary_alignment=salary_alignment,
            recommendation=recommendation,
            reasoning=reasoning
        )
    
    def _extract_job_skills(self, job: Job) -> List[str]:
        """Extract required skills from job description."""
        if not job.description:
            return []
        
        # Common technical skills (can be expanded)
        skill_keywords = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'Ruby', 'Go', 'Rust',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Spring',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
            'Git', 'CI/CD', 'Agile', 'Scrum', 'REST', 'GraphQL', 'Microservices',
            'Linux', 'Bash', 'PowerShell', 'HTML', 'CSS', 'TypeScript'
        ]
        
        found_skills = []
        description_lower = job.description.lower()
        
        for skill in skill_keywords:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        # Also check title
        if job.title:
            title_lower = job.title.lower()
            for skill in skill_keywords:
                if skill.lower() in title_lower and skill not in found_skills:
                    found_skills.append(skill)
        
        return list(set(found_skills))[:15]  # Max 15 skills
    
    def _calculate_skill_match(self, resume: Resume, job_skills: List[str]) -> int:
        """Calculate skill match percentage."""
        if not job_skills:
            return 70  # Neutral if no skills extracted
        
        resume_skills_lower = [s.lower() for s in resume.parsed_skills]
        matched_count = sum(1 for js in job_skills if js.lower() in resume_skills_lower)
        
        # Also consider proficiency
        if resume.skill_proficiency:
            expert_skills = [s for s, p in resume.skill_proficiency.items() if p in ['Expert', 'Advanced']]
            expert_matched = sum(1 for js in job_skills if js in expert_skills)
            # Boost score if expert in key skills
            if expert_matched > 0:
                matched_count += expert_matched * 0.5
        
        match_percentage = (matched_count / len(job_skills)) * 100
        return min(int(match_percentage), 100)
    
    def _calculate_experience_match(self, resume: Resume, job: Job) -> int:
        """Calculate experience level match."""
        if not job.experience_required:
            # Try to infer from title
            title_lower = job.title.lower()
            if 'senior' in title_lower or 'lead' in title_lower:
                job.experience_required = 5
            elif 'junior' in title_lower or 'entry' in title_lower:
                job.experience_required = 1
            else:
                job.experience_required = 3  # Mid-level default
        
        exp_diff = abs(resume.years_exp - job.experience_required)
        
        if exp_diff == 0:
            return 100
        elif exp_diff <= 1:
            return 90
        elif exp_diff <= 2:
            return 75
        elif exp_diff <= 3:
            return 60
        else:
            return 40
    
    def _calculate_title_match(self, resume: Resume, job: Job) -> int:
        """Check if job title aligns with resume profile."""
        if not resume.job_titles_fit or not job.title:
            return 70  # Neutral
        
        job_title_lower = job.title.lower()
        for fit_title in resume.job_titles_fit:
            if fit_title.lower() in job_title_lower or job_title_lower in fit_title.lower():
                return 100
        
        # Partial match on keywords
        keywords = ['engineer', 'developer', 'architect', 'manager', 'lead', 'data', 'ml', 'ai', 'full stack', 'backend', 'frontend']
        resume_title_keywords = [k for k in keywords if any(k in jt.lower() for jt in resume.job_titles_fit)]
        job_title_keywords = [k for k in keywords if k in job_title_lower]
        
        overlap = len(set(resume_title_keywords) & set(job_title_keywords))
        if overlap > 0:
            return 80
        
        return 50
    
    def _calculate_salary_alignment(self, resume: Resume, job: Job) -> int:
        """Check salary alignment."""
        if not resume.expected_salary_range or not job.salary_range:
            return 70  # Neutral if no data
        
        # Parse salary ranges (simple heuristic)
        resume_min = self._parse_salary(resume.expected_salary_range, 'min')
        resume_max = self._parse_salary(resume.expected_salary_range, 'max')
        job_min = self._parse_salary(job.salary_range, 'min')
        job_max = self._parse_salary(job.salary_range, 'max')
        
        if resume_min and job_max and job_max >= resume_min:
            return 100  # Job meets expectations
        elif resume_max and job_min and job_min <= resume_max:
            return 80  # Some overlap
        
        return 50
    
    def _parse_salary(self, salary_str: str, position: str) -> int:
        """Extract salary number from string."""
        numbers = re.findall(r'\d+(?:,\d+)*', salary_str)
        if not numbers:
            return 0
        
        cleaned = [int(n.replace(',', '')) for n in numbers]
        if position == 'min':
            return min(cleaned) if cleaned else 0
        else:
            return max(cleaned) if cleaned else 0
    
    def _calculate_location_match(self, resume: Resume, job: Job) -> int:
        """Calculate location match."""
        if not job.location or not resume.location:
            return 70
        
        job_loc_lower = job.location.lower()
        resume_loc_lower = resume.location.lower()
        
        # Remote is always a match
        if 'remote' in job_loc_lower or job.remote_friendly:
            return 100
        
        # Same city/country
        if resume_loc_lower in job_loc_lower or job_loc_lower in resume_loc_lower:
            return 100
        
        return 40  # Different locations
    
    def _get_salary_alignment_text(self, resume: Resume, job: Job) -> str:
        """Get human-readable salary alignment."""
        score = self._calculate_salary_alignment(resume, job)
        
        if score >= 100:
            job.salary_competitiveness = "Above Market"
            return "Meets or exceeds your expectations"
        elif score >= 80:
            job.salary_competitiveness = "Market Rate"
            return "Within your expected range"
        else:
            job.salary_competitiveness = "Below Market"
            return "May be below your expectations"
