# 🔍 Phase 5 Audit Report

**Date**: 2026-01-07
**Auditor**: Antigravity

## 🛑 Critical Issues (Must Fix)

### 1. Resource Leaks (Socket Warnings)
- **File**: `tools/email_drafter.py`
- **Issue**: `ChatOllama` is instantiated in `__init__` and persists. While standard HTTP requests are stateless, the `urllib3`/`requests` pools underlying LangChain can result in "Unclosed socket" warnings if not managed or if the script exits abruptly.
- **Fix**: Use `contextlib.closing` or ensure proper scope management for LLM instances.

### 2. Tight Coupling
- **File**: `agent/chat_agent.py`
- **Issue**: Tools are hardcoded in `_register_tools`:
  ```python
  return { "parse_resume": ResumeParserTool(), ... }
  ```
  This makes it impossible to unit test the agent with mock tools.
- **Fix**: Inject tools via constructor or use a Registry pattern.

### 3. Mixed Responsibility
- **File**: `scripts/cli_chat.py`
- **Issue**: The CLI implements its own logic for `job_search` and `draft_email` intents, bypassing `agent.process_message`. This leads to code duplication (e.g., checking for existing resume) and makes the Agent less autonomous.
- **Fix**: While CLI needs UI control (ASCII cards), the *execution* logic should ideally be centralized. However, for Phase 5, we will prioritize stability first.

### 4. Hardcoded Configuration
- **Several Files**: `http://localhost:11434`, `gemma2:2b`, timeouts (`90`), and headers are scattered.
- **Fix**: Centralize in `config.py`.

## ⚠️ Stability Risks

### 1. External API Flakiness
- **File**: `tools/job_search.py`
- **Issue**: `search_reddit` and `jobspy` rely on external services.
- **Mitigation**: The current `try...except` blocks are good, but we need **Retries** with backoff for network glitches.

### 2. Missing Timeouts
- **File**: `tools/job_search.py`
- **Issue**: `JobSearchTool.run_all` awaits results but has no global timeout. If one scraper hangs, the user waits forever.
- **Fix**: Wrap `run_all` in `asyncio.wait_for`.

## 🔄 Architecture & Modularity

- **Dependency Injection**: Tools should assume their dependencies (like `praw.Reddit`) are passed in, allowing for easier testing.
- **Tool Registry**: A decorator-based registry will make adding future tools (e.g., "Web Browser") cleaner.

## 📝 Plan of Action

1.  **Refactor Config**: Move all magic strings/numbers to `config.py`.
2.  **Harden Tools**: Apply `with closing(...)` pattern for LLMs and add timeouts.
3.  **Decouple**: Implement `ToolRegistry` and Injection.
4.  **Persist**: Add SQLite memory.
