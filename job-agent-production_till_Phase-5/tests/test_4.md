# Comprehensive Test Specification - Phases 1-4
# Test File: test_4
# Last Updated: January 7, 2026

---

## PHASE 1: FOUNDATION & MODELS

### Test 1.1: Resume Model Validation
**Function**: `Resume.__init__()` (models.py)
**Input**:
```python
Resume(
    parsed_skills=["Python", "JavaScript"],
    education_level="BACHELORS",
    years_exp=3,
    location="San Francisco",
    keywords=["AI", "ML"],
    profile_type="WEB_DEVELOPER",
    raw_text="sample text"
)
```
**Expected Output**: Valid Resume object created without errors
**Pass Criteria**: No ValidationError raised

---

### Test 1.2: Job Model URL Validation
**Function**: `Job.__init__()` (models.py)
**Input**:
```python
Job(
    title="AI Engineer",
    company="TechCorp",
    location="Remote",
    job_url="https://example.com/job",
    apply_url="https://example.com/apply",
    description="AI/ML role",
    source="Test"
)
```
**Expected Output**: Valid Job object with properly validated URLs
**Pass Criteria**: `job_url` and `apply_url` are HttpUrl types

---

### Test 1.3: Resume Parser - Basic Extraction
**Function**: `ResumeParserTool.execute()` (tools/resume_parser.py)
**Input**: 
```
"John Doe
Senior AI Engineer with 5 years of experience
Skills: Python, TensorFlow, AWS, Docker
Education: M.S. Computer Science
Location: San Francisco, CA"
```
**Expected Output**:
```python
Resume(
    parsed_skills=["Python", "TensorFlow", "AWS", "Docker"],
    years_exp=5,
    education_level="MASTERS",
    location="San Francisco, CA"
)
```
**Pass Criteria**: 
- At least 3 skills extracted correctly
- Years of experience = 5
- Education level = "MASTERS"

---

### Test 1.4: Resume Parser - Profile Type Detection
**Function**: `ResumeParserTool._llm_extract_detailed()` (tools/resume_parser.py)
**Input**: Resume text mentioning "AI", "Machine Learning", "TensorFlow"
**Expected Output**: `profile_type = "AI_ML_ENGINEER"`
**Pass Criteria**: Correct profile type assigned based on skills

---

### Test 1.5: Resume Parser - Minimum Length Validation
**Function**: `ResumeParserTool.execute()` (tools/resume_parser.py)
**Input**: "Short text" (38 characters)
**Expected Output**: ValueError raised
**Pass Criteria**: Error message contains "too short (min 100 chars required)"

---

## PHASE 2: JOB SEARCH & MATCHING

### Test 2.1: JobSpy Integration
**Function**: `JobSearchTool.run_all()` (tools/job_search.py)
**Input**: query="Python developer", limit=5
**Expected Output**: 
- List of Job objects (1-5 items)
- Each job has valid title, company, job_url
- Source contains "JobSpy"
**Pass Criteria**: At least 1 job returned from JobSpy

---

### Test 2.2: Reddit Search
**Function**: `JobSearchTool.search_reddit()` (tools/job_search.py)
**Input**: query="remote developer"
**Expected Output**: List of dict with keys: 'title', 'company', 'url', 'description', 'source'
**Pass Criteria**: 
- Returns list (may be empty if Reddit API fails gracefully)
- Source = "Reddit (r/subredditname)"

---

### Test 2.3: Hybrid Site Search (500+ Domains)
**Function**: `SiteSearchTool.search_domains()` (tools/site_search.py)
**Input**: 
```python
query="AI engineer"
domains=["weworkremotely.com", "remoteok.com"]
limit_per_domain=2
```
**Expected Output**: List of Job objects with `source="Direct (domain.com)"`
**Pass Criteria**: Jobs contain URLs from specified domains

---

### Test 2.4: Job Matching - Basic Scoring
**Function**: `JobMatchingTool.execute()` (tools/job_matcher.py)
**Input**: 
- Resume with skills=["Python", "TensorFlow"]
- Jobs: ["Python Developer", "Java Developer"]
**Expected Output**: 
- Python Developer has higher score than Java Developer
- Ranked list with tuples (job, score, reason)
**Pass Criteria**: Score difference > 0.1

---

### Test 2.5: CSV Export Format
**Function**: `JobSearchTool._save_to_csv()` (tools/job_search.py)
**Input**: List of 3 Job objects, query="test"
**Expected Output**: 
- CSV file created in jobs/ folder
- Columns: Company, Title, Location, Salary, Posted, Source, URL
**Pass Criteria**: File exists, has 4 rows (header + 3 data)

---

### Test 2.6: File Operations - Write
**Function**: `FileWriteTool.execute()` (tools/file_ops.py)
**Input**: 
```python
{
    "filepath": "test_output.txt",
    "content": "Hello World",
    "overwrite": True
}
```
**Expected Output**: File created with content "Hello World"
**Pass Criteria**: File exists and contains exact content

