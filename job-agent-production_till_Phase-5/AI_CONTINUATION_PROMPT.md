# 🚀 CYNO Job Agent - AI Development Continuation Prompt

**Project Status**: Phase 4 Complete (Production Ready)  
**Last Updated**: January 7, 2026  
**Next Phase**: Production Hardening & Advanced Features

---

## 📋 EXECUTIVE SUMMARY

You are continuing development of **Cyno**, an intelligent job search agent that:
- Auto-parses resumes using LLM
- Searches 500+ job sites globally
- Matches jobs using semantic AI
- Drafts personalized emails
- Applies intelligent filters
- Maintains conversation memory

**Your Mission**: Analyze the current codebase and make it **production-grade** while maintaining **zero-cost** operations and **fault-tolerant** architecture.

---

## ✅ COMPLETED WORK (Phases 1-4)

### Phase 1: Foundation ✅
**What Was Built**:
- Pydantic models: `Resume`, `Job`, `EmailDraft`, `Session`
- Ollama integration (local LLM: gemma2:2b, qwen2.5:3b)
- Data validation with strict schemas

**Key Files**:
- `models.py`: All Pydantic schemas
- `agent/chat_agent.py`: Dual-LLM agent (tool_llm for JSON, chat_llm for persona)

**Status**: ✅ Production-ready, no changes needed

---

### Phase 2: Core Brain & Tools ✅
**What Was Built**:

#### 1. Resume Parser (`tools/resume_parser.py`)
- Hybrid: Regex + LLM (gemma2:2b)
- Extracts: Skills, Experience, Education, Projects, Soft Skills, Profile Type
- **Auto-detects** resume on startup from `resumes/` folder
- Processing time: ~2-3 minutes per resume

#### 2. Job Search (`tools/job_search.py`)
- **3-Layer Architecture**:
  1. **JobSpy**: LinkedIn, Indeed, Glassdoor, Google
  2. **Reddit**: r/remotejobs, r/forhire, +10 more
  3. **Hybrid Site-Search**: 500+ domains via DuckDuckGo `site:` queries
- **Sources**: `tools/job_lists.py` (categorized: Startups, Internships, etc.)
- **Site-Search**: `tools/site_search.py` (DDGS + BeautifulSoup fallback)
- Results saved as CSV in `jobs/` folder

#### 3. Job Matching (`tools/job_matcher.py`)
- Semantic scoring using embeddings
- Weighted by: Skills, Location, Seniority, Domain

#### 4. File Operations (`tools/file_ops.py`)
- Read, Write, Edit, List Directory, Create Folder
- All tools have independent `execute()` methods

**Key Files**:
- `tools/resume_parser.py`
- `tools/job_search.py`
- `tools/site_search.py`
- `tools/job_lists.py`
- `tools/job_matcher.py`
- `tools/file_ops.py`

**Status**: ✅ Functional, needs fault-tolerance improvements

---

### Phase 3: Email Drafting & Professional UI ✅
**What Was Built**:

#### 1. Email Drafter (`tools/email_drafter.py`)
- LLM-generated personalized emails
- Input: Job + Resume
- Output: EmailDraft (subject, body, recipient)
- Auto-saves to `emails/` folder
- **Opt-in only** (requires explicit keywords: "draft", "write", "compose")

#### 2. CLI Interface (`scripts/cli_chat.py`)
- ASCII job cards with match percentages
- Intent detection (search vs email vs chat)
- Ollama auto-start (20s timeout)
- Log suppression (clean terminal output)
- Ctrl+C cancellation support

**Key Files**:
- `tools/email_drafter.py`
- `scripts/cli_chat.py`

**Status**: ✅ Working, needs error handling improvements

---

### Phase 4: Intelligence & Advanced Features ✅
**What Was Built**:

#### 1. Auto-Resume System
- On CLI startup: Auto-detects PDF in `resumes/`
- Uses existing `load_resume()` + `ResumeParserTool.execute()`
- Stores in `session_context["resume"]`

