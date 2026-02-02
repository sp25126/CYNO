"""
HR Chat CLI - Fixed version with actual tool execution
"""
import asyncio
import sys
import os
import subprocess
import time
from pathlib import Path
import pdfplumber
from colorama import init, Fore, Style
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Suppress noisy logs
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("jobspy").setLevel(logging.WARNING)
logging.getLogger("praw").setLevel(logging.WARNING)
logging.getLogger("duckduckgo_search").setLevel(logging.WARNING)
logging.getLogger("pdfminer").setLevel(logging.ERROR)
logging.getLogger("pdfplumber").setLevel(logging.ERROR)
import warnings
warnings.filterwarnings("ignore", message=".*FontBBox.*")

init(autoreset=True)
import textwrap

sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.chat_agent import HRChatAgent
from models import Resume, Job

def render_job_card(index: int, job: Job, score: float, reason: str):
    """Renders a beautiful ASCII job card."""
    width = 60
    border_color = Fore.CYAN
    text_color = Fore.WHITE
    
    # Match color
    if score >= 0.8: match_color = Fore.GREEN
    elif score >= 0.5: match_color = Fore.YELLOW
    else: match_color = Fore.RED
    
    score_str = f"[{int(score*100)}% MATCH]"
    
    # Title Line
    title = f"#{index} {job.title}"[:40]
    header = f"{title:<40} {match_color}{score_str:>13}{border_color}"
    
    # Content
    company_loc = f"{job.company} • {job.location}"[:56]
    
    # Reason wrapping
    reason_lines = textwrap.wrap(f"💡 {reason}", width=56)
    reason_text = "\n".join([f"│  {line:<56}│" for line in reason_lines])
    
    print(f"{border_color}┌{'─'*58}┐")
    print(f"│  {header:<65} │")
    print(f"│  {company_loc:<56}  │")
    print(f"├{'─'*58}┤")
    print(reason_text)
    print(f"│  🔗 {str(job.job_url)[:53]:<53}   │")
    print(f"└{'─'*58}┘{Style.RESET_ALL}")


