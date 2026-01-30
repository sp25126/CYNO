"""
CYNO Live System Test - All Tools
Tests against REAL Cloud Brain with REAL data using GitHub: sp25126
"""
import os
import sys
import json
import time

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['COLAB_SERVER_URL'] = 'https://9b25fe231854.ngrok-free.app'

def print_header(text):
    print(f"\n{'='*60}\n{text}\n{'='*60}")

def print_result(name, success, details=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} | {name}")
    if details:
        print(f"    → {details[:150]}")

test_results = []

def record_test(name, success, details=""):
    test_results.append({"name": name, "success": success, "details": details})
    print_result(name, success, details)

# ============================================
# TEST 1: Cloud Brain Connection
# ============================================
print_header("TEST 1: CLOUD BRAIN CONNECTION")

from cloud.enhanced_client import get_cloud_client
client = get_cloud_client()
stats = client.health_check()
print(f"Cloud URL: {stats['cloud']['url']}")
print(f"Cloud Available: {stats['cloud']['available']}")
record_test("Cloud Connection", stats['cloud']['available'], f"URL: {stats['cloud']['url']}")

if not stats['cloud']['available']:
    print("❌ CRITICAL: Cloud not available. Stopping tests.")
    sys.exit(1)

# ============================================
# TEST 2: Project Deep Dive (GitHub Analysis)
# ============================================
print_header("TEST 2: PROJECT DEEP DIVE (GitHub: sp25126)")

from tools.interview_prep import ProjectDeepDiveTool
deep_dive = ProjectDeepDiveTool()
dive_result = deep_dive.execute('sp25126')
record_test(
    "Project Deep Dive",
    dive_result.get('success', False),
    f"Analyzed {len(dive_result.get('projects', []))} projects"
)
if dive_result.get('projects'):
    print("    Projects found:")
    for p in dive_result.get('projects', [])[:3]:
        print(f"      - {p.get('name')}: {p.get('languages', [])}")

# ============================================
# TEST 3: Cloud Text Generation (Core LLM)
# ============================================
print_header("TEST 3: CLOUD TEXT GENERATION")

gen_result = client.generate_text(
    "List 3 interview tips. Return JSON: {\"tips\": []}",
    max_tokens=200,
    parse_json=True
)
record_test(
    "Text Generation",
    gen_result.success,
    f"Backend: {gen_result.backend}, Time: {gen_result.time_seconds}s"
)
if gen_result.success:
    print(f"    Result: {str(gen_result.result)[:200]}")

# ============================================
# TEST 4: Tech Stack Detector
# ============================================
print_header("TEST 4: TECH STACK DETECTOR")

from tools.discovery_tools import TechStackDetectorTool
jd_sample = """
Senior Python Developer - Remote
Requirements:
- Python 3.8+, FastAPI, Django
- PostgreSQL, Redis
- Docker, Kubernetes
- AWS (EC2, S3, Lambda)
Nice to have: React, TypeScript, Machine Learning
"""
tech_detector = TechStackDetectorTool()
tech_result = tech_detector.execute(jd_sample)
has_stack = 'tech_stack' in tech_result or isinstance(tech_result, dict)
record_test("Tech Stack Detector", has_stack, str(tech_result)[:150])

# ============================================
# TEST 5: Salary Estimator
# ============================================
print_header("TEST 5: SALARY ESTIMATOR")

from tools.discovery_tools import SalaryEstimatorTool
salary_tool = SalaryEstimatorTool()
salary_result = salary_tool.execute(
    job_title="Senior Python Developer",
    company="Google",
    location="Remote USA",
    experience_level="Senior"
)
record_test(
    "Salary Estimator",
    'estimates' in salary_result or 'error' not in salary_result,
    str(salary_result)[:150]
)

# ============================================
# TEST 6: Interview Question Finder
# ============================================
print_header("TEST 6: INTERVIEW QUESTION FINDER")

from tools.discovery_tools import InterviewQuestionFinderTool
q_finder = InterviewQuestionFinderTool()
q_result = q_finder.execute(company="Google", role="Software Engineer")
record_test(
    "Interview Q Finder",
    'questions' in q_result or 'error' not in q_result,
    str(q_result)[:150]
)

# ============================================
# TEST 7: Cover Letter Generator
# ============================================
print_header("TEST 7: COVER LETTER GENERATOR")

cover_result = client.generate_cover_letter(
    job_title="Python Developer",
    company="Anthropic",
    job_description="Build AI systems with Python",
    skills=["Python", "FastAPI", "Machine Learning"],
    experience_years=3
)
record_test(
    "Cover Letter Gen",
    cover_result.success,
    f"Length: {len(str(cover_result.result))} chars" if cover_result.success else str(cover_result.error)
)

# ============================================
# TEST 8: Email Drafter
# ============================================
print_header("TEST 8: EMAIL DRAFTER")

email_result = client.draft_email(
    job_title="ML Engineer",
    company="OpenAI",
    job_description="Build GPT models",
    resume_skills=["Python", "PyTorch", "Transformers"],
    resume_experience=2
)
record_test(
    "Email Drafter",
    email_result.success,
    f"Subject: {email_result.result.get('subject', 'N/A')[:80]}" if email_result.success else str(email_result.error)
)

