# 🚀 Cyno: The Autonomous Job Search Roadmap (v6.2)

Welcome to the future of career acceleration. This roadmap outlines the evolution of Cyno—from a simple search tool into a proactive, voice-controlled, and human-like intellectual partner.

---

## 🏗️ Part 1: The Foundation (Completed)
These phases are already built and functional. They form the core "brain" and "eyes" of Cyno.

### Phase 1-3: Intelligence & Search Ecosystem
- **Resume Intelligence**: 50+ data points (Personality, Trajectory, Match Scoring).
- **Search Aggregator**: 14+ sources (LinkedIn, Indeed, Hacker News, Freelance Boards).
- **Intelligent Matcher**: 5-factor scoring (Skills, Experience, Salary, etc.).
- **Email Drafter**: Auto-generating personalized outreach.

### Phase 4-5: Production Hardening & Autonomy
- **Infrastructure**: Centralized `config.py`, resource management, and SQLite memory.
- **Safety**: Git-based **Auto-Revert** system (Rolls back bugs in <60s).
- **Notifications**: Instant updates via **WhatsApp, Telegram, and Discord**.
- **Self-Improvement**: Cyno automatically identifies and fixes its own scraper timeouts.

---

## 🎙️ Part 2: Phase 6 - The Proactive AI Era (Upcoming)

### 🗓️ Week 1: Voice Control & Senses (Jan 21-25)
**Goal**: Enable hands-free voice control via background Windows service.

#### Day 1: Wake Word Detection
- **Task**: Create `voice/wake_word.py` using Porcupine (free tier).
- **Steps**:
  1. Implement background listening.
  2. Map wake word "Hey Cyno" to trigger command mode.
  3. Hook into existing `query_parser.py`.

#### Day 2: Speech recognition
- **Task**: Create `voice/command_processor.py` with OpenAI Whisper (tiny model).
- **Steps**:
  1. Run Whisper Tiny locally for fast, high-accuracy transcription.
  2. Implement fallback to Google Speech API (60 min/mo free).
  3. Connect voice commands to `HRChatAgent`.

#### Day 3: Background Service & TTX
- **Task**: Create `voice/voice_service.py` as a Windows background service.
- **Steps**:
## 🎙️ Part 2: The Proactive AI Era (Upcoming Phase 6)

### Week 1: Voice Control & Hotkeys (DEPRIORITIZED)
> [!WARNING]
> Skipped on Jan 20, 2026. Performance analysis showed Voice/Hotkey features were distractions. **Focus shifted to latency reduction.**
- **Status**: Hotkey Service (`Ctrl+Shift+Z`) implemented but secondary.
- **Decision**: Moving directly to Cloud GPU for speed.

### Week 2: Cloud GPU & Performance (✅ COMPLETE - Jan 21, 2026)
**Goal**: Make heavy AI tasks faster using external power.
- **Step 2.1**: ✅ Set up **Free Cloud GPU Server** 
    - **Stack**: Google Colab + FastAPI + `TinyLlama-1.1B` (Quantized)
    - **Tunneling**: Switched to `zrok` for stable, persistent public URLs.
- **Step 2.2**: ✅ Built **Robust Cloud Client**
    - **Features**: Auto-retry, JSON repair, and transparent local fallback.
    - **Performance**: Reduced parse time from ~45s (CPU) to <3s (Cloud GPU).
- **Step 2.3**: ✅ **System Stabilization**
    - Fixed critical bugs in Email Drafter (`ChatOllama` resource management).
    - Resolved Pydantic validation errors across all tools.

> [!NOTE]
> The system is now technically "Hybrid". It prefers Cloud for heavy lifting but fully functions offline/locally if the internet drops.

---

### 🗓️ Week 3: Selenium & Unrestricted Access (Feb 1-5)
**Goal**: Access restricted job boards blocked by traditional HTTP requests.

#### Day 1: Selenium Scraper Foundation
- **Task**: Create `tools/selenium_scrapers.py` with `undetected-chromedriver`.
- **Steps**:
  1. Map `scrape_weworkremotely()`, `scrape_himalayas()`, and `scrape_wellfound()`.
  2. Implement human-like scrolling and delay patterns to avoid 403s.

#### Day 2: Social & Community Sourcing
- **Task**: Create `tools/reddit_freelance.py` and `tools/twitter_leads.py`.
- **Steps**:
  1. Scrape r/forhire and r/hiring for direct client posts.
  2. Use `snscrape` to find hiring tweets with personal emails.
  3. **Outcome**: +50 extra high-quality jobs per daily search.

---

### 🗓️ Week 4: Professional Architecture & Security (Feb 6-10)
**Goal**: Prepare for enterprise-grade scalability.

#### Day 1: Plugin & Registry Refactor
- **Task**: Move all scrapers to `plugins/` directory.
- **Steps**:
  1. Implement `PluginBase` and `PluginManager` for hot-loading new sites.
  2. Add `hot_reload.py` to update the brain without restarting the app.

#### Day 2: Security & Encryption
- **Task**: Implement `security/auth.py` and `security/encryption.py`.
- **Steps**:
  1. Add Fernet encryption for data in transit to Cloud GPU.
  2. Move all API keys to Windows Credential Manager (Zero hardcoding).

---

### 🗓️ Week 5: Proactive Human-Like Agency (Feb 11-15) ⭐ NEW
**Goal**: Give Cyno a "Soul" that thinks and acts on its own.

#### Day 1: Mission-Based Proactivity
- **Task**: Create `agent/goal_engine.py`.
- **Steps**:
  1. Automatically identifies "Career Missions" (e.g., "Find Lead Python Role").
  2. Monitors match scores in the background.
  3. **Function**: Pings you via Telegram ONLY when a 90%+ match is found.

#### Day 2: Skills Roadmap & Market Intel
- **Task**: Create `agent/context_memory.py`.
- **Steps**:
  1. Stores deep memory of user preferences and conversation history.
  2. **Intelligence**: Suggests learning paths: "If you learn AWS, I can double your match score for these 12 jobs."

---

## 📈 Success Metrics (Our Promise)

| Metric | Reactive Cyno (Before) | Proactive Cyno (After) |
| :--- | :---: | :---: |
| **User Effort** | Manual Search Required | **Autonomous Monitoring** |
| **Response Time** | 90+ Seconds | **Under 10 Seconds** |
| **Job Sources** | 14 Sources | **20+ Global Sources** |
| **Intelligence** | Keyword Matching | **Human-Like Reasoning** |
| **Cost** | $0 | **Still $0 (100% Free)** |

---

**Current Progress**: 95% of Foundation Complete.  
**Next Call to Action**: `python scripts/cli_chat.py` to experience the current brain.
