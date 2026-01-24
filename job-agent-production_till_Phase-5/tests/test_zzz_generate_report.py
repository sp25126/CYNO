import json

def test_generate_report(fixture_store):
    results = {
        "test_resume_valid_parsing": fixture_store.get("resume_parsing", "failed"),
        "test_resume_invalid_years": fixture_store.get("resume_invalid_years", "failed"),
        "test_job_url_validation": fixture_store.get("job_url_validation", "failed"),
        "test_session_message_persistence": fixture_store.get("session_persistence", "failed"),
        "test_email_draft_sanitization": fixture_store.get("email_sanitization", "failed"),
    }

    with open("tests/test_results.json", "w") as f:
        json.dump(results, f, indent=4)
