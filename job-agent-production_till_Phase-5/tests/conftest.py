import pytest
import json
import time

# Store results
results = []

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    
    if rep.when == "call":
        results.append({
            "name": item.name,
            "status": "PASS" if rep.passed else "FAIL",
            "duration": rep.duration,
            "error": str(rep.longrepr) if rep.failed else None
        })

def pytest_sessionfinish(session, exitstatus):
    """Write results to JSON at end of session."""
    with open("test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total": len(results),
                "passed": len([r for r in results if r["status"] == "PASS"]),
                "failed": len([r for r in results if r["status"] == "FAIL"])
            },
            "results": results
        }, f, indent=2)
