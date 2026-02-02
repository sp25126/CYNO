import sys
import os
import json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Add project root
sys.path.append(os.getcwd())

from tools.interview_prep import ProjectDeepDiveTool, SystemDesignSimulatorTool

# Setup Env
console = Console()

def load_settings():
    try:
        with open("config/cli_settings.json") as f:
            return json.load(f)
    except:
        return {}

config = load_settings()
if config.get("cloud_url"):
    os.environ["COLAB_SERVER_URL"] = config["cloud_url"]

def run_deep_dive(username):
    console.print(f"[bold blue]🔍 Starting Deep Dive for: {username}...[/bold blue]")
    
    # 1. ANALYZE REPOS
    tool = ProjectDeepDiveTool()
    res = tool.execute(username)
    
    if not res.get("success"):
        console.print(f"[red]Failed: {res.get('error')}[/red]")
        return

    projects = res.get("projects", [])
    if not projects:
        console.print("[yellow]No public projects found.[/yellow]")
        return
        
    console.print(f"[green]Found {len(projects)} Projects![/green]")
    
    # Check the top project
    top_project = projects[0]
    p_name = top_project['name']
    p_desc = top_project['description']
    p_stack = ", ".join(top_project['tech_stack'])
    
    console.print(Panel(
        f"**Project:** {p_name}\n**Stack:** {p_stack}\n**Desc:** {p_desc}",
        title="🏆 Top Project",
        border_style="green"
    ))
    
    # 2. SHOW GENERATED QUESTIONS (From Deep Dive)
    console.print("\n[bold white]🧠 Predicted Interview Questions:[/bold white]")
    for q in top_project.get('questions', [])[:3]:
        question_text = q.get('question', 'Q')
        console.print(f"- [cyan]{question_text}[/cyan]")

    # 3. SYSTEM DESIGN CHALLENGE (Simulated)
    console.print(f"\n[bold white]🏗️ Generating System Design Challenge for {p_name}...[/bold white]")
    design_tool = SystemDesignSimulatorTool()
    design_res = design_tool.execute({
        "name": p_name,
        "description": p_desc,
        "tech_stack": top_project['tech_stack']
    })
    
    challenge = design_res.get('design_challenge', 'Generation Failed')
    console.print(Panel(Markdown(str(challenge)), title="System Design Interview", border_style="magenta"))

if __name__ == "__main__":
    run_deep_dive("sp25126")