def check_ollama_running() -> bool:
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Starts Ollama service if not running."""
    if check_ollama_running():
        return True
    
    print(Fore.YELLOW + "[System] Starting Ollama (this might take 20s)..." + Style.RESET_ALL)
    
    try:
        # Check if ollama is installed
        try:
            subprocess.run(["ollama", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(Fore.RED + "Error: 'ollama' command not found. Please install Ollama from ollama.com" + Style.RESET_ALL)
            return False

        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], 
                           creationflags=subprocess.CREATE_NO_WINDOW,
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["ollama", "serve"],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        
        # Wait up to 20 seconds
        for i in range(20):
            if check_ollama_running():
                print(Fore.GREEN + "✓ Ollama connected!" + Style.RESET_ALL)
                return True
            time.sleep(1)
            print(".", end="", flush=True)
        
        print("\n" + Fore.RED + "Timed out waiting for Ollama." + Style.RESET_ALL)
        return False
    except Exception as e:
        print(Fore.RED + f"Failed to start Ollama: {e}" + Style.RESET_ALL)
        return False

class HRChatCLI:
    def __init__(self):
        self.agent = HRChatAgent()
        self.session_context = {
            "messages": [],
            "conversation_history": [],  # Track last 10 interactions
            "last_search_query": None,
            "last_search_time": None
        }
        
        # Check Cloud Brain connectivity
        self._check_cloud_brain()
        
        # Auto-load resume on startup
        self._auto_load_resume()
    
    def _check_cloud_brain(self):
        """Check if Cloud Brain (Colab) is connected and detect local GPU."""
        try:
            from cloud.cloud_client import CloudClient
            import os
            
            server_url = os.getenv("COLAB_SERVER_URL")
            
            # First, check for local GPU
            local_gpu = self._check_local_gpu()
            if local_gpu:
                self.print_sys("🎮 Local GPU detected! Will use if Cloud Brain is offline.")
            
            if not server_url:
                self.print_sys("⚠️ Cloud Brain (Colab) not configured.")
                self.print_sys("   Set COLAB_SERVER_URL in .env to enable cloud features.")
                if local_gpu:
                    self.print_sys("   ✅ Will use Local GPU Brain as primary.")
                else:
                    self.print_sys("   Will use Local CPU Brain (Ollama).")
                self.session_context["cloud_status"] = "offline"
                return
            
            # Quick health check
            client = CloudClient(server_url=server_url)
            health = client.health_check()
            
            if health.get('cloud_available'):
                gpu_status = "🎮 GPU" if health.get('gpu_available') else "💻 CPU"
                self.print_sys(f"✅ Cloud Brain Connected! ({gpu_status})")
                self.session_context["cloud_status"] = "online"
            else:
                self.print_sys(f"⚠️ Cloud Brain unreachable: {health.get('error', 'Unknown')}")
                if local_gpu:
                    self.print_sys("   ✅ Will use Local GPU Brain.")
                else:
                    self.print_sys("   Will use Local CPU Brain (Ollama).")
                self.session_context["cloud_status"] = "offline"
                
        except Exception as e:
            self.print_sys(f"⚠️ Cloud Brain check failed: {str(e)[:50]}")
            local_gpu = self._check_local_gpu()
            if local_gpu:
                self.print_sys("   ✅ Will use Local GPU Brain.")
            else:
                self.print_sys("   Will use Local CPU Brain (Ollama).")
            self.session_context["cloud_status"] = "offline"
    
    def _check_local_gpu(self) -> bool:
        """Check if local GPU is available."""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                return True
        except:
            pass
        return False
        
    def _auto_load_resume(self):
        """Auto-detects and parses the first resume found in 'resumes/'.
        Uses Cloud PDF OCR for best accuracy, falls back to local if unavailable.
        """
        try:
            resume_dir = Path("resumes")
            resume_dir.mkdir(exist_ok=True)
            files = list(resume_dir.glob("*"))
            
            valid_files = [f for f in files if f.suffix.lower() in ['.pdf', '.txt', '.docx']]
            
            if valid_files:
                target = valid_files[0]
                self.print_sys(f"Auto-detected resume: {target.name}")
                
                # Try Cloud PDF OCR first (better accuracy)
                if target.suffix.lower() == '.pdf' and self.session_context.get("cloud_status") == "online":
                    try:
                        self.print_sys("📤 Sending PDF to Cloud Brain for OCR processing...")
                        from cloud.cloud_client import get_client
                        from models import Resume
                        
                        # Read PDF bytes
                        with open(target, 'rb') as f:
                            pdf_bytes = f.read()
                        
                        # Send to cloud for OCR + parsing
                        client = get_client()
                        llm_data = client.parse_resume_pdf(pdf_bytes)
                        
                        # Build Resume object from cloud response (simplified structure)
                        skills = llm_data.get('skills', [])
                        if isinstance(skills, str):
                            skills = [s.strip() for s in skills.split(',')]
                        
                        resume = Resume(
                            name=llm_data.get('name', 'Unknown'),
                            parsed_skills=skills,
                            projects=llm_data.get('projects', []),
                            profile_type=llm_data.get('profile_type', 'GENERAL'),
                            raw_text=llm_data.get('raw_extracted_text', '')
                        )
                        
                        self.session_context["resume"] = resume
                        skills_preview = ', '.join(skills[:5]) if skills else 'None extracted'
                        self.print_sys(f"✅ Resume loaded via Cloud OCR! Profile: {resume.profile_type}")
                        self.print_sys(f"   Skills: {skills_preview}")
                        return
                        
                    except Exception as e:
                        self.print_sys(f"⚠️ Cloud OCR failed: {str(e)[:50]}. Falling back to local...")
                
                # Fallback: Local text extraction
                text_content = self.load_resume(str(target))
                
                if text_content and len(text_content) > 100:
                    from tools.resume_parser import ResumeParserTool
                    resume = ResumeParserTool().execute(text_content)
                    
                    self.session_context["resume"] = resume
                    self.print_sys(f"Resume loaded! Profile: {resume.profile_type}")
                else:
                    self.print_sys("Resume text extraction failed or too short.")
            else:
                self.print_sys("No resume found in 'resumes/'. Please upload one to get started!")
        except Exception as e:
            self.print_sys(f"Auto-load failed: {e}")
        
    def print_cyno(self, msg):
        print(Fore.GREEN + "Cyno: " + Style.RESET_ALL + msg + "\n")
    
    def print_sys(self, msg):
        print(Fore.YELLOW + "[System] " + msg + Style.RESET_ALL)
    
    def find_resume(self):
        resumes_dir = Path("resumes")
        if not resumes_dir.exists():
            resumes_dir.mkdir()
            return None
        
        resumes = list(resumes_dir.glob("*.pdf"))
        return str(resumes[0]) if resumes else None
    
    def load_resume(self, path):
        try:
            pdf = pdfplumber.open(path)
            text = "\n".join([p.extract_text() or "" for p in pdf.pages])
            pdf.close()
            return text
        except Exception as e:
            self.print_sys(f"Error: {e}")
            return None
    
    async def run(self):
        print(Fore.CYAN + "\n=== CareerConnect AI ===\n" + Style.RESET_ALL)
        
        # If resume already loaded by auto-loader, skip prompt
        if self.session_context.get("resume"):
            self.print_cyno(f"Resume ready! I've analyzed your {self.session_context['resume'].profile_type} profile.\nWhat kind of jobs should I look for?")
        else:
            self.print_cyno("Welcome! Drop your resume in the 'resumes/' folder to get started.")
        
        while True:
            try:
                user_input = input(Fore.CYAN + "You: " + Style.RESET_ALL).strip()
                
                if not user_input or user_input.lower() in ["/quit", "quit", "exit"]:
                    self.print_cyno("Good luck with your job search! 👍")
                    break
                
                
                # Handle "yes" for auto-resume (more relaxed matching)
                is_yes = user_input.lower().split()[0] in ["yes", "y", "yeah", "sure", "ok"]
                if is_yes and self.find_resume() and not self.session_context.get("resume"):
                    # If they say "yes" but also give more context like "yes find AI jobs"
                    # We first parse resume, then process the rest
                    self.print_sys("Analyzing your resume first...")
                    user_input = "parse resume " + user_input  # Prepend parse command
                
                # Parse resume
                if any(kw in user_input.lower() for kw in ["resume", "cv", "parse", "analyze"]):
                    resume_path = self.find_resume()
                    if resume_path:
                        self.print_sys(f"Reading: {Path(resume_path).name}...")
                        text = self.load_resume(resume_path)
                        if text:
                            from tools.resume_parser import ResumeParserTool
                            try:
                                resume = ResumeParserTool().execute(text)
                                self.session_context["resume"] = resume
                                
                                self.print_cyno(f"""Perfect! I've analyzed your profile:

