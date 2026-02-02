# CYNO CLI - The Career Intelligence Agent 🧠

> **"Stop being agreeable. Build the Ferrari."**

CYNO is a terminal-based autonomous agent designed for high-performance job seeking. It does not use a web UI. It operates directly in your shell to scrape, analyze, and generate career assets with zero latency.

## 🚀 Capabilities (The 50+ Tools)

### 1. Growth Hacking (`/net`)
Find the hidden job market that isn't on LinkedIn.
- **Find Leads**: `find leads for python` -> Scrapes Twitter, Reddit, HackerNews for "hiring" posts.
- **Deep Research**: `find company Stripe` -> Aggregates detailed intel for cover letters.
- **Smart Email**: `draft cold email for Google` -> Generates personalized outreach using AI.

### 2. Deep Interview Prep (`/prep`)
Don't just read LeetCode. Simulate the interview.
- **GitHub Deep Dive**: `analyze github <username>` -> Scans your *actual* code to predict technical questions.
- **System Design**: `prep design <project_name>` -> Generates a scaling challenge based on your specific project stack.
- **Behavioral**: `prep behavior <question>` -> Drafts STAR-method answers using your resume's context.

### 3. Application Engineering (`/app`)
- **Cover Letters**: `app cover <company> <role>` -> Writes authentic letters citing your real experience.
- **ATS Scoring**: `app score <job_description>` -> Brutally honest resume scoring.

## 🛠️ Installation

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Run the Agent
python -m cli
```

## 🧠 State & Persistence
CYNO remembers you.
- **State File**: `data/cli_state.json`
- **Resume**: Loaded once via `/resume <path>`, used forever.
- **History**: Context is preserved across sessions.

## ⚡ Quick Start Guide

| Intent | Command | Natural Language |
|--------|---------|------------------|
| **Load Resume** | `/resume my_resume.pdf` | "analyze my resume" |
| **Find Jobs** | `/jobs python remote` | "find python jobs" |
| **Get Leads** | `/net leads react` | "find leads for react" |
| **Draft Email** | `/net email cold <name>` | "draft email to Elon" |
| **Prep Code** | `/prep github <user>` | "analyze my github" |

---
*Built for speed. No browser required.*
