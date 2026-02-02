<p align="center">
  <img src="https://img.shields.io/badge/🤖_CYNO-AI_Job_Agent-blueviolet?style=for-the-badge&logoColor=white" alt="CYNO Logo"/>
</p>

<h1 align="center">CYNO - Cybernetic Yield Navigator for Opportunities</h1>

<p align="center">
  <img src="https://img.shields.io/badge/⚠️_PROTOTYPE-Not_Production_Ready-orange?style=for-the-badge" alt="Prototype Warning"/>
</p>

<p align="center">
  <a href="#-quick-start"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.11+"/></a>
  <a href="#-architecture"><img src="https://img.shields.io/badge/Cloud-Google_Colab-F9AB00?style=flat-square&logo=googlecolab&logoColor=white" alt="Google Colab"/></a>
  <a href="#-tool-categories"><img src="https://img.shields.io/badge/Tools-50+-success?style=flat-square" alt="50+ Tools"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT License"/></a>
</p>

<p align="center">
  <strong>An AI-powered job search agent that automates job discovery, resume matching, and interview preparation.</strong>
</p>

---

## ⚠️ Prototype Disclaimer

> **This is a prototype/proof-of-concept.** It demonstrates the core functionality of an AI job search agent but is **NOT production-ready**. Expect bugs, incomplete features, and breaking changes.

**Current Limitations:**
- Cloud Brain requires manual Colab restart every ~12 hours
- Some job scrapers may break due to website changes
- No persistent database (SQLite for sessions only)
- Limited error recovery in edge cases

