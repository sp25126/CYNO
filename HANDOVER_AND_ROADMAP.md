# 📘 CYNO AGENT: HANDOVER & ROADMAP GUIDE (v6.6)
**Date:** 2026-01-23
**Status:** Phase 6 Complete (Cloud AI + Precision Scrapers)

---

## 🚀 1. System Snapshot (Current State)
The Cyno Job Agent is now a **Hybrid AI System**:
- **Local Client**: Runs on user's PC (`scripts/cli_chat.py`). Handles scrapers, file management, and UI.
- **Cloud Brain**: Runs on Google Colab (`cloud/COLAB_DEPLOY_OCR.py`). Handles heavy AI tasks (Resume OCR, Email Drafting).

### ✅ Key Capabilities
1.  **Precise Job Search**: scours Indeed, LinkedIn, Glassdoor, WWR, RemoteOK, and Freelance sites. Returns **ONLY direct job/project links**.
2.  **Smart Resume Parsing**: Uses **Llama-3.2-3B (Cloud)** to extract skills ("Python", "React") and profile type from PDFs.
3.  **Professional Emailing**: Drafts tailored cover letters using specific resume skills, avoiding hallucinations.
4.  **Organized Output**:
    *   Internships → `internships/`
    *   Freelance → `freelance/` (configured for next run)
    *   Leads → `leads/`
    *   General Jobs → `jobs/`

---

## 🛠️ 2. Architecture & Critical Files

### 🧠 Cloud Brain (The Intelligence)
- **File**: `cloud/COLAB_DEPLOY_OCR.py`
- **Role**: FastAPI server running on Colab GPU.
- **Models**: `Llama-3.2-3B-Instruct` (Text Gen), `parsurya/resume-parser-bert` (Legacy/Fallback).
- **Endpoints**: `/parse_resume_pdf`, `/draft_email`.
- **Note**: **Must be deployed manually** by user on Colab. URL stored in `.env` (`COLAB_SERVER_URL`).

### 🔍 Search Engine (The Scrapers)
- **File**: `tools/job_search.py`
- **Logic**:
    *   **Level 1 (API-like)**: JobSpy (Indeed, LinkedIn, Glassdoor). **NO GOOGLE** (removed for precision).
    *   **Level 2 (Direct)**: `tools/direct_scrapers.py` (WWR, RemoteOK, Remotive).
    *   **Level 3 (Freelance)**: `tools/freelance_scrapers.py` (Upwork RSS, Freelancer, Guru).
    *   **Level 4 (Extended)**: `tools/extended_job_scrapers.py` (Wellfound, YC, Arc).
    *   **DISABLED**: `tools/site_search.py` (Hybrid DDGS) - *Do not re-enable without strict filters.*

### 🖥️ CLI (The Interface)
- **File**: `scripts/cli_chat.py`
- **Role**: Terminal chat interface.
- **Tools**: `scrape_leads`, `draft_email`, `search_jobs`.

---

## 📜 3. Work Completed (Phase 6 Summary)
We transformed the agent from a local script to a cloud-powered precise hunter.

| Feature | Old State | New State (v6.6) |
|---------|-----------|------------------|
| **Resume Parsing** | Simple Text Extraction (imprecise) | **OCR + Llama-3.2** (High precision) |
| **Scrapers** | Included generic Google/DDG searches | **Strictly Direct Links Only** |
| **Emailing** | Generic templates | **Skill-Aware & Professional** |
| **Speed** | Slow (Local CPU) | **Fast (Cloud GPU)** |
| **Organization** | Single folder | **Categorized Folders** |

---

## 🗺️ 4. Roadmap (What's Next?)

### ➤ Phase 7: Selenium & Unrestricted Access (Feb 1-5)
**Goal**: Access restricted job boards blocked by traditional HTTP requests & Start "Clicking".
- [ ] **Selenium Scraper Foundation**: Create `tools/selenium_scrapers.py` with `undetected-chromedriver`.
    - Purpose: Bypass 403s on strict sites (e.g. Wellfound complex pages) & Enable "Auto-Apply".
- [ ] **Social Enhancements**: Expand Leads scraper to specific subreddits (r/forhire) and Twitter.

### ➤ Phase 8: Professional Architecture & Security (Feb 6-10)
**Goal**: Enterprise-grade scalability.
- [ ] **Plugin System**: Move scrapers to `plugins/` for hot-loading.
- [ ] **Security**: Encrypt data in transit to Cloud GPU.

### ➤ Phase 9: Proactive Human-Like Agency (Feb 11-15)
**Goal**: "Run while I sleep" & "Think for me".
- [ ] **Goal Engine**: Create `agent/goal_engine.py` to identify "Career Missions".
- [ ] **Context Memory**: Suggest learning paths based on job gaps.
- [ ] **Auto-Apply**: Use Phase 7 Selenium foundation to fill applications.

---

## 🤖 5. Notes for Future AI Agents
If you are picking up this project, please observe:

1.  **Precision is King**: Do not add scrapers that rely on `site:domain.com query`. They return search pages and frustrate the user. Stick to direct listing endpoints.
2.  **Resume Parsing**: The `parse_resume_pdf` endpoint returns structured JSON including `original_text`, `skills` (list), and `experience_years`. Use these for personalization.
3.  **Environment**: 
    *   User OS: Windows.
    *   Python: `C:\sp\ai-agent\ai_agent_env\Scripts\python.exe`.
    *   **Always check `.env`** for the ngrok URL validity.
4.  **Testing**: Before committing changes, run the `find python jobs` command manually to verify link precision.

---
**Maintained by**: Cyno Development Team (Saumya & Agent)
