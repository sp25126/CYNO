#!/usr/bin/env python
"""
Autonomous Agent Runner
Runs scheduled improvements and monitors system health.

Usage:
    python scripts/autonomous_run.py --daemon     # Run in background
    python scripts/autonomous_run.py --once       # Run once and exit
"""
import sys
import argparse
import logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from agent.autonomous_improver import AutonomousImprover
from agent.version_control import HealthChecker
from tools.notifier import MultiChannelNotifier
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AutonomousRunner:
    """Manages scheduled autonomous operations."""
    
    def __init__(self):
        self.improver = AutonomousImprover()
        self.health_checker = HealthChecker()
        self.notifier = MultiChannelNotifier()
        self.scheduler = BackgroundScheduler()
    
    def daily_performance_check(self):
        """Run daily performance analysis and safe improvements."""
        logger.info("=== Daily Performance Check (2:00 AM) ===")
        
        try:
            # Check system health first
            health = self.health_checker.verify_system_health()
            
            if health == "CRITICAL":
                self.notifier.send_alert(
                    "System Critical",
                    "Daily check detected critical issues. Manual intervention may be needed."
                )
                return
            
            # Run improvements
            self.improver.run_daily_improvements()
            
        except Exception as e:
            logger.error(f"Daily check failed: {e}")
            self.notifier.send_alert("Daily Check Failed", str(e))
    
    def weekly_feature_scan(self):
        """Scan for new features and integrations weekly."""
        logger.info("=== Weekly Feature Scan (Sunday 10:00 AM) ===")
        
        try:
            # In real implementation, would:
            # 1. Check for new job sites
            # 2. Look for API updates
            # 3. Scan for popular scrapers on GitHub
            # 4. Analyze user search patterns for gaps
            
            opportunities = {
                "new_sites": ["RemoteLeaf.com", "WorkFromHome.com"],
                "api_updates": ["Remotive v2 API available"],
                "user_requests": ["More India-based job boards"]
            }
            
            if opportunities["new_sites"]:
                message = f"""
📋 Weekly Feature Discovery

New Job Sites Found:
{chr(10).join(f'  • {site}' for site in opportunities['new_sites'])}

Would you like me to add these?
Reply YES to approve automatic integration.
                """.strip()
                
                self.notifier.send(message, priority="normal")
            
        except Exception as e:
            logger.error(f"Weekly scan failed: {e}")
    
    def realtime_monitoring(self):
        """Continuous health monitoring (runs every 5 minutes)."""
        try:
            health = self.health_checker.verify_system_health()
            
            if health == "CRITICAL":
                logger.warning("⚠️ System health critical!")
                self.improver.version_control.auto_revert_on_failure(
                    "Health monitoring detected critical state"
                )
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
    
    def setup_schedule(self):
        """Configure scheduled jobs."""
        
        # Daily at 2:00 AM
        self.scheduler.add_job(
            self.daily_performance_check,
            CronTrigger(hour=2, minute=0),
            id='daily_check',
            name='Daily Performance Check'
        )
        
        # Weekly on Sunday at 10:00 AM
        self.scheduler.add_job(
            self.weekly_feature_scan,
            CronTrigger(day_of_week='sun', hour=10, minute=0),
            id='weekly_scan',
            name='Weekly Feature Scan'
        )
        
        # Every 5 minutes - health monitoring
        self.scheduler.add_job(
            self.realtime_monitoring,
            'interval',
            minutes=5,
            id='health_monitor',
            name='Health Monitoring'
        )
        
        logger.info("✅ Scheduled jobs configured:")
        for job in self.scheduler.get_jobs():
            logger.info(f"  - {job.name}: {job.trigger}")
    
    def run_once(self):
        """Run improvement cycle once (for manual testing)."""
        logger.info("Running one-time improvement cycle...")
        self.daily_performance_check()
        logger.info("One-time cycle complete")
    
    def run_daemon(self):
        """Run as background daemon."""
        logger.info("🤖 Starting Cyno Autonomous Agent (Daemon Mode)")
        
        # Send startup notification
        self.notifier.send(
            "🤖 Cyno Autonomous Agent Started\n\nScheduled operations:\n• Daily: 2:00 AM\n• Weekly: Sunday 10:00 AM\n• Health checks: Every 5 min",
            priority="normal"
        )
        
        # Setup and start scheduler
        self.setup_schedule()
        self.scheduler.start()
        
        logger.info("Autonomous agent running. Press Ctrl+C to stop.")
        
        try:
            # Keep running
            while True:
                time.sleep(60)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Shutting down autonomous agent...")
            self.scheduler.shutdown()
            self.notifier.send("🤖 Cyno Autonomous Agent Stopped", priority="normal")


def main():
    parser = argparse.ArgumentParser(description='Cyno Autonomous Agent')
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as background daemon'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run improvement cycle once and exit'
    )
    
    args = parser.parse_args()
    
    runner = AutonomousRunner()
    
    if args.daemon:
        runner.run_daemon()
    elif args.once:
        runner.run_once()
    else:
        print("Usage: autonomous_run.py --daemon OR --once")
        parser.print_help()


if __name__ == "__main__":
    main()
