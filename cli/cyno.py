"""
CYNO CLI Agent - AI Career Strategist
Terminal-based job search and career guidance agent.

Supports:
- 📄 PDF Resume Parsing
- 🔗 Auto-Ngrok Configuration
- 🤖 Gemini-like Live UI
- 🗣️ Natural Language Processing
"""

import os
import sys
import re
import json
import time
import threading
import textwrap
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Rich terminal UI
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt
    from rich.theme import Theme
    from rich.text import Text
    from rich.live import Live
    from rich.style import Style
    from rich.layout import Layout
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Installing rich for better terminal experience...")
    os.system(f"{sys.executable} -m pip install rich prompt_toolkit pypdf -q")
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt
    from rich.theme import Theme
    from rich.text import Text
    from rich.live import Live

# PDF Support
try:
    import pypdf
except ImportError:
    pypdf = None

# CYNO Theme - Gemini Inspired
CYNO_THEME = Theme({
    "info": "blue",
    "warning": "yellow",
    "error": "red bold",
    "success": "green bold",
    "command": "magenta",
    "highlight": "#4B8BBE bold", # Python Blue
    "user": "#34C759 bold",     # User Green
    "agent": "#AF52DE bold",    # Agent Purple
    "timestamp": "dim white",
})

# Force UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

console = Console(theme=CYNO_THEME, force_terminal=True)

# ========================================
# CONFIGURATION
# ========================================
CONFIG_FILE = PROJECT_ROOT / "config" / "cli_settings.json"

DEFAULT_CONFIG = {
    "cloud_url": "",
    "ollama_url": "http://localhost:11434",
    "ollama_model": "gemma2:2b",
    "mode": "cloud",
    "history_file": str(PROJECT_ROOT / "config" / ".cyno_history"),
    "theme": "gemini"
}

def load_config() -> dict:
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
    except Exception:
        pass
    return DEFAULT_CONFIG

def save_config(config: dict):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

config = load_config()

# Update env immediately
if config.get("cloud_url"):
    os.environ["COLAB_SERVER_URL"] = config["cloud_url"]

# ========================================
# UI HELPERS
# ========================================
class SmartUI:
    @staticmethod
    def stream_response(text: str, title: str = "CYNO"):
        """Typing effect for responses"""
        with Live(console=console, refresh_per_second=20) as live:
            accumulated = ""
            for word in text.split(" "):
                accumulated += word + " "
                md = Markdown(accumulated)
                live.update(Panel(md, title=f"🤖 {title}", border_style="agent", padding=(1, 2)))
                time.sleep(0.02)
    
    @staticmethod
    def show_thinking(message: str = "Processing..."):
        """Show thinking spinner"""
        return console.status(f"[bold agent]{message}[/bold agent]", spinner="dots")

    @staticmethod
    def print_user(text: str):
        console.print(f"\n[user]You[/user] › {text}")

