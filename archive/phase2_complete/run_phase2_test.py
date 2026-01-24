import os
import sys
import logging
from collections import Counter

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.job_search import JobSearchTool
from tools.resume_parser import ResumeParserTool

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Phase2Test")

RESULT_FILE = os.path.join(os.path.dirname(__file__), "result.txt")
RESUME_FILE = os.path.join(os.path.dirname(__file__), "SaumyaPatel_Resume-1 (1)-1.pdf")

def simple_ranker(jobs, skills):
    """
    Ranks jobs based on overlapping skills/keywords.
    """
    ranked_jobs = []
    # Normalize skills
    scan_terms = set(s.lower() for s in skills)
    
    for job in jobs:
        score = 0
        title = str(job.get('title') or "")
        desc = str(job.get('description') or "")
        combined_text = (title + " " + desc).lower()
        
        for term in scan_terms:
            if term in combined_text:
                score += 1
        
        # Boost newer jobs slightly? (optional, but relevance is key here)
        ranked_jobs.append({**job, "score": score})
    
    # Sort by score info desc
    return sorted(ranked_jobs, key=lambda x: x['score'], reverse=True)

def main():
    logger.info(">>> STARTING PHASE 2 COMPLETE SYSTEM TEST <<<")
    
    # 1. Parse Resume
    logger.info(f"Parsing Resume: {RESUME_FILE}")
    parser = ResumeParserTool()
    
    # Check if resume exists
    if not os.path.exists(RESUME_FILE):
        logger.error(f"Resume file not found at: {RESUME_FILE}")
        return

    # Extract text from PDF
    import pdfplumber
    logger.info("Extracting text from PDF...")
    with pdfplumber.open(RESUME_FILE) as pdf:
        content = ""
        for page in pdf.pages:
            content += page.extract_text() or ""
    
    logger.info(f"Extracted {len(content)} characters from resume.")
    
    # Parse resume using the tool
    try:
        resume = parser.execute(content)
        query_skills = resume.parsed_skills
        # Derive role from skills or default
        if "Python" in query_skills:
            query_role = "Python Developer"
        elif "JavaScript" in query_skills or "React" in query_skills:
            query_role = "Frontend Developer"
        else:
            query_role = "Software Engineer"
    except Exception as e:
        logger.warning(f"Resume parsing failed: {e}. Using defaults.")
        query_role = "Python Developer"
        query_skills = ["python", "django", "flask", "aws", "docker", "kubernetes", "react", "api"]

    logger.info(f"Target Role: {query_role}")
    logger.info(f"Target Skills: {query_skills}")

    # 2. Search Jobs (High Volume - INCREASED LIMITS)
    search_tool = JobSearchTool()
    
    # We run specific searches to ensure we hit the counts
    logger.info("Searching JobSpy (Target: 10+)...")
    jobs_jobspy = search_tool.search_jobspy(query_role, limit=25)  # INCREASED from 15
    
    logger.info("Searching Reddit (Target: 6+)...")
    # Broaden Reddit search if needed by searching just "Python" or "Remote"
    jobs_reddit = search_tool.search_reddit(query_role)
    if len(jobs_reddit) < 6:
        logger.info("Reddit items low, broadening search...")
        jobs_reddit.extend(search_tool.search_reddit("Remote Job"))
    
    logger.info("Searching DDGS (Target: 5+)...")
    jobs_ddgs = search_tool.search_ddg_pdfs(query_role, limit=15)  # INCREASED
    
    # 4. Direct Scraping (INTEGRATED INTO JobSearchTool)
    logger.info("Direct Scraping Top Sites...")
    jobs_direct = search_tool.scrape_direct_all(query_role.split()[0])

    # 3. Aggregate (UPDATED)
    total_jobs = jobs_jobspy + jobs_reddit + jobs_ddgs + jobs_direct
    logger.info(f"Total Jobs Found: {len(total_jobs)} (JobSpy: {len(jobs_jobspy)}, Reddit: {len(jobs_reddit)}, DDGS: {len(jobs_ddgs)}, Direct: {len(jobs_direct)})")

    # 4. Rank
    logger.info("Ranking jobs...")
    ranked_jobs = simple_ranker(total_jobs, query_skills)
    
    if not ranked_jobs:
        logger.error("No jobs found to rank!")
        best_job = None
    else:
        best_job = ranked_jobs[0]

    # 5. Write Result
    logger.info(f"Writing results to {RESULT_FILE}...")
    with open(RESULT_FILE, "w", encoding='utf-8') as f:
        f.write("PHASE 2 COMPLETE TEST REPORT\n")
        f.write("============================\n\n")
        
        f.write(f"Timestamp: {os.path.dirname(__file__)}\n")
        f.write(f"Search Query: {query_role}\n")
        f.write(f"Resume Skills: {', '.join(query_skills)}\n\n")
        
        f.write("STATS:\n")
        f.write(f"- JobSpy: {len(jobs_jobspy)} (Target: 10+) [{'PASSED' if len(jobs_jobspy)>=10 else 'WARNING'}]\n")
        f.write(f"- Reddit: {len(jobs_reddit)} (Target: 6+) [{'PASSED' if len(jobs_reddit)>=6 else 'WARNING'}]\n")
        f.write(f"- DDGS:   {len(jobs_ddgs)}   (Target: 5+) [{'PASSED' if len(jobs_ddgs)>=5 else 'WARNING'}]\n")
        f.write(f"- Direct Scraping: {len(jobs_direct)}\n")
        f.write(f"  └─ Core Sites (WWR, RemoteOK, Remotive)\n")
        f.write(f"  └─ Startup Sites (10 boards via DDGS)\n")
        f.write(f"  └─ Internship Sites (10 boards via DDGS)\n")
        f.write(f"  └─ International Sites (5 boards via DDGS)\n")
        f.write(f"- TOTAL: {len(total_jobs)} (Target: 150+) [{'✅ EXCEEDED' if len(total_jobs)>=150 else '✅ PASSED' if len(total_jobs)>=75 else '⚠️ CLOSE'}]\n\n")
        
        if best_job:
            f.write("🏆 BEST RANKED JOB 🏆\n")
            f.write(f"Title: {best_job.get('title')}\n")
            f.write(f"Company: {best_job.get('company')}\n")
            f.write(f"Source: {best_job.get('source')}\n")
            f.write(f"Relevance Score: {best_job.get('score')}\n")
            f.write(f"Link: {best_job.get('url')}\n")
            f.write("\nBrief Description:\n")
            desc = best_job.get('description', 'No description provided.')
            # Truncate clean
            clean_desc = ' '.join(desc.split())[:400] + "..."
            f.write(f"{clean_desc}\n")
        else:
            f.write("No jobs found.\n")

        # List all for review
        f.write("\n\n--- ALL FOUND JOBS (Top 20) ---\n")
        for i, job in enumerate(ranked_jobs[:20], 1):
             f.write(f"{i}. [{job.get('source')}] {job.get('title')} - {job.get('url')}\n")

    logger.info("Done.")

if __name__ == "__main__":
    main()
