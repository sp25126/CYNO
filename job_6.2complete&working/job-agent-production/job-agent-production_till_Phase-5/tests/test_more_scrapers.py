import logging
import sys
from tools.more_scrapers import MoreScrapers

# Setup logging
logging.basicConfig(level=logging.INFO)

def test_new_scrapers():
    print("Testing Jobspresso...")
    ms = MoreScrapers()
    jobs = ms.scrape_jobspresso("python", limit=5)
    print(f"Jobspresso: {len(jobs)} jobs")
    for j in jobs:
        print(f" - {j.title} @ {j.company}")

    print("\nTesting Remote.io...")
    jobs = ms.scrape_remote_io("python", limit=5)
    print(f"Remote.io: {len(jobs)} jobs")
    for j in jobs:
        print(f" - {j.title} @ {j.company}")

    print("\nTesting DailyRemote...")
    jobs = ms.scrape_dailyremote("python", limit=5)
    print(f"DailyRemote: {len(jobs)} jobs")
    for j in jobs:
        print(f" - {j.title} @ {j.company}")

if __name__ == "__main__":
    test_new_scrapers()
