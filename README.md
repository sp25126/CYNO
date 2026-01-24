# 🚀 CYNO: The Autonomous Job Hunter (v6.6)
**Production-Grade AI Agent for Job Search & Applications**

![License](https://img.shields.io/badge/license-MIT-blue)
![Status](https://img.shields.io/badge/status-Phase%206%20Complete-green)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)

## 📖 Overview
Cyno is a sophisticated, autonomous agent designed to navigate the modern job market. Unlike basic scrapers, Cyno uses a **Hybrid Brain** approach:
-   **Local Client**: Lightweight, fast, and secure CLI for searching jobs across 20+ sources.
-   **Cloud Brain (GPU)**: Offloads heavy AI tasks (Resume Parsing, Email Drafting) to Google Colab/Cloud, ensuring <3s latency with 99% precision.

**Key Difference**: Cyno prioritizes **Link Precision**. It ignores generic search pages and only delivers direct "Apply" links.

---

## ✨ Key Features
-   **🔍 Precise Job Search**: Scours Indeed, LinkedIn, Glassdoor, Wellfound, RemoteOK, and Freelance platforms. Returns *only* direct listing URLs.
-   **📄 AI Resume Parsing**: Uses **Llama-3.2 (OCR)** to extract skills and experience with human-level accuracy.
-   **✉️ Smart Email Drafter**: context-aware cover letters that map your resume skills to the job description.
-   **📂 Organized Output**: Automatically sorts results into `internships/`, `freelance/`, `leads/`, and `jobs/`.
-   **💰 100% Free**: Designed to run on free tiers (Colab T4 GPU, Local CPU). No OpenAI API key required.

---

## 🛠️ Architecture
-   **`scripts/cli_chat.py`**: The Command Line Interface (CLI) and main agent loop.
-   **`cloud/COLAB_DEPLOY_OCR.py`**: The Cloud Brain server (FastAPI) to deploy on Google Colab.
-   **`tools/job_search.py`**: Advanced Scraper Engine (JobSpy + Direct + Freelance).
-   **`AI_CONTINUATION_PROMPT.md`**: Strict instructions for AI developers.

---

## 🚀 Quick Start

### 1. Installation
```bash
# Clone the repo
git clone https://github.com/sp25126/CYNO.git
cd CYNO

# Create Virtual Environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configure Cloud Brain (Optional but Recommended)
1.  Upload `cloud/COLAB_DEPLOY_OCR.py` to Google Colab.
2.  Run the notebook to get your `ngrok` public URL.
3.  Create a `.env` file (or `credentials_setup.env`):
    ```env
    COLAB_SERVER_URL=https://your-ngrok-url.ngrok-free.app
    ```

### 3. Run the Agent
```bash
python scripts/cli_chat.py
```

### 4. Commands
-   **Find Jobs**: `find python jobs`, `find react internships`
-   **Find Freelance**: `find photoshop freelance`
-   **Draft Email**: `draft email for job #1`
-   **Get Leads**: `scrape leads for python`

---

## 🗺️ Roadmap
-   [x] **Phase 1-6**: Core Search, Cloud Brain, Precision Scrapers.
-   [ ] **Phase 7**: Selenium Automation ("Auto-Apply").
-   [ ] **Phase 8**: GUI Dashboard.
-   [ ] **Phase 9**: Fully Autonomous Mode.

---

## 🤝 Contributing
Read **`HANDOVER_AND_ROADMAP.md`** for the developer guide. Code must be production-grade, modular, and 100% free.

**Maintainers**: Saumya Patel & Cyno Agent.