✨ **Skills**: {', '.join(resume.parsed_skills[:6])} 
✨ **Experience**: {resume.years_exp} years
✨ **Domain**: {', '.join(resume.domains) if resume.domains else 'General'}

Now I can find the best jobs for you. What are you looking for?""")
                                # If the user had a search query in their "yes" message, continue to search
                                if "find" in user_input.lower() or "search" in user_input.lower():
                                    pass # Fall through to search block
                                else:
                                    continue
                            except Exception as e:
                                self.print_sys(f"Parse error: {e}")
                    else:
                        self.print_cyno("I couldn't find a resume in the 'resumes/' folder. Please add one!")
                    
                    if "find" not in user_input.lower() and "search" not in user_input.lower():
                        continue
                
                
                # Use agent intent detection instead of hardcoded keywords
                if not self.session_context.get("resume"):
                    # Let agent handle if no resume
                    self.print_sys("Thinking...")
                    response = self.agent.process_message(user_input, self.session_context)
                    self.print_cyno(response)
                    continue
                
                # Check intent
                intent = self.agent.detect_intent(user_input, self.session_context)
                
                # Check for explicit email drafting keywords OR intent
                # PRIORITIZE THIS OVER SEARCH to avoid accidental searches
                if intent.primary == "draft_email" or any(kw in user_input.lower() for kw in ["draft", "write email", "compose", "cover letter", "make an email"]):
                    if not self.session_context.get("matched"):
                        last_search = self.session_context.get("last_search_query")
                        if last_search:
                            self.print_cyno(f"Hmm, I remember searching for '{last_search}' but the results aren't available anymore. Let me search again!")
                            # Trigger a new search with the last query
                            user_input = f"find {last_search}"
                            # Will fall through to search logic below
                        else:
                            self.print_cyno("I need to search for jobs first before I can draft an email. Try searching for jobs!")
                            continue
                        
                    # Extract job number if specified (e.g., "draft email for job #1")
                    import re
                    job_num_match = re.search(r'#?(\d+)', user_input)
                    job_index = int(job_num_match.group(1)) - 1 if job_num_match else 0
                    
                    matched_jobs = self.session_context["matched"]
                    if job_index >= len(matched_jobs):
                        self.print_cyno(f"Sorry, I only found {len(matched_jobs)} jobs. Please pick a number between 1 and {len(matched_jobs)}.")
                        continue
                    
                    job, score, reason = matched_jobs[job_index]
                    resume = self.session_context["resume"]
                    
                    self.print_sys(f"Drafting email for: {job.title} at {job.company}...")
                    
                    try:
                        from tools.email_drafter import EmailDraftTool
                        draft = EmailDraftTool().execute(job, resume)
                        
                        self.print_cyno(f"""✉️ Email Draft Created!

