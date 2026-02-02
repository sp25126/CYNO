# CYNO Job Agent (v6.2 Legacy Snapshot) - Professional Setup Guide

This branch contains the stable snapshot of the Cyno Job Agent (version 6.2). It includes the full capabilities for automated job searching, resume parsing, and application automation as they existed prior to the Production Hardening phase.

## 📋 System Requirements
- **Python**: 3.10 or higher
- **Node.js**: 16+ (for future frontend)
- **OS**: Windows, macOS, or Linux

## 🛠️ Step-by-Step Installation

### 1. Environment Setup
Create a virtual environment to isolate dependencies:
```bash
python -m venv venv
```

Activate the environment:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### 2. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### 3. Configuration
1. **Credentials**: Rename `credentials_setup.env` to `.env`:
   ```cmd
   copy credentials_setup.env .env
   ```
2. **Edit .env**: Open `.env` and fill in your API keys (Gemini, LinkedIn, etc.).

### 4. Resume Setup
1. Place your PDF resume in the `resumes/` folder.
2. The agent will automatically detect and parse it on first run.

## 🚀 Running the Agent
There are two ways to launch CYNO:

### Option A: Interactive CLI (Recommended)
This provides the full command-line experience.
```bash
python scripts/run_agent.py
```

### Option B: Quick Start
Use the included batch file (Windows only):
```cmd
start-cyno.bat
```

## 📂 Project Structure
- `agent/`: Core AI logic (Brain, Personality, Router)
- `tools/`: The 50+ tool implementations (Scrapers, Emailers)
- `cli/`: Terminal user interface
- `data/`: Local database storage
- `resumes/`: Your resume PDF storage
- `leads/`: Exported job leads (CSV)

---
*Note: This is a legacy snapshot. For the latest "Production Hardened" version, switch to the `production-cli-v1` branch.*
