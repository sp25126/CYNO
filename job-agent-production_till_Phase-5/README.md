# Job Agent Production

This repository contains the **Job Agent** project, which provides tools for parsing resumes, validating job postings, managing sessions, and drafting email applications.

## Project Structure

```
job-agent-production/
├── models.py               # Pydantic schemas for core data models
├── requirements.txt        # Project dependencies
├── .gitignore              # Standard Python ignores
├── README.md               # Project overview (this file)
├── tests/                  # Unit tests
│   ├── __init__.py
│   ├── test_resume_parsing.py
│   ├── test_job_validation.py
│   ├── test_session_persistence.py
│   ├── test_email_draft_validation.py
│   └── test_results.json   # Generated after tests run
└── acceptance_tests/       # Acceptance tests and sample data
    ├── __init__.py
    ├── resume_samples/
    │   ├── resume_1.txt
    │   ├── resume_2.txt
    │   └── ... (additional samples)
    └── expected_output/
        ├── resume_1_expected.json
        └── ... (matching expected outputs)
```

## Getting Started

1. Set up the environment:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # Windows (Git Bash):
   source venv/Scripts/activate
   # Windows (Command Prompt):
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. Run unit tests:
   ```bash
   pytest tests/
   ```
3. Add your own resume samples in `acceptance_tests/resume_samples/` and define the expected JSON output in `acceptance_tests/expected_output/`.

## Contributing

Feel free to open issues or submit pull requests for improvements, additional tests, or new features.
