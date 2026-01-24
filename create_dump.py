
import os

files_to_dump = [
    "README.md", "SETUP.md", "AI_CONTINUATION_PROMPT.md", "BEFOREAI.md", "HANDOVER_AND_ROADMAP.md",
    "models.py", "config.py",
    "scripts/cli_chat.py",
    "cloud/COLAB_DEPLOY_OCR.py",
    "tools/job_search.py",
    "tools/resume_parser.py",
    "tools/email_drafter.py",
    "tools/direct_scrapers.py",
    "tools/freelance_scrapers.py",
    "tools/extended_job_scrapers.py",
    "tools/more_scrapers.py",
    "tools/lead_scraper.py"
]

output_file = "PROJECT_CONTEXT_DUMP.txt"

with open(output_file, "w", encoding="utf-8") as out:
    out.write("# CYNO PROJECT FULL DUMP\n")
    out.write("# This file contains all source code and documentation.\n\n")
    
    for fname in files_to_dump:
        if os.path.exists(fname):
            out.write(f"\n\n{'='*50}\n# FILE: {fname}\n{'='*50}\n\n")
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"# Error reading file: {e}\n")
        else:
            out.write(f"\n\n# FILE NOT FOUND: {fname}\n\n")

print(f"Dump created at {output_file}")