---

### Test 2.7: File Operations - List Directory
**Function**: `ListDirTool.execute()` (tools/file_ops.py)
**Input**: {"path": "./jobs"}
**Expected Output**: List of filenames in jobs/ folder
**Pass Criteria**: Returns list type, contains .csv files if any exist

---

## PHASE 3: EMAIL DRAFTING & UI

### Test 3.1: Email Draft Generation
**Function**: `EmailDraftTool.execute()` (tools/email_drafter.py)
**Input**: 
- Job: AI Engineer at TechCorp
- Resume: 3 years Python experience
**Expected Output**: 
```python
EmailDraft(
    subject="Application for AI Engineer at TechCorp",
    body="Dear Hiring Manager...",
    recipient="careers@techcorp.com"
)
```
**Pass Criteria**: 
- Subject mentions job title and company
- Body length > 200 characters
- Recipient is valid email format

---

### Test 3.2: Email Draft - File Saving
**Function**: `EmailDraftTool.execute()` (tools/email_drafter.py)
**Input**: Valid job and resume
**Expected Output**: 
- EmailDraft object returned
- .txt file created in emails/ folder
**Pass Criteria**: File exists, contains subject and body

---

### Test 3.3: CLI Job Card Rendering
**Function**: `render_job_card()` (scripts/cli_chat.py)
**Input**: 
```python
render_job_card(
    index=1,
    job=Job(...),
    score=0.85,
    reason="Strong Python match"
)
```
**Expected Output**: ASCII-formatted card with:
- Job title
- Company & location
- Match percentage (85%)
- Reason text
**Pass Criteria**: Output contains "85% MATCH" and reason text

---

### Test 3.4: Ollama Service Check
**Function**: `check_ollama_running()` (scripts/cli_chat.py)
**Input**: None
**Expected Output**: 
- True if Ollama running on localhost:11434
- False otherwise
**Pass Criteria**: No exceptions raised, returns boolean

---

### Test 3.5: Intent Detection - Email vs Search
**Function**: `HRChatAgent.detect_intent()` (agent/chat_agent.py)
**Input**: 
- "draft email for job #1"
- "find AI jobs"
**Expected Output**: 
- First: intent.primary = "draft_email"
- Second: intent.primary = "job_search"
**Pass Criteria**: Correct intent detected for both

---

## PHASE 4: INTELLIGENCE & FILTERING

### Test 4.1: Auto-Resume Detection
**Function**: `HRChatCLI._auto_load_resume()` (scripts/cli_chat.py)
**Input**: PDF file exists in resumes/ folder
**Expected Output**: 
- Resume automatically parsed
- session_context["resume"] populated
- Console message: "Resume loaded! Profile: {type}"
**Pass Criteria**: Resume object in session_context

---

### Test 4.2: Auto-Resume - Missing File
**Function**: `HRChatCLI._auto_load_resume()` (scripts/cli_chat.py)
**Input**: Empty resumes/ folder
**Expected Output**: Console message: "No resume found in 'resumes/'"
**Pass Criteria**: No crash, graceful message displayed

---

### Test 4.3: Location Filter - Permissive
**Function**: `JobSearchTool.run_all()` filtering logic (tools/job_search.py)
**Input**: 
- query="AI jobs india"
- Jobs: [India, Remote, "UK only"]
**Expected Output**: India and Remote jobs included, "UK only" excluded
**Pass Criteria**: 2 jobs in result (India + Remote)

---

### Test 4.4: Internship Filter - Strict
**Function**: `JobSearchTool.run_all()` filtering logic (tools/job_search.py)
**Input**: 
- query="AI intern"
- Jobs: ["AI Intern", "AI Engineer"]
**Expected Output**: Only "AI Intern" included
**Pass Criteria**: 1 job in result

---

### Test 4.5: Salary Filter - LPA
**Function**: `JobSearchTool.run_all()` filtering logic (tools/job_search.py)
**Input**: 
- query="jobs with 5lpa"
- Jobs: ["3 LPA", "7 LPA", "Not specified"]
**Expected Output**: "7 LPA" and "Not specified" included, "3 LPA" excluded
**Pass Criteria**: 2 jobs in result

---

### Test 4.6: Conversation Memory - Storage
**Function**: `HRChatCLI.run()` (scripts/cli_chat.py)
**Input**: 
1. User searches for "AI jobs"
2. Results returned and stored
**Expected Output**: 
- session_context["matched"] contains jobs
- session_context["last_search_query"] = "AI jobs"
- conversation_history has entry with type="search"
**Pass Criteria**: All 3 memory fields populated

---

### Test 4.7: Conversation Memory - Recovery
**Function**: Email drafting with memory fallback (scripts/cli_chat.py)
**Input**: 
1. User searches for "Python jobs"
2. matched jobs cleared (simulated)
3. User says "draft email for job #1"
**Expected Output**: 
- Message: "I remember searching for 'Python jobs' but results aren't available"
- Triggers new search
**Pass Criteria**: Recovery message displayed, no crash