**See [Roadmap](#-roadmap) for planned improvements.**

---

## 🎯 What is CYNO?

CYNO is an intelligent job search assistant that combines:

- **🔍 Multi-Source Job Discovery** - Aggregates jobs from 14+ platforms (LinkedIn, Indeed, HackerNews, Freelance boards)
- **🧠 AI-Powered Resume Analysis** - Extracts 50+ data points including personality traits and career trajectory
- **🎯 Intelligent Job Matching** - 5-factor scoring algorithm (Skills, Experience, Salary, Culture, Growth)
- **✉️ Personalized Outreach** - Auto-generates tailored cover letters and cold emails
- **🎤 Interview Preparation** - Mock interviews with AI feedback

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CYNO System v6.2                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐    ┌──────────────┐    ┌────────────────┐    │
│   │  CLI Chat   │───▶│  NLP Router  │───▶│   50+ Tools    │    │
│   └─────────────┘    └──────────────┘    └────────────────┘    │
│                              │                    │             │
│                              ▼                    ▼             │
│                      ┌──────────────┐    ┌────────────────┐    │
│                      │  LLM Brain   │◀───│  Cloud Client  │    │
│                      └──────────────┘    └────────────────┘    │
│                                                  │              │
└──────────────────────────────────────────────────│──────────────┘
                                                   ▼
                        ┌─────────────────────────────────────┐
                        │     Google Colab GPU Server         │
                        │   (Cloud Brain v6.2 via ngrok)      │
                        └─────────────────────────────────────┘
```

**Hybrid Architecture**: Runs heavy AI tasks on free Cloud GPU, falls back to local Ollama when offline.

---

## 📋 Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Runtime |
| Google Account | - | Colab GPU access (free) |
| ngrok Account | Free tier | Cloud tunneling |
| Ollama | Latest | Local LLM fallback |

---

## 🚀 Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/sp25126/CYNO.git
cd CYNO
```

### Step 2: Install Dependencies
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

### Step 3: Set Up Cloud Brain (Google Colab)

1. Open [Google Colab](https://colab.research.google.com)
2. Create new notebook → Runtime → Change runtime type → **T4 GPU**
3. Copy contents of `cloud/colab_server.py` into a cell
4. Run the cell — note the **ngrok URL** displayed

### Step 4: Configure Environment
```bash
# Copy template and edit with your values
cp credentials_template.env .env

# Add your ngrok URL
echo "COLAB_SERVER_URL=https://your-url.ngrok.io" >> .env
```

### Step 5: Run CYNO
```bash
python scripts/cli_chat.py
```

**For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).**

---

## 🛠️ Tool Categories

### Discovery Tools (14 Sources)
| Tool | Description |
|------|-------------|
| `job_search.py` | Multi-platform job aggregator |
| `direct_scrapers.py` | Direct API scrapers |
| `freelance_scrapers.py` | Upwork, Fiverr, Freelancer |
| `extended_job_scrapers.py` | HackerNews, StackOverflow Jobs |
| `lead_scraper.py` | Lead generation tools |

### Application Tools
| Tool | Description |
|------|-------------|
| `resume_parser.py` | AI-powered resume analysis |
| `advanced_resume_parser.py` | Deep resume insights (50+ fields) |
| `resume_tailor.py` | Job-specific resume optimization |
| `email_drafter.py` | Personalized outreach emails |

### Matching & Analytics
| Tool | Description |
|------|-------------|
| `intelligent_job_matcher.py` | 5-factor matching algorithm |
| `job_matcher.py` | Quick match scoring |

### Utility Tools
| Tool | Description |
|------|-------------|
| `notifier.py` | Telegram/Discord/WhatsApp alerts |
| `memory.py` | Conversation context storage |
| `file_ops.py` | File management utilities |

---

## 📁 Project Structure

```
CYNO/
├── agent/                    # Core AI components
│   ├── llm_brain.py         # Unified LLM interface
│   └── nlp_router.py        # Intent detection & routing
│
├── cloud/                    # Cloud GPU integration
│   ├── colab_server.py      # Colab deployment script
│   ├── cloud_client.py      # Client with fallback
│   ├── README.md            # Cloud setup guide  
│   └── DEPLOY_GUIDE.md      # Deployment instructions
│
├── tools/                    # 50+ specialized tools
│   ├── job_search.py        # Main search aggregator
│   ├── resume_parser.py     # Resume analysis
│   ├── email_drafter.py     # Email generation
│   └── ...
│
├── scripts/                  # CLI & automation
│   ├── cli_chat.py          # Main CLI interface
│   ├── health_check.py      # System diagnostics
│   └── autonomous_run.py    # Background agent
│
├── data/                     # User data (gitignored)
├── docs/                     # Documentation
│
├── config.py                 # Central configuration
├── models.py                 # Pydantic data models
├── requirements.txt          # Python dependencies
├── credentials_template.env  # Env template
├── SETUP_GUIDE.md           # Detailed setup
└── README.md                # This file
```

---

## 🧪 Testing

### Health Check
```bash
python scripts/health_check.py
```

### Full System Test
```bash
python scripts/final_verification.py
```

**Expected Output:**
```
✅ Cloud Brain: Connected (T4 GPU)
✅ Resume Parser: Working
✅ Job Search: 14/14 sources active
✅ Email Drafter: Ready
```

---

## 🗺️ Roadmap

### Completed ✅
- [x] Multi-source job aggregation (14+ platforms)
- [x] AI resume parsing (Cloud GPU accelerated)
- [x] Intelligent job matching
- [x] Email/Cover letter generation
- [x] Cross-platform notifications

### In Progress 🔄
- [ ] Selenium scrapers for restricted sites
- [ ] Plugin architecture for hot-loading
- [ ] Encrypted credential storage

### Planned 📝
- [ ] Voice control (Wake word + Whisper)
- [ ] Proactive job monitoring
- [ ] Skills gap analysis
- [ ] Market intelligence reports

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Google Colab** - Free GPU compute
- **ngrok** - Secure tunneling
- **Ollama** - Local LLM serving
- **LangChain** - LLM orchestration

---

<p align="center">
  <strong>Built with ❤️ for job seekers everywhere</strong>
</p>

<p align="center">
  <sub>⚠️ Remember: This is a PROTOTYPE. Use at your own risk.</sub>
</p>