#### 2. Advanced Filtering
- **Location**: Permissive (excludes only region-locked jobs)
- **Salary**: LPA extraction with benefit-of-doubt for "Not specified"
- **Type**: Strict for internships (must have "intern" in title)
- Applied **post-search** in `JobSearchTool.run_all()`

#### 3. Conversation Memory
- `session_context` tracks:
  - `last_search_query`
  - `matched` (jobs)
  - `conversation_history` (last 10 interactions)
- Smart recovery: "I remember searching for X, let me search again"

**Status**: ✅ Working, memory could be persistent (currently session-only)

---

## 🏗️ CURRENT ARCHITECTURE

### Project Structure
```
job-agent-production/
├── agent/
│   └── chat_agent.py          # Dual-LLM orchestrator
├── tools/
│   ├── resume_parser.py       # LLM-enhanced parsing
│   ├── job_search.py          # Hybrid meta-searcher
│   ├── site_search.py         # DDGS site: queries
│   ├── job_lists.py           # 500+ domain lists
│   ├── job_matcher.py         # Semantic ranking
│   ├── email_drafter.py       # Cold email generator
│   └── file_ops.py            # File manipulation
├── scripts/
│   └── cli_chat.py            # Terminal interface
├── models.py                  # Pydantic schemas
├── tests/
│   ├── test_all_phases.py     # Automated tests
│   └── test_4.md              # Test specifications
├── resumes/                   # User resumes (auto-detected)
├── jobs/                      # CSV search results
├── emails/                    # Email drafts
├── jan_roadmap.md             # Detailed implementation log
├── current_status.md          # Technical status report
└── credentials_setup.env      # API credentials
```

### Key Design Patterns
1. **Independent Tools**: Each tool in `tools/` has standalone `execute()` method
2. **Dual-LLM**: Separate models for structured (JSON) vs conversational tasks
3. **Fail-Safe**: Try/catch blocks around each search source
4. **Zero-Cost**: Uses local Ollama, free APIs (JobSpy, DuckDuckGo, Reddit)

---

## 🎯 YOUR OBJECTIVES

### 1. DEEP CODE ANALYSIS (Priority: CRITICAL)
**Before making ANY changes**:

#### Step 1: Audit Current State
- [ ] Read ALL files in `tools/`, `agent/`, `scripts/`
- [ ] Check for:
  - Unhandled exceptions
  - Missing try/catch blocks
  - Non-independent functions (tight coupling)
  - Resource leaks (open files, sockets)
  - Race conditions in async code
- [ ] Document findings in `AUDIT.md`

#### Step 2: Identify Failure Points
- [ ] Map all external dependencies (Ollama, Reddit API, DuckDuckGo)
- [ ] Test what happens if each fails
- [ ] Ensure **graceful degradation** (if Reddit fails, JobSpy continues)

#### Step 3: Verify Independence
- [ ] Each tool should work standalone
- [ ] Running `tool.execute()` should not require global state
- [ ] Tools should not depend on each other (except models)

---

### 2. PRODUCTION HARDENING (Priority: HIGH)

#### 2.1 Error Handling & Fault Tolerance
**Goal**: If one component fails, others continue

**Required Changes**:
```python
# BAD (current state in some places)
jobs = JobSearchTool().run_all(query)  # Crashes if fails

# GOOD (production-grade)
try:
    jobs = JobSearchTool().run_all(query)
except Exception as e:
    logger.error(f"Search failed: {e}")
    jobs = []  # Graceful fallback
    # Optionally: Try backup search method
```

**Apply to**:
- All tool calls in `scripts/cli_chat.py`
- All source integrations in `tools/job_search.py`
- All LLM calls (Ollama might be down)

#### 2.2 Resource Management
**Fix socket warnings** (currently appearing in output):
```python
# Current issue: Unclosed socket in EmailDraftTool
# Fix: Properly close LLM connections

from contextlib import closing

with closing(ChatOllama(...)) as llm:
    response = llm.invoke(prompt)
```