---

### Test 4.8: Hybrid Search - Source Diversity
**Function**: `JobSearchTool.run_all()` (tools/job_search.py)
**Input**: query="developer remote"
**Expected Output**: 
- Jobs from at least 2 different source types:
  - JobSpy (LinkedIn/Indeed/etc)
  - Reddit
  - Direct (Site-Search)
**Pass Criteria**: At least 2 distinct source types in results

---

### Test 4.9: Deduplication
**Function**: `JobSearchTool.run_all()` (tools/job_search.py)
**Input**: Multiple sources return same job URL
**Expected Output**: Only 1 job with that URL in final results
**Pass Criteria**: No duplicate job_url values in returned list

---

### Test 4.10: Enhanced Resume Fields
**Function**: `ResumeParserTool.execute()` (tools/resume_parser.py)
**Input**: Resume mentioning "Leadership" and "Built chatbot project"
**Expected Output**: 
```python
Resume(
    soft_skills=["Leadership"],
    projects=["Built chatbot project"],
    ...
)
```
**Pass Criteria**: 
- soft_skills list not empty
- projects list not empty

---

## INTEGRATION TESTS

### Integration Test 1: End-to-End Job Search Flow
**Scenario**: User opens CLI, searches, views results, drafts email
**Steps**:
1. Start CLI
2. Resume auto-loads
3. User: "find AI jobs in India"
4. Jobs displayed as cards
5. User: "draft email for job #1"
6. Email saved to emails/

**Expected Behavior**: All steps complete without errors
**Pass Criteria**: 
- Resume loaded message appears
- At least 1 job found
- Job card displayed
- Email file created

---

### Integration Test 2: Filter Application
**Scenario**: User searches with specific filters
**Steps**:
1. User: "find AI internships in India with 5lpa"
2. System applies all 3 filters:
   - Location: India
   - Type: Internship
   - Salary: >= 5 LPA

**Expected Behavior**: 
- Pre-filter: 50 jobs
- Post-filter: 5 jobs (all match criteria)
**Pass Criteria**: All returned jobs have "intern" in title

---

### Integration Test 3: Memory Persistence
**Scenario**: User searches, chats, then drafts email later
**Steps**:
1. User: "find Python jobs"
2. User: "tell me about Python" (general chat)
3. User: "draft email for job #1"

**Expected Behavior**: 
- Step 2 doesn't clear job results
- Step 3 successfully uses stored jobs
**Pass Criteria**: Email drafted successfully in step 3

---

## PERFORMANCE TESTS

### Performance Test 1: Resume Parsing Speed
**Function**: `ResumeParserTool.execute()`
**Input**: 3-page resume (3000 characters)
**Expected Time**: < 180 seconds (3 minutes)
**Pass Criteria**: Completes within time limit

---

### Performance Test 2: Job Search Speed
**Function**: `JobSearchTool.run_all()`
**Input**: query="developer", limit=20
**Expected Time**: < 90 seconds
**Pass Criteria**: Returns results within time limit

---

### Performance Test 3: Concurrent Source Handling
**Function**: `JobSearchTool.run_all()`
**Input**: All 3 sources (JobSpy, Reddit, Site-Search)
**Expected Behavior**: Sources queried asynchronously
**Pass Criteria**: Total time < sum of individual source times

---

## ERROR HANDLING TESTS

### Error Test 1: Invalid Resume Format
**Function**: `ResumeParserTool.execute()`
**Input**: Binary data or corrupted text
**Expected Output**: ValueError with descriptive message
**Pass Criteria**: No crash, clear error message

---

### Error Test 2: Reddit API Failure
**Function**: `JobSearchTool.search_reddit()`
**Input**: Invalid credentials or API down
**Expected Output**: 
- Returns empty list
- Logs warning
- Does NOT crash entire search
**Pass Criteria**: run_all() continues and returns jobs from other sources

---

### Error Test 3: Network Timeout
**Function**: `JobSearchTool.run_all()`
**Input**: Simulated network failure
**Expected Output**: Graceful degradation, partial results
**Pass Criteria**: Returns jobs from available sources, doesn't hang forever

---

### Error Test 4: Missing Resume on Email Draft
**Function**: Email drafting in CLI
**Input**: User requests email without searching first
**Expected Output**: Message: "I need to search for jobs first"
**Pass Criteria**: No crash, helpful error message

---

## SUMMARY

**Total Tests**: 40
- Phase 1: 5 tests
- Phase 2: 7 tests  
- Phase 3: 5 tests
- Phase 4: 10 tests
- Integration: 3 tests
- Performance: 3 tests
- Error Handling: 4 tests
- Additional: 3 tests

**All tests should PASS for production readiness**