# ========================================
# FILE UTILS
# ========================================
def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF or txt file"""
    path = Path(file_path.strip().strip('"').strip("'"))
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    if path.suffix.lower() == '.pdf':
        if not pypdf:
            return "❌ pypdf not installed. Run `pip install pypdf`."
        try:
            reader = pypdf.PdfReader(path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"❌ Failed to parse PDF: {str(e)}"
    else:
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            return f"❌ Failed to read file: {str(e)}"

# ========================================
# TOOL IMPORTS
# ========================================
def lazy_import_tools():
    """Lazy import tools to speed up startup"""
    global JobSearchTool, SalaryEstimatorTool, cloud_client
    
    try:
        from tools.job_search import JobSearchTool
    except ImportError:
        JobSearchTool = None
        
    try:
        from tools.discovery_tools import SalaryEstimatorTool
    except ImportError:
        SalaryEstimatorTool = None
    
    try:
        from cloud.enhanced_client import get_cloud_client
        cloud_client = get_cloud_client()
    except ImportError:
        cloud_client = None

JobSearchTool = None
SalaryEstimatorTool = None
cloud_client = None

# ========================================
# NLP INTENT DETECTION
# ========================================
INTENT_PATTERNS = {
    "job_search": [
        r"find\s+(me\s+)?(.+?)?\s*jobs?",
        r"search\s+(for\s+)?(.+?)?\s*jobs?",
        r"looking\s+for\s+(.+?)?\s*jobs?",
        r"show\s+(me\s+)?(.+?)?\s*jobs?",
        r"jobs?\s+for\s+(.+)",
    ],
    "salary": [
        r"salary\s+(for\s+)?(.+)",
        r"how\s+much\s+(does|do)\s+(.+?)\s+(make|earn|pay)",
        r"market\s+rate\s+(for\s+)?(.+)",
    ],
    "resume": [
        r"analyze\s+(my\s+)?resume",
        r"review\s+(my\s+)?resume",
        r"read\s+(this\s+)?file",
    ],
    "leads": [
        r"leads?\s+(for\s+)?(.+)",
        r"find\s+clients\s+(for\s+)?(.+)",
        r"growth\s+hack\s+(.+)",
    ],
    "prep_github": [
        r"github\s+prep\s+(for\s+)?(.+)",
        r"analyze\s+github\s+(for\s+)?(.+)",
        r"review\s+code\s+(for\s+)?(.+)",
    ],
    "email_gen": [
        r"(draft|write|gen)\s+(a\s+)?(cold|followup|connect)\s+email\s*(for\s+)?(.+)?",
    ],
    "help": [r"^help$", r"commands"],
    "settings": [r"^settings?", r"configure"],
}

def detect_intent(text: str) -> tuple[str, dict]:
    text_lower = text.lower().strip()
    
    # Auto-Ngrok Detection
    ngrok_match = re.search(r'https://[a-z0-9-]+\.ngrok-free\.app', text)
    if ngrok_match:
        return "update_ngrok", {"url": ngrok_match.group(0)}

    # File detection for resume
    if Path(text.strip('"')).exists() or ".pdf" in text_lower:
        return "resume_file", {"path": text.strip('"')}

    for intent, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                # Clean up query
                query = " ".join(g for g in groups if g).strip()
                return intent, {"query": query, "groups": groups}
    
    return "general", {"query": text}

# ========================================
# COMMAND HANDLERS
# ========================================

def cmd_help() -> str:
    """Show available commands"""
    table = Table(title="🤖 CYNO Power Tools", border_style="agent", box=None)
    table.add_column("Command", style="command")
    table.add_column("Description", style="white")
    
    table.add_row("[bold]Classic[/bold]", "")
    table.add_row("/jobs <query>", "Search for jobs (or just type 'find python jobs')")
    table.add_row("/resume <file>", "Analyze resume PDF")
    
    table.add_row("", "")
    table.add_row("[bold]🧠 Interview Prep[/bold]", "")
    table.add_row("/prep github <user>", "Analyze GitHub profile for tech questions")
    table.add_row("/prep behavior <q>", "Generate STAR answers for questions")
    table.add_row("/prep design <proj>", "Simulate System Design challenges")
    
    table.add_row("", "")
    table.add_row("[bold]🤝 Networking[/bold]", "")
    table.add_row("/net leads <skill>", "[bold yellow]Growth Hack[/bold yellow]: Find unlisted roles")
    table.add_row("/net email <type>", "Draft Cold/Follow-up emails with AI")
    
    table.add_row("", "")
    table.add_row("[bold]⚙️ System[/bold]", "")
    table.add_row("/config <url>", "Update Cloud Brain URL")
    
    console.print(Panel(table, title="Help", border_style="agent"))
    return ""

def cmd_jobs(query: str = "") -> str:
    global JobSearchTool
    if not query: return "Please specify a job query."
    if JobSearchTool is None: lazy_import_tools()
    
    with SmartUI.show_thinking(f"Searching millions of jobs for '{query}'..."):
        try:
            tool = JobSearchTool()
            result = tool.execute(query=query, location="Remote")
            
            if result.get("success") and result.get("jobs"):
                jobs = result["jobs"][:8]
                
                table = Table(title=f"🔍 Top {len(jobs)} Matches", border_style="info")
                table.add_column("#", style="dim")
                table.add_column("Role", style="bold white")
                table.add_column("Company", style="cyan")
                table.add_column("Location", style="dim")
                table.add_column("Pay", style="green")
                
                for i, job in enumerate(jobs, 1):
                    # Make title clickable
                    title = job.get("title", "N/A")[:40]
                    url = job.get("job_url") or job.get("url")
                    if url:
                        title = f"[link={url}]{title}[/link]"
                        
                    table.add_row(
                        str(i),
                        title,
                        job.get("company", "N/A")[:20],
                        job.get("location", "Remote")[:15],
                        job.get("salary", "Competitive")[:15]
                    )
                
                console.print(table)
                return ""
            else:
                return "No jobs found."
        except Exception as e:
            return f"Error: {e}"

            return f"Error: {e}"

def cmd_resume(file_path: str = "") -> str:
    from tools.resume_parser import ResumeParserTool
    from cli.state import state

    path = file_path.strip().strip('"')
    if not path:
        # Check if we have a saved resume
        if state.state.resume_path:
            console.print(f"[dim]Using saved resume: {state.state.resume_path}[/dim]")
            path = state.state.resume_path
        else:
            return "Usage: /resume <path/to/resume.pdf>"

    if not os.path.exists(path):
        return f"File found not: {path}"

    with console.status("[bold green]Parsing resume...[/bold green]"):
        try:
            # Run the actual tool
            tool = ResumeParserTool()
            
            # Extract text first to save raw text
            import pypdf
            raw_text = ""
            try:
                with open(path, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        raw_text += page.extract_text() + "\n"
            except:
                raw_text = "Text extraction failed"
            
            # PROD FIX: Pass TEXT not PATH
            if len(raw_text) < 100:
                return f"Parsed text too short ({len(raw_text)} chars). Is the PDF an image?"

            result = tool.execute(raw_text)
            
            if result:
                # SAVE TO STATE (Convert Pydantic to Dict)
                state.set_resume(path, raw_text, result.model_dump())
                
                # Print Summary
                skills = result.parsed_skills
                
                panel = Panel(
                    f"""
