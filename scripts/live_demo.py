import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from cli.cyno import process_input, console
from cli.state import state

def run_demo():
    console.print("[bold green]🤖 STARTING LIVE CYNO DEMO...[/bold green]")
    
    # 1. LOAD RESUME
    resume_path = "resumes/SaumyaPatel_Resume-1 (1)-1.pdf"
    console.print(f"\n[bold white]STEP 1: Loading Resume ({resume_path})...[/bold white]")
    if not os.path.exists(resume_path):
        console.print(f"[red]Resume file not found! Please place it at {resume_path}[/red]")
        return
        
    res = process_input(f'/resume "{resume_path}"')
    if res: console.print(res)
    
    # Verify state
    if not state.get_resume():
        console.print("[red]❌ Resume fail. Aborting.[/red]")
        return
    else:
        console.print("[green]✅ Resume Memory Persisted.[/green]")

    # 2. GROWTH HACKING (Leads)
    console.print("\n[bold white]STEP 2: Hunting for Hidden Leads (Growth Hacking)...[/bold white]")
    # We use a specific query to test the live scraper
    res = process_input("find leads for python") 
    if res: console.print(res)

    # 3. DEEP INTERVIEW PREP (GitHub)
    console.print("\n[bold white]STEP 3: Deep Interview Prep (GitHub Analysis)...[/bold white]")
    # Analyzing a known repo or user if 'saumya' isn't valid on GitHub, 
    # but let's try 'saumyapatel' likely from resume name, or fallback to a popular one for demo if 404.
    # Actually, let's use a very popular one to GUARANTEE results for the demo: 'torvalds' (Linux) or 'tiangolo' (FastAPI).
    # Usage: /prep github <user>
    res = process_input("analyze github for tiangolo") 
    if res: console.print(res)

    # 4. SMART EMAIL
    console.print("\n[bold white]STEP 4: Drafting Cold Email via AI...[/bold white]")
    res = process_input("draft cold email for OpenAI")
    if res: console.print(res)
    
    console.print("\n[bold green]🏁 DEMO COMPLETE.[/bold green]")

if __name__ == "__main__":
    run_demo()
