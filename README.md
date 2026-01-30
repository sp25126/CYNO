# 🤖 CYNO - AI-Powered Job Search Agent

> ⚠️ **PROTOTYPE STATUS**: This project is currently a **working prototype** demonstrating AI-powered job search automation. It is not production-ready for general use but serves as a proof-of-concept for intelligent job application assistance.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Prototype](https://img.shields.io/badge/Status-Prototype-orange.svg)]()

---

## 🎯 What is CYNO?

CYNO (Cybernetic Yield Navigator for Opportunities) is an AI-powered job search agent that automates and enhances the job hunting process. It uses a **Cloud GPU Brain** (hosted on Google Colab) to perform intelligent tasks like resume parsing, cover letter generation, interview preparation, and more.

### Key Features

| Category | Capabilities |
|----------|-------------|
| **Job Discovery** | Salary estimation, tech stack analysis, company research |
| **Application** | Cover letter generation, ATS scoring, resume tailoring |
| **Interview Prep** | Behavioral Q&A, system design practice, project deep-dives |
| **Outreach** | Smart emails, follow-up reminders, recruiter finding |
| **Analytics** | Application tracking, success pattern analysis |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CYNO System                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐     ┌──────────────┐     ┌────────────┐  │
│   │  CLI Chat   │ ──▶ │  NLP Router  │ ──▶ │  53 Tools  │  │
│   └─────────────┘     └──────────────┘     └────────────┘  │
│                              │                     │        │
│                              ▼                     ▼        │
│                       ┌──────────────┐     ┌────────────┐  │
│                       │  LLM Brain   │ ◀── │Cloud Client│  │
│                       └──────────────┘     └────────────┘  │
│                              │                     │        │
└──────────────────────────────│─────────────────────│────────┘
                               ▼                     ▼
                    ┌─────────────────────────────────────┐
                    │       Google Colab GPU Server       │
                    │     (Cloud Brain v6.0 via ngrok)    │
                    └─────────────────────────────────────┘
```

---

## 📋 Prerequisites

- **Python 3.11+**
- **Google Account** (for Colab GPU access)
- **ngrok Account** (free tier works) - [Get token here](https://dashboard.ngrok.com/get-started/your-authtoken)

---

## 🚀 Quick Start

### Step 1: Clone the Repository

```bash
git clone https://github.com/sp25126/CYNO.git
cd CYNO
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install requests structlog jobspy pydantic python-dotenv
```

### Step 3: Set Up Cloud Brain (Google Colab)

1. Open [Google Colab](https://colab.research.google.com)
2. Create a new notebook
3. Copy the entire contents of `cloud/UNIVERSAL_GPU_SERVER.py` into a cell
4. **Update the `NGROK_TOKEN`** with your token from [ngrok dashboard](https://dashboard.ngrok.com)
5. Run the cell (takes 2-3 minutes to load the model)
6. Copy the generated ngrok URL (e.g., `https://xxxx.ngrok-free.app`)

### Step 4: Configure Environment

Create a `.env` file in the project root:

```env
COLAB_SERVER_URL=https://xxxx.ngrok-free.app
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=gemma2:2b
```

### Step 5: Run CYNO

```bash
python scripts/cli_chat.py
```

---

## 🛠️ Tool Categories

### Discovery Tools
| Tool | Description |
|------|-------------|
| `SalaryEstimatorTool` | Estimates salary ranges for roles |
| `TechStackDetectorTool` | Analyzes job descriptions for tech requirements |
| `InterviewQuestionFinderTool` | Generates company-specific interview questions |

### Application Tools
| Tool | Description |
|------|-------------|
| `CoverLetterGeneratorTool` | Creates personalized cover letters |
| `ATSScorerTool` | Scores resume against job descriptions |
| `SkillGapAnalyzerTool` | Identifies missing skills |

### Interview Prep Tools
| Tool | Description |
|------|-------------|
| `ProjectDeepDiveTool` | Analyzes GitHub repos for interview prep |
| `BehavioralAnswerBankTool` | Generates STAR-format answers |
| `SystemDesignSimulatorTool` | Creates system design challenges |

### Advanced AI Tools
| Tool | Description |
|------|-------------|
| `JobFitScorerTool` | Semantic matching of resume to job |
| `WeaknessSpinDoctorTool` | Helps frame weaknesses positively |
| `PersonalBrandBuilderTool` | Creates consistent professional bios |

### Utility Tools
| Tool | Description |
|------|-------------|
| `JobDescriptionSummarizerTool` | Summarizes long JDs |
| `RecruiterFinderTool` | Suggests recruiter search strategies |
| `CourseRecommenderTool` | Recommends learning resources |

---

## 📁 Project Structure

```
CYNO/
├── agent/
│   ├── llm_brain.py        # Unified LLM interface
│   └── nlp_router.py       # Intent detection & routing
├── cloud/
│   ├── UNIVERSAL_GPU_SERVER.py  # Colab server script
│   └── enhanced_client.py       # Cloud client with fallback
├── tools/
│   ├── advanced_ai.py      # AI-powered tools
│   ├── analytics_tools.py  # Tracking & analysis
│   ├── discovery_tools.py  # Job research tools
│   ├── interview_prep.py   # Interview preparation
│   ├── utility_tools.py    # General utilities
│   └── ... (50+ tool files)
├── scripts/
│   ├── cli_chat.py         # Main CLI interface
│   └── live_test.py        # System test script
├── data/
│   └── user_prefs_template.json
└── README.md
```

---

## 🧪 Testing

Run the comprehensive test suite:

```bash
python scripts/live_test.py
```

This tests all 17 core tools against the live Cloud Brain.

**Latest Test Results**: 17/17 PASSED ✅

---

## ⚠️ Prototype Limitations

This is a **prototype** with the following limitations:

| Limitation | Description |
|------------|-------------|
| **Cloud Dependency** | Requires active Colab session (12-hour limit) |
| **No Authentication** | No user accounts or data persistence |
| **Manual Setup** | Requires manual Colab deployment each session |
| **Rate Limits** | Subject to ngrok and Colab rate limits |
| **No UI** | CLI-only interface |

### Roadmap for Production

- [ ] Persistent cloud deployment (AWS/GCP)
- [ ] User authentication & profiles
- [ ] Web/Desktop GUI (Flet/Electron)
- [ ] Database integration (PostgreSQL)
- [ ] Email integration (for actual applications)
- [ ] Scheduled job alerts

---

## 🤝 Contributing

This is a prototype project. Contributions are welcome for:

1. Bug fixes
2. New tool implementations
3. UI development
4. Documentation improvements

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- **Llama 3.2** by Meta for the base LLM
- **Google Colab** for free GPU access
- **ngrok** for tunneling
- **JobSpy** for job aggregation

---

<p align="center">
  <b>Built with ❤️ by sp25126</b><br>
  <i>CYNO - Your AI Job Search Partner</i>
</p>
