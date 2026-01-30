#!/usr/bin/env python3
"""
CYNO CLI - Intelligent Job Search Assistant
Natural Language Interface powered by Cloud GPU
"""

import os
import sys
import json
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import structlog
from agent.nlp_router import CynoAgent, create_cyno_agent

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
    ]
)

logger = structlog.get_logger(__name__)


class CynoCLI:
    """Command-line interface for CYNO."""
    
    BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     ██████╗██╗   ██╗███╗   ██╗ ██████╗                       ║
║    ██╔════╝╚██╗ ██╔╝████╗  ██║██╔═══██╗                      ║
║    ██║      ╚████╔╝ ██╔██╗ ██║██║   ██║                      ║
║    ██║       ╚██╔╝  ██║╚██╗██║██║   ██║                      ║
║    ╚██████╗   ██║   ██║ ╚████║╚██████╔╝                      ║
║     ╚═════╝   ╚═╝   ╚═╝  ╚═══╝ ╚═════╝                       ║
║                                                               ║
║           🚀 Intelligent Job Search Assistant 🚀              ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
"""
    
    COMMANDS = {
        "/help": "Show this help message",
        "/github <username>": "Set your GitHub username for analysis",
        "/resume <path>": "Load your resume from file",
        "/interview": "Start interview prep mode",
        "/jobs <query>": "Search for jobs",
        "/analyze": "Analyze your GitHub projects",
        "/cover <company>": "Generate a cover letter",
        "/ats <job_desc>": "Score your resume against a job description",
        "/skills": "Analyze your skill gaps",
        "/status": "Show current session status",
        "/clear": "Clear conversation context",
        "/quit": "Exit CYNO"
    }
    
    def __init__(self):
        self.agent = None
        self.context = {
            "github_username": None,
            "resume_loaded": False,
            "resume_data": {}
        }
        self.running = True
    
    def start(self):
        """Start the CLI."""
        print(self.BANNER)
        print("🔧 Initializing CYNO agent...")
        
        try:
            self.agent = create_cyno_agent()
            print("✅ Agent ready!")
            
            # Check cloud connection
            cloud_url = os.getenv("COLAB_SERVER_URL")
            if cloud_url:
                print(f"☁️  Cloud Brain: Connected ({cloud_url[:30]}...)")
            else:
                print("⚠️  Cloud Brain: Not connected (using local mode)")
            
            print("\n💡 Tips:")
            print("  • Just type naturally! I understand plain English.")
            print("  • Set your GitHub with: /github <username>")
            print("  • Type /help for all commands")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            print("Starting in limited mode...")
            self.agent = None
        
        self.run_loop()
    
    def run_loop(self):
        """Main interaction loop."""
        while self.running:
            try:
                # Get user input
                user_input = input("\n🧑 You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith("/"):
                    self.handle_command(user_input)
                else:
                    self.handle_natural_input(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Good luck with your job search!")
                break
            except EOFError:
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logger.error("cli_error", error=str(e))
    
    def handle_command(self, command: str):
        """Handle slash commands."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/help":
            self.show_help()
        
        elif cmd == "/quit" or cmd == "/exit":
            print("\n👋 Goodbye! Good luck with your job search!")
            self.running = False
        
        elif cmd == "/github":
            if args:
                self.context["github_username"] = args
                self.agent.set_context("github_username", args)
                print(f"✅ GitHub username set to: {args}")
                print("💡 Now try: 'analyze my projects' or 'prepare for interviews'")
            else:
                print("Usage: /github <username>")
        
        elif cmd == "/resume":
            if args:
                self.load_resume(args)
            else:
                print("Usage: /resume <path_to_resume.txt>")
        
        elif cmd == "/interview":
            self.start_interview_mode()
        
        elif cmd == "/jobs":
            if args:
                response = self.agent.chat(f"find {args} jobs")
                print(f"\n🤖 CYNO: {response}")
            else:
                print("Usage: /jobs <query> (e.g., /jobs python developer)")
        
        elif cmd == "/analyze":
            if self.context.get("github_username"):
                response = self.agent.chat(f"analyze my github projects")
                print(f"\n🤖 CYNO: {response}")
            else:
                print("⚠️ Set your GitHub first with: /github <username>")
        
        elif cmd == "/cover":
            if args:
                response = self.agent.chat(f"write a cover letter for {args}")
                print(f"\n🤖 CYNO: {response}")
            else:
                print("Usage: /cover <company_name>")
        
        elif cmd == "/ats":
            self.run_ats_score()
        
        elif cmd == "/skills":
            self.run_skill_analysis()
        
        elif cmd == "/status":
            self.show_status()
        
        elif cmd == "/clear":
            self.context = {"github_username": None, "resume_loaded": False, "resume_data": {}}
            print("✅ Context cleared.")
        
        else:
            print(f"❓ Unknown command: {cmd}")
            print("Type /help for available commands.")
    
    def handle_natural_input(self, user_input: str):
        """Handle natural language input."""
        if not self.agent:
            print("\n⚠️ Agent not initialized. Using limited mode.")
            return
        
        print("\n🤔 Thinking...")
        
        try:
            response = self.agent.chat(user_input)
            print(f"\n🤖 CYNO: {response}")
        except Exception as e:
            print(f"\n❌ Error processing: {e}")
    
    def show_help(self):
        """Show help message."""
        print("\n📚 CYNO Commands:")
        print("-" * 40)
        for cmd, desc in self.COMMANDS.items():
            print(f"  {cmd:20} - {desc}")
        
        print("\n💬 Natural Language Examples:")
        print("-" * 40)
        print("  • 'prepare me for interviews'")
        print("  • 'find python developer jobs in NYC'")
        print("  • 'analyze my github projects'")
        print("  • 'write a cover letter for Google'")
        print("  • 'what skills am I missing for this job?'")
        print("  • 'help me with behavioral questions'")
    
    def show_status(self):
        """Show current session status."""
        print("\n📊 Session Status:")
        print("-" * 40)
        print(f"  GitHub: {self.context.get('github_username') or 'Not set'}")
        print(f"  Resume: {'Loaded ✅' if self.context.get('resume_loaded') else 'Not loaded'}")
        
        cloud_url = os.getenv("COLAB_SERVER_URL")
        if cloud_url:
            print(f"  Cloud:  Connected ✅")
        else:
            print(f"  Cloud:  Not connected (local mode)")
    
    def load_resume(self, path: str):
        """Load resume from file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                resume_text = f.read()
            
            print("📄 Parsing resume...")
            
            # Use resume parser
            from tools.registry import ToolRegistry
            parser = ToolRegistry.get("parse_resume")
            if parser:
                result = parser.execute(resume_text)
                self.context["resume_loaded"] = True
                self.context["resume_data"] = {
                    "skills": result.parsed_skills,
                    "years_exp": result.years_exp,
                    "education": result.education_level,
                    "projects": result.projects,
                    "profile_type": result.profile_type
                }
                self.agent.set_context("resume", self.context["resume_data"])
                
                print(f"✅ Resume loaded successfully!")
                print(f"   Skills: {len(result.parsed_skills)} found")
                print(f"   Experience: {result.years_exp} years")
                print(f"   Profile: {result.profile_type}")
            else:
                print("⚠️ Resume parser not available. Stored raw text.")
                self.context["resume_text"] = resume_text
                self.context["resume_loaded"] = True
                
        except FileNotFoundError:
            print(f"❌ File not found: {path}")
        except Exception as e:
            print(f"❌ Error loading resume: {e}")
    
    def start_interview_mode(self):
        """Start interactive interview prep mode."""
        if not self.context.get("github_username"):
            print("⚠️ Set your GitHub first with: /github <username>")
            return
        
        print("\n🎯 Starting Interview Prep Mode...")
        print("=" * 50)
        
        response = self.agent.chat(
            f"Analyze my GitHub profile ({self.context['github_username']}) and prepare interview questions"
        )
        print(f"\n🤖 CYNO: {response}")
        
        print("\n💡 Now you can ask:")
        print("  • 'give me a behavioral question'")
        print("  • 'explain why I used X technology'")
        print("  • 'practice system design for my project'")
    
    def run_ats_score(self):
        """Run ATS scoring."""
        print("\n📝 ATS Resume Scorer")
        print("-" * 40)
        
        if not self.context.get("resume_loaded"):
            print("⚠️ Load your resume first with: /resume <path>")
            return
        
        print("Paste the job description (end with empty line):")
        lines = []
        while True:
            line = input()
            if line == "":
                break
            lines.append(line)
        
        job_desc = "\n".join(lines)
        
        if not job_desc.strip():
            print("❌ No job description provided.")
            return
        
        print("\n🔍 Analyzing...")
        
        from tools.registry import ToolRegistry
        scorer = ToolRegistry.get("ats_scorer")
        if scorer:
            result = scorer.execute(
                resume_text=self.context.get("resume_text", str(self.context.get("resume_data", ""))),
                job_description=job_desc
            )
            
            print(f"\n📊 ATS Score: {result['score']}/100 ({result['grade']})")
            print(f"   Keyword Match: {result['keyword_match_rate']}%")
            
            if result.get("matched_keywords"):
                print(f"\n✅ Matched Keywords: {', '.join(result['matched_keywords'][:8])}")
            
            if result.get("missing_keywords"):
                print(f"\n❌ Missing Keywords: {', '.join(result['missing_keywords'][:5])}")
            
            if result.get("recommendations"):
                print("\n💡 Recommendations:")
                for rec in result["recommendations"][:3]:
                    print(f"   • {rec}")
        else:
            print("⚠️ ATS scorer not available.")
    
    def run_skill_analysis(self):
        """Run skill gap analysis."""
        if not self.context.get("resume_loaded"):
            print("⚠️ Load your resume first with: /resume <path>")
            return
        
        print("\n📝 Skill Gap Analyzer")
        print("-" * 40)
        print("Enter required skills from job posting (comma-separated):")
        skills_input = input("> ").strip()
        
        if not skills_input:
            print("❌ No skills provided.")
            return
        
        job_skills = [s.strip() for s in skills_input.split(",")]
        
        from tools.registry import ToolRegistry
        analyzer = ToolRegistry.get("skill_gap_analyzer")
        if analyzer:
            result = analyzer.execute(
                resume_skills=self.context["resume_data"].get("skills", []),
                job_requirements=job_skills
            )
            
            print(f"\n📊 Skill Match: {result['match_rate']}%")
            print(f"\n✅ Matched: {', '.join(result['matched_skills'][:8])}")
            
            if result.get("skill_gaps"):
                print(f"\n❌ Gaps: {', '.join(result['skill_gaps'][:5])}")
            
            if result.get("course_recommendations"):
                print("\n📚 Course Recommendations:")
                for rec in result["course_recommendations"][:3]:
                    print(f"\n   {rec['skill'].upper()}:")
                    for course in rec["courses"][:2]:
                        free_tag = "🆓" if course.get("free") else "💰"
                        print(f"   {free_tag} {course['name']} ({course['platform']})")
            
            print(f"\n📝 Summary: {result['summary']}")
        else:
            print("⚠️ Skill analyzer not available.")


def main():
    """Main entry point."""
    cli = CynoCLI()
    cli.start()


if __name__ == "__main__":
    main()
