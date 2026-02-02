# 📘 CYNO Setup Guide

> **Complete installation and configuration guide for CYNO - AI Job Search Agent**

---

## Table of Contents

1. [Prerequisites](#-prerequisites)
2. [Installation](#-installation)
3. [Cloud Brain Setup](#-cloud-brain-setup)
4. [Configuration](#-configuration)
5. [Running CYNO](#-running-cyno)
6. [Troubleshooting](#-troubleshooting)
7. [FAQ](#-faq)

---

## 📋 Prerequisites

### Required Software

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |
| Ollama | Latest | [ollama.ai](https://ollama.ai/) |

### Required Accounts (Free)

| Service | Purpose | Sign Up |
|---------|---------|---------|
| Google Account | Colab GPU access | [accounts.google.com](https://accounts.google.com) |
| ngrok | Cloud tunneling | [ngrok.com](https://ngrok.com/) |

---

## 🛠️ Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/sp25126/CYNO.git
cd CYNO
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
.\venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install Local Ollama (Fallback)

```bash
# Download from ollama.ai, then:
ollama pull gemma2:2b
```

---

## ☁️ Cloud Brain Setup

The Cloud Brain provides 18x faster AI processing using Google's free T4 GPU.

### Step 1: Get ngrok Auth Token

1. Go to [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken)
2. Sign up or log in
3. Copy your authtoken

### Step 2: Open Google Colab

1. Go to [Google Colab](https://colab.research.google.com)
2. Click **File → New Notebook**
3. Click **Runtime → Change runtime type**
4. Select **T4 GPU** → Click **Save**

### Step 3: Deploy Server

Paste this code into the first cell:

```python
# CYNO Cloud Brain Deployment
# Run this cell to start the server

# Install dependencies
!pip install -q fastapi uvicorn pyngrok transformers accelerate

# Clone and run server
!wget -q https://raw.githubusercontent.com/sp25126/CYNO/26012026(6.2)/cloud/colab_server.py

# Add your ngrok token
NGROK_TOKEN = "YOUR_NGROK_TOKEN_HERE"  # ← Replace this!

from colab_server import start_server
start_server(ngrok_token=NGROK_TOKEN)
```

### Step 4: Note Your Server URL

After ~2 minutes, you'll see:
```
✅ SERVER READY
🌐 Public URL: https://abc123.ngrok.io
```

**Copy this URL** — you'll need it for configuration.

---

## ⚙️ Configuration

### Step 1: Create Environment File

```bash
cp credentials_template.env .env
```

### Step 2: Edit .env File

Open `.env` in your editor and add your values:

```env
# Required
NGROK_AUTH_TOKEN=your_ngrok_token_here
COLAB_SERVER_URL=https://your-url.ngrok.io

# Optional: Notifications
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
DISCORD_WEBHOOK_URL=
```

### Step 3: Add Your Resume (Optional)

Create `data/resume.md` with your resume in markdown format:

```markdown
# John Doe

## Contact
- Email: john@example.com
- Phone: +1-555-0123
- Location: San Francisco, CA

## Summary
Senior Software Engineer with 5+ years experience...

## Skills
- Python, JavaScript, Go
- AWS, Docker, Kubernetes
- Machine Learning, NLP

## Experience
### Senior Engineer @ TechCorp (2020-Present)
- Led team of 5 engineers...
```

---

## 🚀 Running CYNO

### Interactive CLI Mode

```bash
python scripts/cli_chat.py
```

**Example conversation:**
```
You: Find me remote Python developer jobs
CYNO: 🔍 Searching 14 sources...
      Found 47 matches. Top 5:
      1. Senior Python Dev @ Stripe (95% match)
      2. Backend Engineer @ GitLab (92% match)
      ...
```

### Health Check

```bash
python scripts/health_check.py
```

**Expected output:**
```
✅ Ollama: Running (gemma2:2b)
✅ Cloud Brain: Connected (T4 GPU)
✅ Resume Parser: Working
✅ Job Search: 14/14 sources
```

### Autonomous Mode

```bash
python scripts/autonomous_run.py
```

This runs CYNO in the background, checking for new job matches periodically.

---

## 🔧 Troubleshooting

### Cloud Brain Issues

| Issue | Solution |
|-------|----------|
| "No server URL configured" | Add `COLAB_SERVER_URL` to `.env` |
| "Connection timeout" | Check Colab notebook is running |
| "ngrok tunnel expired" | Restart Colab notebook |
| "Colab disconnected" | Free tier auto-disconnects after 12h — restart notebook |

### Local Fallback Issues

| Issue | Solution |
|-------|----------|
| "Ollama not found" | Run `ollama serve` in a separate terminal |
| "Model not found" | Run `ollama pull gemma2:2b` |
| "Slow response" | Expected — CPU is 18x slower than Cloud GPU |

### Installation Issues

| Issue | Solution |
|-------|----------|
| "pip install failed" | Try: `pip install --upgrade pip` first |
| "Permission denied" | Run terminal as Administrator (Windows) |
| "Module not found" | Ensure venv is activated |

---

## ❓ FAQ

### Q: Is this really free?
**A:** Yes! Google Colab provides ~15 hours/day of free T4 GPU. ngrok free tier gives 40 hours/month of tunneling.

### Q: What if my Cloud Brain disconnects?
**A:** CYNO automatically falls back to local Ollama (slower but works offline).

### Q: How do I update CYNO?
```bash
git pull origin 26012026(6.2)
pip install -r requirements.txt
```

### Q: Can I use my own resume?
**A:** Yes! Create `data/resume.md` with your resume in markdown format.

### Q: Is my data private?
**A:** Your resume data is sent to Colab (Google servers) temporarily for processing. Do NOT use for highly sensitive data. All results are stored locally.

### Q: How many job sources are supported?
**A:** Currently 14+ sources including:
- LinkedIn (limited)
- Indeed
- Glassdoor
- HackerNews Who's Hiring
- RemoteOK
- WeWorkRemotely
- Freelancer, Upwork, Fiverr
- And more...

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/sp25126/CYNO/issues)
- **Discussions:** [GitHub Discussions](https://github.com/sp25126/CYNO/discussions)

---

<p align="center">
  <sub>⚠️ Remember: This is a PROTOTYPE. Expect bugs and breaking changes.</sub>
</p>