**Subject**: {draft.subject}
**To**: {draft.recipient_email}

{draft.body[:200]}...

📁 Full draft saved to: emails/ folder
💡 Review and customize before sending!""")
                        continue
                    except Exception as e:
                        self.print_sys(f"Email draft error: {e}")
                        continue

                # Lead Generation (New Feature)
                if any(kw in user_input.lower() for kw in ["find leads", "get leads", "generate leads", "scrape leads"]):
                    resume = self.session_context.get("resume")
                    skills = resume.parsed_skills if resume else ["python", "developer"]
                    
                    self.print_sys(f"Hunting for leads using skills: {', '.join(skills[:3])}...")
                    self.print_sys("Scanning Google/DDG/Social for direct email contacts...")
                    
                    try:
                        from tools.lead_scraper import LeadScraperTool
                        # Use a reasonable limit
                        leads = LeadScraperTool().scrape_leads(skills, limit=15)
                        
                        if leads:
                            # SAVE TO CSV
                            import pandas as pd
                            from datetime import datetime
                            
                            leads_dir = Path("leads")
                            leads_dir.mkdir(exist_ok=True)
                            
                            # Clean query for filename
                            query_str = "leads_" + "_".join(skills[:2]).replace(" ", "_")
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = leads_dir / f"{query_str}_{timestamp}.csv"
                            
                            # Convert leads to DF
                            df = pd.DataFrame([vars(l) for l in leads])
                            df.to_csv(filename, index=False)
                            
                            self.print_sys(f"✅ Leads saved to: {filename}")
                            
                            self.print_cyno(f"🎯 Found {len(leads)} potential leads with emails!")
                            print(Fore.CYAN + "="*60 + Style.RESET_ALL)
                            for i, lead in enumerate(leads[:5], 1):
                                print(f"{Fore.GREEN}Lead #{i}: {lead.contact_email or 'No Email'}{Style.RESET_ALL}")
                                print(f"  For:   {lead.role_needed}")
                                print(f"  Pain:  {lead.pain_points}")
                                print(f"  Source: {lead.source[:40]}...")
                                print(f"  Link:  {str(lead.url)[:60]}...")
                                print(Fore.CYAN + "-"*60 + Style.RESET_ALL)
                            
                            if len(leads) > 5:
                                print(f"... and {len(leads)-5} more saved to CSV.")
                            
                            self.print_sys("Tip: Use these emails to send cold outreach.")
                        else:
                            self.print_cyno("No direct leads found right now. Try different skills or general job search.")
                            
                        continue
                    except Exception as e:
                        self.print_sys(f"Lead gen error: {e}")
                        continue

                # Execute job search if detected
                if intent.primary == "job_search":
                    resume = self.session_context["resume"]
                    
                    # Extract query from user input
                    query = user_input.replace("find me", "").replace("search for", "").replace("get me", "").replace("looking for", "").strip()
                    
                    # If query too short, use resume domains
                    if len(query.split()) < 2:
                        query_parts = resume.domains[:1] if resume.domains else ["developer"]
                        query = " ".join(query_parts)
                    
                    location = "remote"
                    for city in ["ahmedabad", "bangalore", "mumbai", "delhi", "pune", "hyderabad", "chennai", "remote", "india", "usa"]:
                        if city in user_input.lower():
                            location = city
                            break
                    
                    print(Fore.YELLOW + "┌" + "─"*50 + "┐")
                    print(f"│ Searching: {query:<37} │")
                    print(f"│ Location:  {location:<37} │")
                    print("└" + "─"*50 + "┘" + Style.RESET_ALL)
                    self.print_sys("Scanning LinkedIn, Indeed, Glassdoor & more... (30-60s)")
                    self.print_sys("Press Ctrl+C to cancel search")
                    
                    try:
                        # SEARCH
                        from tools.job_search import JobSearchTool
                        # Use higher limit to get more results
                        # FIX: run_all is async now, so we must await it
                        jobs = await JobSearchTool().run_all(query, limit=20)
                        
                        if not jobs:
                            self.print_cyno(f"No jobs found for '{query}'. Try a broader search or different location.")
                            continue
 
                        # Count by source for user info
                        sources = {}
                        for j in jobs:
                            src = j.source.split('(')[0].strip()
                            sources[src] = sources.get(src, 0) + 1
                        
                        source_summary = ", ".join([f"{k}: {v}" for k,v in sources.items()])
                        self.print_sys(f"Sources: {source_summary}")
                        self.print_sys(f"Full results saved to 'jobs/' folder")

                        # MATCH
                        self.print_sys("Ranking jobs against your resume...")
                        from tools.job_matcher import JobMatchingTool
                        matched = await JobMatchingTool().execute(resume, jobs)
                        
                        # Store in session for email drafting
                        self.session_context["matched"] = matched
                        self.session_context["last_search_query"] = query
                        self.session_context["last_search_time"] = "just now"
                        
                        # Add to conversation history
                        from datetime import datetime
                        self.session_context["conversation_history"].append({
                            "type": "search",
                            "query": query,
                            "results_count": len(jobs),
                            "top_match": matched[0][0].title if matched else None,
                            "timestamp": datetime.now().isoformat()
                        })
                        
                        # SHOW TOP 3
                        self.print_cyno(f"Found {len(jobs)} matches! Here are the best ones:")
                        
                        for i, (job, score, reason) in enumerate(matched[:3], 1):
                            render_job_card(i, job, score, reason)
                        
                        print("\n")
                        self.print_cyno(f"💡 Suggestion: Type 'Draft email for job #1' to generate a cover letter!")
                        continue
                    
                    except KeyboardInterrupt:
                        print("\n" + Fore.RED + "🚫 Search canceled by user." + Style.RESET_ALL)
                        continue    
                    except Exception as e:
                        self.print_sys(f"Search error: {e}")
                        continue
                
                # Default: LLM chat
                self.print_sys("Thinking...")
                response = self.agent.process_message(user_input, self.session_context)
                self.print_cyno(response)
                
            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                self.print_sys(f"Error: {e}")

def main():
    start_ollama()
    cli = HRChatCLI()
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()
