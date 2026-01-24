"""
Version Control & Auto-Revert System
Automatic rollback to stable versions when changes fail.
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class VersionControl:
    """Git-based version control with auto-revert."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.versions_dir = self.project_root / "data" / "versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize git if not already
        if not (self.project_root / ".git").exists():
            self._init_git()
    
    def _init_git(self):
        """Initialize git repository."""
        try:
            subprocess.run(["git", "init"], cwd=self.project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Cyno Agent"], cwd=self.project_root, check=True)
            subprocess.run(["git", "config", "user.email", "cyno@agent.local"], cwd=self.project_root, check=True)
            logger.info("Git repository initialized")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize git: {e}")
    
    def create_snapshot(self, reason: str, files_changed: List[str]) -> str:
        """
        Create a stable version snapshot before making changes.
        
        Returns:
            version_id: Timestamp-based ID
        """
        version_id = datetime.now().strftime("stable_%Y%m%d_%H%M%S")
        
        try:
            # Stage all changes
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)
            
            # Commit
            commit_msg = f"[Cyno Auto] {reason}"
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            # Get commit hash
            commit_hash = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            # Create tag
            subprocess.run(
                ["git", "tag", version_id],
                cwd=self.project_root,
                check=True
            )
            
            # Save metadata
            metadata = {
                "version_id": version_id,
                "timestamp": datetime.now().isoformat(),
                "git_commit": commit_hash,
                "reason": reason,
                "files_changed": files_changed,
                "status": "stable"
            }
            
            metadata_path = self.versions_dir / f"{version_id}.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Created snapshot: {version_id}")
            return version_id
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create snapshot: {e}")
            return None
    
    def get_last_stable_version(self) -> Optional[str]:
        """Get the most recent stable version."""
        versions = sorted(self.versions_dir.glob("stable_*.json"), reverse=True)
        if versions:
            return versions[0].stem  # Remove .json extension
        return None
    
    def revert_to_version(self, version_id: str) -> bool:
        """
        Revert to a specific stable version.
        
        Args:
            version_id: Version to revert to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if version exists
            metadata_path = self.versions_dir / f"{version_id}.json"
            if not metadata_path.exists():
                logger.error(f"Version {version_id} not found")
                return False
            
            # Load metadata
            with open(metadata_path) as f:
                metadata = json.load(f)
            
            commit_hash = metadata.get("git_commit")
            if not commit_hash:
                logger.error("No commit hash in metadata")
                return False
            
            # Revert to commit
            subprocess.run(
                ["git", "reset", "--hard", commit_hash],
                cwd=self.project_root,
                check=True
            )
            
            logger.info(f"✅ Reverted to version: {version_id}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to revert: {e}")
            return False
    
    def auto_revert_on_failure(self, failure_reason: str) -> bool:
        """
        Automatically revert to last stable version on critical failure.
        
        Args:
            failure_reason: Description of what failed
            
        Returns:
            True if reverted successfully
        """
        last_stable = self.get_last_stable_version()
        if not last_stable:
            logger.error("No stable version found to revert to")
            return False
        
        logger.warning(f"⚠️ AUTO-REVERTING due to: {failure_reason}")
        success = self.revert_to_version(last_stable)
        
        if success:
            # Log the revert
            revert_log = {
                "timestamp": datetime.now().isoformat(),
                "reason": failure_reason,
                "reverted_to": last_stable,
                "action": "auto_revert"
            }
            
            log_path = self.versions_dir / "revert_log.jsonl"
            with open(log_path, 'a') as f:
                f.write(json.dumps(revert_log) + '\n')
        
        return success
    
    def cleanup_old_versions(self, keep_last: int = 10):
        """Keep only the last N stable versions."""
        versions = sorted(self.versions_dir.glob("stable_*.json"))
        if len(versions) > keep_last:
            for old_version in versions[:-keep_last]:
                old_version.unlink()
                logger.info(f"Cleaned up old version: {old_version.stem}")
    
    def get_version_history(self, limit: int = 10) -> List[Dict]:
        """Get recent version history."""
        versions = sorted(self.versions_dir.glob("stable_*.json"), reverse=True)[:limit]
        
        history = []
        for version_file in versions:
            with open(version_file) as f:
                history.append(json.load(f))
        
        return history


class HealthChecker:
    """System health monitoring."""
    
    def __init__(self):
        self.logger = logging.getLogger("HealthChecker")
    
    def verify_system_health(self) -> str:
        """
        Run comprehensive health checks.
        
        Returns:
            "HEALTHY" / "DEGRADED" / "CRITICAL"
        """
        checks = {
            "syntax": self._check_syntax(),
            "imports": self._check_imports(),
            "tests": self._run_tests(),
            "scrapers": self._check_scrapers(),
            "llm": self._check_llm()
        }
        
        self.logger.info(f"Health check results: {checks}")
        
        # Determine overall health
        if all(checks.values()):
            return "HEALTHY"
        elif checks["syntax"] and checks["imports"]:
            return "DEGRADED"
        else:
            return "CRITICAL"
    
    def _check_syntax(self) -> bool:
        """Check for Python syntax errors."""
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", "tools/job_search.py"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def _check_imports(self) -> bool:
        """Check if critical imports work."""
        try:
            import tools.job_search
            import tools.resume_parser
            import agent.chat_agent
            return True
        except ImportError as e:
            self.logger.error(f"Import failed: {e}")
            return False
    
    def _run_tests(self) -> bool:
        """Run basic tests."""
        try:
            # Quick smoke test
            from tools.job_search import JobSearchTool
            tool = JobSearchTool()
            return True
        except:
            return False
    
    def _check_scrapers(self) -> bool:
        """Check if scrapers are responsive."""
        # Placeholder: Would check actual scraper endpoints
        return True
    
    def _check_llm(self) -> bool:
        """Check LLM availability."""
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