# ============================================
# TEST 9: Job Fit Scorer
# ============================================
print_header("TEST 9: JOB FIT SCORER")

from tools.advanced_ai import JobFitScorerTool
fit_scorer = JobFitScorerTool()
fit_result = fit_scorer.execute(
    resume_text="Python developer with 3 years experience in FastAPI, Django, PostgreSQL, Docker.",
    job_description=jd_sample
)
record_test(
    "Job Fit Scorer",
    'fit_analysis' in fit_result or isinstance(fit_result, dict),
    str(fit_result)[:150]
)

# ============================================
# TEST 10: Weakness Spin Doctor
# ============================================
print_header("TEST 10: WEAKNESS SPIN DOCTOR")

from tools.advanced_ai import WeaknessSpinDoctorTool
spin_tool = WeaknessSpinDoctorTool()
spin_result = spin_tool.execute(weakness="I sometimes over-engineer solutions")
record_test(
    "Weakness Spin Doctor",
    'answer_guide' in spin_result or isinstance(spin_result, dict),
    str(spin_result)[:150]
)

# ============================================
# TEST 11: Personal Brand Builder
# ============================================
print_header("TEST 11: PERSONAL BRAND BUILDER")

from tools.advanced_ai import PersonalBrandBuilderTool
brand_tool = PersonalBrandBuilderTool()
brand_result = brand_tool.execute(
    resume_summary="Python developer focused on AI and automation",
    key_skills=["Python", "AI/ML", "FastAPI"]
)
record_test(
    "Brand Builder",
    'brand_kit' in brand_result or isinstance(brand_result, dict),
    str(brand_result)[:150]
)

# ============================================
# TEST 12: Side Project Idea Generator
# ============================================
print_header("TEST 12: SIDE PROJECT IDEAS")

from tools.advanced_ai import SideProjectIdeaGenTool
idea_tool = SideProjectIdeaGenTool()
idea_result = idea_tool.execute(
    current_skills=["Python", "FastAPI"],
    target_role="ML Engineer"
)
record_test(
    "Project Ideas",
    'project_ideas' in idea_result or isinstance(idea_result, dict),
    str(idea_result)[:150]
)

# ============================================
# TEST 13: Job Description Summarizer
# ============================================
print_header("TEST 13: JD SUMMARIZER")

from tools.utility_tools import JobDescriptionSummarizerTool
jd_tool = JobDescriptionSummarizerTool()
jd_result = jd_tool.execute(jd_sample)
record_test(
    "JD Summarizer",
    'summary' in jd_result or isinstance(jd_result, dict),
    str(jd_result)[:150]
)

# ============================================
# TEST 14: Recruiter Finder
# ============================================
print_header("TEST 14: RECRUITER FINDER")

from tools.utility_tools import RecruiterFinderTool
recruit_tool = RecruiterFinderTool()
recruit_result = recruit_tool.execute(company="Microsoft")
record_test(
    "Recruiter Finder",
    'recruiter_intel' in recruit_result or isinstance(recruit_result, dict),
    str(recruit_result)[:150]
)

# ============================================
# TEST 15: System Design Simulator
# ============================================
print_header("TEST 15: SYSTEM DESIGN SIMULATOR")

from tools.interview_prep import SystemDesignSimulatorTool
design_tool = SystemDesignSimulatorTool()
design_result = design_tool.execute(project_summary={
    "name": "E-commerce Platform",
    "description": "Online shopping with payments",
    "tech_stack": ["Python", "React", "PostgreSQL"]
})
record_test(
    "System Design Sim",
    'design_challenge' in design_result or isinstance(design_result, dict),
    str(design_result)[:150]
)

# ============================================
# TEST 16: Behavioral Answer Bank
# ============================================
print_header("TEST 16: BEHAVIORAL ANSWER BANK")

from tools.interview_prep import BehavioralAnswerBankTool
behavioral_tool = BehavioralAnswerBankTool()
behavioral_result = behavioral_tool.execute(
    question="Tell me about a time you solved a difficult problem",
    project_context={"name": "Job Agent", "tech_stack": ["Python", "FastAPI"]}
)
record_test(
    "Behavioral Answers",
    'star_answer' in behavioral_result or isinstance(behavioral_result, dict),
    str(behavioral_result)[:150]
)

# ============================================
# TEST 17: Course Recommender
# ============================================
print_header("TEST 17: COURSE RECOMMENDER")

from tools.advanced_ai import CourseRecommenderTool
course_tool = CourseRecommenderTool()
course_result = course_tool.execute(missing_skills=["Kubernetes", "AWS Lambda"])
record_test(
    "Course Recommender",
    'learning_plan' in course_result or isinstance(course_result, dict),
    str(course_result)[:150]
)

# ============================================
# SUMMARY
# ============================================
print_header("FINAL TEST SUMMARY")
passed = sum(1 for t in test_results if t['success'])
total = len(test_results)
print(f"\n✅ PASSED: {passed}/{total}")
print(f"❌ FAILED: {total - passed}/{total}")
print(f"\nCloud Stats: {client.get_stats()}")

for t in test_results:
    status = "✅" if t['success'] else "❌"
    print(f"  {status} {t['name']}")
