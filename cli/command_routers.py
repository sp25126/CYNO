from typing import Dict, Callable, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

# We won't import heavy tools at top level to keep startup fast
# imports will be inside functions

class CommandRouter:
    def __init__(self, console: Console):
        self.console = console

    def route_app(self, args: str) -> str:
        """Handle /app commands (Applications)"""
        if not args:
            return self._show_help("/app")
        
        cmd, rest = self._split_args(args)
        
        if cmd == "cover":
            return self._handle_cover_letter(rest)
        elif cmd == "score":
            return self._handle_ats_score(rest)
        elif cmd == "resume":
            return self._handle_resume_export(rest)
        
        return f"Unknown application command: {cmd}"

    def route_net(self, args: str) -> str:
        """Handle /net commands (Networking)"""
        if not args:
            return self._show_help("/net")
        
        cmd, rest = self._split_args(args)
        
        if cmd == "email":
            return self._handle_email(rest)
        elif cmd == "leads":
            return self._handle_leads(rest)
        elif cmd == "referral":
            return self._handle_referral(rest)
            
        return f"Unknown networking command: {cmd}"

    def route_prep(self, args: str) -> str:
        """Handle /prep commands (Interview Prep)"""
        if not args:
            return self._show_help("/prep")
            
        cmd, rest = self._split_args(args)
        
        if cmd == "github":
            return self._handle_github_prep(rest)
        elif cmd == "behavior":
            return self._handle_behavioral(rest)
        elif cmd == "design":
            return self._handle_system_design(rest)
            
        return f"Unknown prep command: {cmd}"

    def route_find(self, args: str) -> str:
        """Handle /find commands (Discovery)"""
        if not args:
            return self._show_help("/find")
            
        cmd, rest = self._split_args(args)
        
        if cmd == "jobs":
            from cli.cyno import cmd_jobs # Re-use existing
            return cmd_jobs(rest)
        elif cmd == "salaries":
            from cli.cyno import cmd_salary # Re-use existing
            return cmd_salary(rest)
        elif cmd == "company":
            return self._handle_company_research(rest)
            
        return f"Unknown find command: {cmd}"

    # ==========================
    # HANDLERS (Lazy Load Tools)
    # ==========================
    
    # ==========================
    # HANDLERS (Lazy Load Tools)
    # ==========================
            
    def _handle_cover_letter(self, args: str) -> str:
        if not args: return "Usage: /app cover <company> <role>"
        from tools.application_tools import CoverLetterGeneratorTool
        from cli.state import state
        
        # BRUTAL CHECK: Do we have data?
        if not state.get_resume():
            return "[bold red]❌ No resume loaded.[/bold red]\nPlease run `/resume <path/to/resume.pdf>` first so I know who you are."

        parts = args.split(maxsplit=1)
        company = parts[0]
        role = parts[1] if len(parts) > 1 else "Software Engineer"
        
        with self.console.status(f"[cyan]Generating cover letter for {company}...[/cyan]"):
            tool = CoverLetterGeneratorTool()
            resume_data = state.get_resume()
            
            res = tool.execute(role, company, "Job Description", resume_data)
            
            if res.get("success"):
                self.console.print(Panel(res['cover_letter'], title=f"📄 Cover Letter: {company}", border_style="green"))
                return ""
            return "Failed to generate cover letter."

    def _handle_ats_score(self, args: str) -> str:
        if not args: return "Usage: /app score <job_description>"
        from tools.application_tools import ATSScorerTool
        from cli.state import state
        
        if not state.get_resume_text():
             return "[bold red]❌ No resume loaded.[/bold red]\nPlease run `/resume <path>` first."

        with self.console.status("[cyan]Scoring resume against JD...[/cyan]"):
            tool = ATSScorerTool()
            resume_text = state.get_resume_text()
            
            res = tool.execute(resume_text, args)
            
            score = res['score']
            color = "green" if score > 70 else "yellow" if score > 50 else "red"
            
            md = f"""
## 🎯 ATS Score: [{color}]{score}[/{color}]

**Missing Keywords:** {', '.join(res['missing_keywords'][:5])}
**Recommendations:**
"""
            for rec in res['recommendations']:
                md += f"- {rec}\n"
                
            self.console.print(Markdown(md))
            return ""

    def _handle_email(self, args: str) -> str:
        # args: type recipient_name
        if not args: return "Usage: /net email <type> <recipient> (type: cold, followup, connection)"
        
        from tools.smart_email import SmartEmailEngine, EmailType
        
        parts = args.split(maxsplit=1)
        e_type = parts[0]
        recipient = parts[1] if len(parts) > 1 else "Hiring Manager"
        
        engine = SmartEmailEngine()
        
        with self.console.status(f"[cyan]Drafting {e_type} email for {recipient}...[/cyan]"):
            if e_type == "cold":
                draft = engine.generate_cold_outreach_email(
                    recipient_name=recipient,
                    recipient_role="Hiring Manager",
                    company="Target Company",
                    connection_reason="Shared interest in AI"
                )
            elif e_type == "followup":
                # Mock previous email for standalone usage
                from tools.smart_email import EmailDraft
                prev = EmailDraft(subject="App", body="", company="Target Co", job_title="Role")
                draft = engine.generate_follow_up_email(prev, days_since=3)
            elif e_type == "connection":
                draft = engine.generate_connection_request(
                    recipient_name=recipient,
                    recipient_role="Professional",
                    company="Target Company",
                    connection_reason="Professional networking",
                    platform="LinkedIn"
                )
                self.console.print(Panel(draft.body, title="LinkedIn Connection", border_style="blue"))
                return ""
            else:
                 return "Supported types: cold, followup, connection"
                 
            self.console.print(Panel(f"[bold]{draft.subject}[/bold]\n\n{draft.body}", title=f"📧 {e_type.title()} Email", border_style="cyan"))
            return ""

    def _handle_leads(self, args: str) -> str:
        if not args: return "Usage: /net leads <skill>"
        
        from tools.lead_scraper import LeadScraperTool
        
        with self.console.status(f"[cyan]Scouring the web for unlisted '{args}' leads...[/cyan]"):
            scraper = LeadScraperTool()
            leads = scraper.scrape_leads([args], limit=8)
            
            if not leads: return "No leads found."
            
            table = Table(title=f"🚀 Growth Hacking Results: {args}", border_style="yellow")
            table.add_column("Source", style="dim")
            table.add_column("Need", style="cyan")
            table.add_column("Link / Contact", style="green")
            
            for lead in leads:
                # Create clickable link
                link = lead.url
                display = lead.contact_email or "View Post"
                if link:
                    display = f"[link={link}]{display}[/link]"
                
                table.add_row(
                    lead.source.split('(')[0].strip(), 
                    lead.role_needed[:50],
                    display
                )
            
            self.console.print(table)
            return ""

    def _handle_github_prep(self, args: str) -> str:
        if not args: return "Usage: /prep github <username>"
        from tools.interview_prep import ProjectDeepDiveTool
        
        with self.console.status(f"[cyan]Analyzing GitHub profile for {args}...[/cyan]"):
            tool = ProjectDeepDiveTool()
            res = tool.execute(username=args)
            
            if not res['success']:
                return f"Analysis failed: {res.get('error')}"
            
            projects = res['projects']
            if not projects: return "No suitable projects found."
            
            for p in projects:
                md = f"""
## 📂 {p['name']}
*{p['description']}*
**Tech Stack:** {', '.join(p['tech_stack'])}

**Potential Questions:**
"""
                if 'questions' in p and p['questions']:
                    for q in p['questions']:
                        qt = q.get('question', 'Q')
                        md += f"- **Q:** {qt}\n"
                
                self.console.print(Panel(Markdown(md), border_style="magenta"))
            
            return ""

    def _handle_system_design(self, args: str) -> str:
        if not args: return "Usage: /prep design <project_name>"
        from tools.interview_prep import SystemDesignSimulatorTool
        
        with self.console.status(f"[cyan]Generating system design challenge...[/cyan]"):
            tool = SystemDesignSimulatorTool()
            res = tool.execute({"name": args, "description": f"A scalable {args}", "tech_stack": ["Cloud"]})
            challenge = res.get('design_challenge', "No challenge generated.")
            self.console.print(Panel(Markdown(str(challenge)), title="🏗️ System Design Challenge", border_style="magenta"))
            return ""

    def _handle_behavioral(self, args: str) -> str:
        if not args: return "Usage: /prep behavior <question>"
        from tools.interview_prep import BehavioralAnswerBankTool
        
        with self.console.status("[cyan]Crafting STAR answer...[/cyan]"):
            tool = BehavioralAnswerBankTool()
            res = tool.execute(args, {"name": "My Project"})
            ans = res.get('star_answer', "Error")
            
            if isinstance(ans, dict):
                md = f"""
**Situation**: {ans.get('situation')}
**Task**: {ans.get('task')}
**Action**: {ans.get('action')}
**Result**: {ans.get('result')}
"""
            else:
                md = str(ans)
            
            self.console.print(Panel(Markdown(md), title="⭐ STAR Answer", border_style="green"))
            return ""

    def _handle_company_research(self, args: str) -> str:
        if not args: return "Usage: /find company <name>"
        from tools.application_tools import CompanyStalkerTool
        
        with self.console.status(f"[cyan]Researching {args}...[/cyan]"):
            tool = CompanyStalkerTool()
            res = tool.execute(args)
            
            md = f"""
## 🏢 {res['company']}
*Data Sources: {', '.join(res['data_sources'])}*

**Suggestions:**
"""
            for s in res['suggestions']:
                md += f"- {s}\n"
            
            self.console.print(Panel(Markdown(md), border_style="blue"))
            return ""

    # ... Helpers ...
    def _split_args(self, text: str):
        parts = text.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""
        return cmd, rest

    def _show_help(self, category: str) -> str:
        if category == "/app":
            return "Commands: cover, score"
        if category == "/net":
            return "Commands: email, lead, referral"
        if category == "/prep":
            return "Commands: github, behavior, design"
        if category == "/find":
            return "Commands: jobs, salaries, company"
        return "Unknown category."

    # ... Helpers ...
    def _split_args(self, text: str):
        parts = text.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ""
        return cmd, rest

    def _show_help(self, category: str) -> str:
        # Simple help for subcategories
        if category == "/app":
            return """
Available Application Commands:
- `/app cover <company> <role>`: Generate cover letter
- `/app resume <path>`: Analyze resume (alias for /resume)
            """
        if category == "/net":
            return """
Available Networking Commands:
- `/net email <type> <recipient>`: Generate emails (cold, followup)
    Types: cold, followup
- `/net leads <skill>`: Find unlisted leads via "growth hacking"
            """
        if category == "/prep":
            return """
Available Prep Commands:
- `/prep github <username>`: Analyze GitHub for questions
- `/prep behavior <question>`: Generate STAR answers
- `/prep design <project>`: System design challenges
            """
        return "Unknown category."