[bold]Name:[/bold] {result.name}
[bold]Email:[/bold] {result.email}
[bold]Skills:[/bold] {', '.join(skills[:10])}...
[bold]Experience:[/bold] {len(result.experience)} roles found.
""",
                    title="📄 Resume Analyzed & Saved",
                    border_style="green"
                )
                console.print(panel)
                return ""
            else:
                return "Failed to parse resume."
        except Exception as e:
            return f"Error parsing resume: {str(e)}"
# Placeholder functions for new commands
def cmd_salary(query: str = "") -> str:
    return f"Salary command not yet implemented for query: {query}"

def cmd_cover(query: str = "") -> str:
    return f"Cover letter command not yet implemented for query: {query}"

def cmd_interview(query: str = "") -> str:
    return f"Interview prep command not yet implemented for query: {query}"

def cmd_email(query: str = "") -> str:
    return f"Email command not yet implemented for query: {query}"

def cmd_settings() -> str:
    return "Settings command not yet implemented."

def cmd_clear() -> str:
    console.clear()
    return ""

# ========================================
# COMMAND ROUTER
# ========================================

# Lazy load router
Router = None

def get_router():
    global Router
    if Router is None:
        from cli.command_routers import CommandRouter
        Router = CommandRouter(console)
    return Router

COMMANDS: Dict[str, Callable] = {
    "/help": lambda _: cmd_help(),
    "/jobs": cmd_jobs,
    "/resume": cmd_resume,
    "/salary": cmd_salary,
    "/cover": cmd_cover,
    "/interview": cmd_interview,
    "/email": cmd_email, # Keeping legacy for now, but /net email is superior
    "/settings": lambda _: cmd_settings(),
    "/clear": lambda _: cmd_clear(),
    "/exit": lambda _: sys.exit(0),
    "/quit": lambda _: sys.exit(0),
}

SUB_COMMANDS = {
    "/app": lambda args: get_router().route_app(args),
    "/net": lambda args: get_router().route_net(args),
    "/prep": lambda args: get_router().route_prep(args),
    "/find": lambda args: get_router().route_find(args),
}

def process_input(user_input: str) -> str:
    """Process user input - commands or natural language"""
    text = user_input.strip()
    if not text: return ""
    
    SmartUI.print_user(text)
    
    # Slash commands
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # New Sub-Routers
        if cmd in SUB_COMMANDS:
            try:
                return SUB_COMMANDS[cmd](args)
            except Exception as e:
                return f"[error]Command failed: {e}[/error]"

        # Classic Commands
        if cmd == "/jobs": return cmd_jobs(args)
        if cmd == "/resume": return cmd_resume(args)
        if cmd == "/help": return cmd_help()
        if cmd == "/exit": sys.exit(0)
        
        # Fallback to map
        if cmd in COMMANDS:
            return COMMANDS[cmd](args)
    
    # Intent Detection
    intent, ctx = detect_intent(text)
    
    if intent == "update_ngrok":
        url = ctx["url"]
        config["cloud_url"] = url
        save_config(config)
        os.environ["COLAB_SERVER_URL"] = url
        global cloud_client
        cloud_client = None # Reload
        console.print(f"[success]🔗 Cloud Brain connected to: {url}[/success]")
        return ""
        
    if intent == "resume_file":
        return cmd_resume(ctx["path"])
        
    if intent == "leads":
        return get_router().route_net(f"leads {ctx['query']}")
        
    if intent == "prep_github":
        return get_router().route_prep(f"github {ctx['query']}")
        
    if intent == "email_gen":
        # extract type and recipient from groups if available, else standard split
        msg = ctx['query']
        return get_router().route_net(f"email {msg}")
        
    if intent == "job_search":
        return cmd_jobs(ctx.get("query") or "Software Engineer")
        
    if intent == "help":
        return cmd_help()
        
    # Fallback to general chat / unknown
    return cmd_help()

def main():
    console.clear()
    console.print(Panel(
        "[bold white]Welcome to CYNO[/bold white]\n[dim]AI Career Agent v2.0[/dim]", 
        style="agent", 
        width=50
    ))
    
    while True:
        try:
            user_input = console.input("\n[dim]>[/dim] ")
            result = process_input(user_input)
            if result: console.print(result)
        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[error]{e}[/error]")

if __name__ == "__main__":
    main()
