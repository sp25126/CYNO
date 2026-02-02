import time
import asyncio
from typing import List, Tuple, Any, Dict
from models import Job, Resume
from tools.base import JobAgentTool

try:
    from sentence_transformers import SentenceTransformer, util
    from fuzzywuzzy import fuzz
except ImportError:
    SentenceTransformer = None
    fuzz = None

class JobMatchingTool(JobAgentTool):
    """
    Tool to score and rank jobs against a resume using semantic and heuristic analysis.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.model = None
        if SentenceTransformer:
            try:
                # Lightweight model optimized for semantic similarity
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                print(f"Warning: Failed to load semantic model: {e}")

    def validate_input(self, **kwargs) -> bool:
        """Validates that resume and jobs are provided."""
        # For simplicity, we just check if arguments are passed to execute
        # But execute signature is explicit (resume, jobs). 
        # So we can just return True or check args if we were using kwargs.
        return True

    async def execute(self, resume: Resume, jobs: List[Job]) -> List[Tuple[Job, float, str]]:
        """
        Scores jobs against the resume.
        Returns a list of tuples: (Job, Score 0-1, Reason) sorted by score descending.
        """
        scored_jobs = []
        
        # Prepare resume embedding once
        resume_text = self._get_resume_text(resume)
        resume_embedding = None
        if self.model and resume_text:
            # Run in thread executor to avoid blocking main loop during inference
            resume_embedding = await asyncio.to_thread(self.model.encode, resume_text, convert_to_tensor=True)

        for job in jobs:
            score = 0.0
            reasons = []
            
            # --- Hard Filters (Simplified) ---
            # 1. Location (Binary)
            # Relaxed logic: If resume wants remote and job is remote -> mismatch penalty? 
            # For now, let's assume we want valid jobs. 
            # If job has no location, neutral.
            location_score = 1.0 
            if resume.location and job.location:
                # Very basic check
                if "remote" in resume.location.lower() and "remote" not in job.location.lower():
                    location_score = 0.5 # Penalty
                    reasons.append("Location Mismatch")
            
            # --- Soft Filters ---
            
            # 2. Title Similarity (Fuzzy)
            title_score = 0.0
            if resume.experience:
                # Compare job title with past roles
                # We take the max similarity with any past role
                max_ratio = 0
                for exp in resume.experience:
                    ratio = fuzz.token_set_ratio(job.title.lower(), exp.title.lower())
                    if ratio > max_ratio:
                        max_ratio = ratio
                title_score = max_ratio / 100.0
            else:
                # Fallback if no exp: compare with resume summary or skills?
                # Neutral score
                title_score = 0.5
            
            # 3. Semantic Similarity (Vectors)
            semantic_score = 0.0
            if self.model and resume_embedding is not None:
                job_text = f"{job.title} {job.description} {job.company}"
                # Async encode
                job_embedding = await asyncio.to_thread(self.model.encode, job_text, convert_to_tensor=True)
                
                # Compute cosine difference
                # util.cos_sim returns a tensor [[score]]
                sim = util.cos_sim(resume_embedding, job_embedding)
                semantic_score = float(sim[0][0])
                # Normalize -1 to 1 -> 0 to 1 roughly (though MiniLM usually 0-1 for text)
                semantic_score = max(0.0, semantic_score)
            else:
                # Fallback if model missing
                semantic_score = 0.5
                reasons.append("Model Missing")

            # --- Aggregation ---
            # Weights: Semantic (50%), Title (30%), Location/Hard (20%)
            final_score = (semantic_score * 0.5) + (title_score * 0.3) + (location_score * 0.2)
            
            # Debug reason
            reason_str = f"Sem: {semantic_score:.2f}, Title: {title_score:.2f}"
            if reasons:
                reason_str += f" ({', '.join(reasons)})"
            
            scored_jobs.append((job, final_score, reason_str))

        # Sort descending
        scored_jobs.sort(key=lambda x: x[1], reverse=True)
        return scored_jobs

    def _get_resume_text(self, resume: Resume) -> str:
        """Helper to combine resume fields into a single semantic string."""
        parts = []
        # Skills are high signal
        if resume.parsed_skills:
            parts.append("Skills: " + ", ".join(resume.parsed_skills))
        
        # Latest experience is high signal
        if resume.experience:
            latest = resume.experience[0]
            parts.append(f"Recent Role: {latest.title} at {latest.company}. {latest.description}")
            
        # Summary
        if resume.summary:
            parts.append(f"Summary: {resume.summary}")
            
        return " ".join(parts)
