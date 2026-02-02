import pytest
import sys
import os
import json
import argparse

# Usage: python scripts/run_suite.py [--production]

class ResultsCollector:
    def __init__(self):
        self.results = {}

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            test_name = report.nodeid.split("::")[-1]
            self.results[test_name] = "pass" if report.passed else "fail"

def run_suite():
    parser = argparse.ArgumentParser(description="Run Job Agent Test Suite")
    parser.add_argument("--production", action="store_true", help="Run production tests only")
    args = parser.parse_args()

    # Move up one level if running from scripts/ to ensure root is cwd
    if os.getcwd().endswith("scripts"):
        os.chdir("..")
        print(f"Changed CWD to: {os.getcwd()}")
    
    sys.path.insert(0, os.getcwd())

    collector = ResultsCollector()
    
    # Select tests
    if args.production:
        target = ["tests/test_production.py", "-v"]
    else:
        target = ["tests/", "-v"]

    # Run pytest
    ret = pytest.main(target, plugins=[collector])

    # Save Results
    output_dir = "tests"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "test_results.json")
    
    with open(output_path, "w") as f:
        json.dump(collector.results, f, indent=2)
    
    print(f"\nTest execution finished. Exit code: {ret}")
    print(f"Results saved to {output_path}")
    sys.exit(ret)

if __name__ == "__main__":
    run_suite()
