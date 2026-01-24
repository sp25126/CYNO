"""
Autonomous Improvement Engine
Self-improving agent that enhances features without breaking core logic.
"""
import logging
from typing import Dict, List, Optional
from pathlib import Path
import json
from datetime import datetime

from agent.version_control import VersionControl, HealthChecker
from tools.notifier import MultiChannelNotifier

logger = logging.getLogger(__name__)


class AutonomousImprover:
    """
    Autonomous agent that improves the system while maintaining safety.
    """
    
    def __init__(self):
        self.version_control = VersionControl()
        self.health_checker = HealthChecker()
        self.notifier = MultiChannelNotifier()
        
        # Load improvement history
        self.history_file = Path("data/improvement_history.json")
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load past improvement history."""
        if self.history_file.exists():
            with open(self.history_file) as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save improvement history."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def analyze_performance(self) -> Dict:
        """
        Analyze system performance and identify improvement opportunities.
        
        Returns:
            Dict with improvement opportunities
        """
        logger.info("Analyzing system performance...")
        
        opportunities = {
            "scraper_optimizations": [],
            "new_features": [],
            "parameter_tuning": [],
            "error_handling": []
        }
        
        # In real implementation, would analyze metrics from database
        # For now, return sample opportunities
        
        opportunities["scraper_optimizations"].append({
            "type": "timeout_increase",
            "target": "Remotive scraper",
            "current": "10s",
            "proposed": "15s",
            "reason": "87% success rate, timeout errors detected",
            "classification": "MINOR"
        })
        
        return opportunities
    
    def apply_improvement(self, improvement: Dict, require_approval: bool = True) -> bool:
        """
        Apply a single improvement.
        
        Args:
            improvement: Improvement dictionary
            require_approval: Whether to ask user first
            
        Returns:
            True if successfully applied
        """
        improvement_type = improvement.get("type")
        classification = improvement.get("classification", "MEDIUM")
        
        # Create snapshot before change
        snapshot_id = self.version_control.create_snapshot(
            reason=f"Before {improvement_type}",
            files_changed=improvement.get("files", [])
        )
        
        if not snapshot_id:
            logger.error("Failed to create snapshot. Aborting improvement.")
            return False
        
        # Check if approval needed
        if classification == "MAJOR" and require_approval:
            approval = self._request_approval(improvement)
            if not approval:
                logger.info("Improvement rejected by user")
                return False
        
        # Apply improvement based on type
        try:
            success = False
            
            if improvement_type == "timeout_increase":
                success = self._apply_timeout_increase(improvement)
            elif improvement_type == "add_error_handling":
                success = self._apply_error_handling(improvement)
            elif improvement_type == "new_scraper":
                success = self._apply_new_scraper(improvement)
            else:
                logger.warning(f"Unknown improvement type: {improvement_type}")
                return False
            
            if not success:
                logger.error("Improvement application failed")
                self.version_control.auto_revert_on_failure("Improvement failed to apply")
                return False
            
            # Verify health after change
            health = self.health_checker.verify_system_health()
            
            if health == "CRITICAL":
                logger.error("System critical after improvement. Reverting...")
                self.version_control.auto_revert_on_failure("Critical health check failed")
                self.notifier.send_alert(
                    "Auto-Revert Triggered",
                    f"Change reverted due to critical failure. System restored to {snapshot_id}."
                )
                return False
            
            # Success! Log and notify
            self._log_improvement(improvement, snapshot_id, success=True)
            
            if classification in ["MEDIUM", "MAJOR"]:
                self.notifier.send(
                    f"✅ Improvement Applied: {improvement.get('target', 'System')} - {improvement.get('reason', '')}",
                    priority="normal"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Error applying improvement: {e}")
            self.version_control.auto_revert_on_failure(f"Exception: {str(e)}")
            self.notifier.send_alert(
                "Improvement Failed",
                f"Auto-reverted due to error: {str(e)}"
            )
            return False
    
    def _request_approval(self, improvement: Dict) -> bool:
        """
        Request user approval for major changes.
        
        Returns:
            True if approved, False otherwise
        """
        description = f"""
{improvement.get('target', 'System')}
Change: {improvement.get('type')}
Reason: {improvement.get('reason')}
Current: {improvement.get('current')}
Proposed: {improvement.get('proposed')}
        """.strip()
        
        request_id = self.notifier.send_approval_request(
            change_description=description,
            change_type=improvement.get('classification', 'MEDIUM'),
            expected_impact=improvement.get('expected_impact', 'Improved reliability')
        )
        
        # In real implementation, would wait for user response
        # For now, return False (require manual approval)
        logger.info(f"Approval request {request_id} sent. Awaiting user response...")
        return False
    
    def _apply_timeout_increase(self, improvement: Dict) -> bool:
        """Apply timeout increase to a scraper."""
        # In real implementation, would modify the actual file
        logger.info(f"Applied timeout increase to {improvement.get('target')}")
        return True
    
    def _apply_error_handling(self, improvement: Dict) -> bool:
        """Add error handling to a component."""
        logger.info(f"Added error handling to {improvement.get('target')}")
        return True
    
    def _apply_new_scraper(self, improvement: Dict) -> bool:
        """Add a new scraper based on template."""
        logger.info(f"Added new scraper: {improvement.get('target')}")
        return True
    
    def _log_improvement(self, improvement: Dict, snapshot_id: str, success: bool):
        """Log improvement to history."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "improvement": improvement,
            "snapshot_id": snapshot_id,
            "success": success
        }
        
        self.history.append(log_entry)
        self._save_history()
    
    def run_daily_improvements(self):
        """Run daily autonomous improvement cycle."""
        logger.info("=== Starting Daily Improvement Cycle ===")
        
        # Analyze performance
        opportunities = self.analyze_performance()
        
        # Apply safe improvements
        applied_count = 0
        for category, improvements in opportunities.items():
            for improvement in improvements:
                if improvement.get("classification") == "MINOR":
                    # Auto-apply minor improvements
                    if self.apply_improvement(improvement, require_approval=False):
                        applied_count += 1
        
        # Send daily report
        self.notifier.send_daily_report({
            "jobs_found": 0,  # Would get from metrics
            "match_accuracy": 0,
            "active_scrapers": 13,
            "total_scrapers": 13,
            "improvements": applied_count,
            "health": self.health_checker.verify_system_health()
        })
        
        logger.info(f"=== Daily cycle complete. {applied_count} improvements applied ===")


# CLI for manual testing
if __name__ == "__main__":
    improver = AutonomousImprover()
    
    # Test improvement
    test_improvement = {
        "type": "timeout_increase",
        "target": "Test Scraper",
        "current": "10s",
        "proposed": "15s",
        "reason": "Testing autonomous improver",
        "classification": "MINOR",
        "files": ["tools/job_search.py"]
    }
    
    print("Testing autonomous improvement...")
    success = improver.apply_improvement(test_improvement, require_approval=False)
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