#### 2.3 Retry Logic
**For flaky external APIs** (Reddit, DuckDuckGo):
```python
def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### 2.4 Timeout Protection
**Prevent infinite hangs**:
```python
import asyncio

# For job search
async def search_with_timeout(query, timeout=90):
    try:
        return await asyncio.wait_for(
            JobSearchTool().run_all(query),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.warning("Search timed out")
        return []
```

---

### 3. MODULARITY & INDEPENDENCE (Priority: HIGH)

#### 3.1 Extract Configuration
**Create** `config.py`:
```python
class Config:
    OLLAMA_BASE_URL = "http://localhost:11434"
    TOOL_LLM_MODEL = "gemma2:2b"
    CHAT_LLM_MODEL = "qwen2.5:3b"
    SEARCH_TIMEOUT = 90
    RESUME_MIN_LENGTH = 100
    MAX_JOBS_TO_MATCH = 20
```

**Benefits**:
- Easy to change settings
- No magic numbers in code
- Enables testing with different configs

#### 3.2 Dependency Injection
**Make tools testable without side effects**:
```python
# Current (tightly coupled)
class JobSearchTool:
    def __init__(self):
        self.reddit = praw.Reddit(...)  # Hardcoded

# Better (injectable)
class JobSearchTool:
    def __init__(self, reddit_client=None):
        self.reddit = reddit_client or self._default_reddit()
    
    def _default_reddit(self):
        return praw.Reddit(...)
```

**Enables**:
- Unit testing with mock clients
- Easy swapping of implementations

#### 3.3 Tool Registry Pattern
**For easy integration of new tools**:
```python
# tools/registry.py
class ToolRegistry:
    _tools = {}
    
    @classmethod
    def register(cls, name):
        def decorator(tool_class):
            cls._tools[name] = tool_class
            return tool_class
        return decorator
    
    @classmethod
    def get(cls, name):
        return cls._tools.get(name)

# Usage
@ToolRegistry.register("search_jobs")
class JobSearchTool:
    ...

# In agent
tool = ToolRegistry.get("search_jobs")()
```

---

### 4. ENHANCED FEATURES (Priority: MEDIUM)

#### 4.1 Persistent Memory
**Current**: Memory lost on CLI exit  
**Improvement**: Save to local SQLite

```python
# tools/memory.py
import sqlite3

class PersistentMemory:
    def __init__(self, db_path="data/memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def save_search(self, query, results_count):
        self.conn.execute(
            "INSERT INTO searches (query, count, timestamp) VALUES (?, ?, ?)",
            (query, results_count, datetime.now())
        )
        self.conn.commit()
```

#### 4.2 Better Logging
**Current**: Basic print statements  
**Improvement**: Structured logging

```python
# Use structlog (already imported in some files)
import structlog

logger = structlog.get_logger(__name__)

# Rich context
logger.info("search_started", query=query, sources=["JobSpy", "Reddit"])
logger.error("search_failed", error=str(e), source="JobSpy")
```

#### 4.3 Health Checks
**Monitor system health**:
```python
# scripts/health_check.py
def check_system_health():
    checks = {
        "ollama": check_ollama_running(),
        "resume_folder": Path("resumes").exists(),
        "credentials": check_env_vars()
    }
    return all(checks.values()), checks
```

---

## 🚫 CRITICAL CONSTRAINTS

### What NOT to Change
1. **Zero-Cost Principle**: Must remain completely free
   - No paid APIs (keep JobSpy, DuckDuckGo, local Ollama)
   - No cloud services requiring credit cards
2. **Local-First**: Core functionality works offline
   - Resume parsing (uses local Ollama)
   - Job matching (local embeddings)
3. **Models**: Keep existing Pydantic schemas unless absolutely necessary
4. **File Structure**: Don't reorganize folders without strong reason

### What TO Change
1. **Error Handling**: Add comprehensive try/except blocks
2. **Resource Management**: Fix socket leaks, close connections
3. **Logging**: Structured logging instead of print()
4. **Testing**: Add unit tests for each tool
5. **Documentation**: Inline docstrings for all functions

---

## 📝 IMPLEMENTATION GUIDELINES

### Step-by-Step Approach

#### Phase 5.1: Audit & Fix (Week 1)
1. Create `AUDIT.md` with findings
2. Fix all resource leaks (unclosed sockets)
3. Add try/except to all external calls
4. Test each tool independently

#### Phase 5.2: Modularity (Week 2)
1. Extract `config.py`
2. Implement dependency injection in tools
3. Create tool registry
4. Add unit tests

#### Phase 5.3: Enhanced Features (Week 3)
1. Persistent memory (SQLite)
2. Structured logging (structlog)
3. Health check endpoint
4. Performance monitoring

### Testing Strategy
**For each change**:
1. Write test first (TDD)
2. Make minimal change
3. Run `tests/test_all_phases.py`
4. Ensure backward compatibility

### Git Workflow
```bash
# Before starting
git checkout -b phase5-production-hardening

# Commit frequently
git commit -m "Add error handling to JobSearchTool"

# Test before pushing
python tests/test_all_phases.py
```

---

## 🎓 KNOWLEDGE TRANSFER

### Key Gotchas
1. **Async/Await**: `JobSearchTool.run_all()` is async, must be awaited
2. **Ollama Startup**: Takes 10-20s on first run, handle gracefully
3. **Reddit API**: Requires valid credentials, fails with 401 if invalid
4. **LLM Parsing**: gemma2:2b sometimes returns markdown ```json, strip it
5. **PDF Parsing**: pdfplumber throws FontBBox warnings, suppressed in CLI

### Performance Notes
- Resume parsing: 2-3 minutes (LLM overhead)
- Job search: 30-90 seconds (network I/O)
- Email drafting: 10-20 seconds (LLM generation)

### Free Tier Limits
- **Ollama**: Unlimited (local)
- **JobSpy**: No official limits
- **DuckDuckGo**: Rate limits after ~50 queries/minute
- **Reddit**: 60 requests/minute (free tier)

---

## 📚 REFERENCE DOCUMENTATION

### Essential Reading
1. `jan_roadmap.md`: Detailed implementation history
2. `current_status.md`: Technical architecture overview
3. `tests/test_4.md`: Complete test specifications
4. `models.py`: All data structures

### External Dependencies
- **Pydantic**: https://docs.pydantic.dev/
- **LangChain**: https://python.langchain.com/docs/
- **Ollama**: https://ollama.ai/library
- **JobSpy**: https://github.com/cullenwatson/JobSpy

---

## 🎯 SUCCESS CRITERIA

Your work is complete when:
- [ ] All 40 tests in `test_4.md` pass
- [ ] No unclosed resource warnings
- [ ] Each tool can be imported and used standalone
- [ ] If any external API fails, system continues with degraded functionality
- [ ] New `AUDIT.md` documents all findings and fixes
- [ ] Code coverage > 80% (use pytest-cov)
- [ ] Average search time < 60 seconds
- [ ] Zero-cost operation maintained

---

## 🚨 URGENT ISSUES TO FIX

Based on last run:
1. **Socket Leak**: `EmailDraftTool` not closing Ollama connection properly
2. **No Global Error Handler**: CLI crashes on unexpected errors
3. **Memory**: Lost on exit, should persist to disk
4. **Logging**: Too much noise from dependencies

---

## 💡 FINAL NOTES

**Philosophy**: This project is about making job searching accessible and free. Maintain that spirit while making it rock-solid.

**Communication**: If you make breaking changes, document them clearly. Future developers/users depend on this.

**Testing**: Always test with a real resume before committing. Use `resumes/` folder with a sample PDF.

**Good luck! The foundation is solid. Make it unbreakable. 🚀**
