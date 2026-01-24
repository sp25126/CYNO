import pytest
from tools.resume_parser import ResumeParserTool

# 10 Samples (strings)
SAMPLE_RESUME_1 = """
John Doe
Software Engineer
Location: San Francisco
Experience: 5 years in Python and Django.
Skills: Python, Django, SQL, AWS.
Education: B.S. in Computer Science.
"""

SAMPLE_RESUME_2 = """
Jane Smith
Senior Developer
Location: London, UK
10+ years of building scalable systems. Expert in Java and Spring Boot.
Also knows React and Node.js.
Masters in Engineering.
"""

SAMPLE_RESUME_3 = """
Bob Jones
Frontend Dev
Location: Remote
3 years exp. 
Focus on React, TypeScript, CSS.
B.Tech graduate.
"""

SAMPLE_RESUME_4 = """
Alice Wonderland
Data Scientist
Location: New York
PhD in Mathematics.
7 years experience in Machine Learning, TensorFlow, PyTorch.
Python expert.
"""

SAMPLE_RESUME_5 = """
Charlie Brown
DevOps Engineer
Location: Berlin
Experience: 4 years.
Skills: Docker, Kubernetes, AWS, Terraform, Go.
B.Sc in IT.
"""

SAMPLE_RESUME_6 = """
David Lee
Full Stack
Location: Toronto
6 years experience.
Ruby on Rails, React, PostgreSQL.
Masters degree.
"""

SAMPLE_RESUME_7 = """
Eva Green
Backend Dev
Location: Austin, TX (Remote)
8 years exp.
C#, .NET, Azure, SQL Server.
Bachelor of Engineering.
"""

SAMPLE_RESUME_8 = """
Frank White
Junior Dev
Location: Bangalore
1 year experience.
Java, SQL, HTML.
B.Tech in CS.
Summary: Eager to learn and grow in a fast-paced environment. Looking for junior backend roles.
"""

SAMPLE_RESUME_9 = """
Grace Hopper
Lead Engineer
Location: Washington DC
20 years experience.
COBOL (just kidding), Python, Go, Rust.
PhD in CS.
"""

SAMPLE_RESUME_10 = """
Harry Potter
Wizard / Dev
Location: London
2 years experience in Python magic.
Flask, SQLAlchemy.
Diploma in Wizardry.
"""

SHORT_RESUME = "Too short"

@pytest.fixture
def parser():
    return ResumeParserTool()

def test_short_input_raises_error(parser):
    with pytest.raises(ValueError) as exc:
        parser.execute("Too short")
    assert "too short" in str(exc.value)

def test_resume_1(parser):
    res = parser.execute(SAMPLE_RESUME_1)
    assert "Python" in res.parsed_skills
    assert res.years_exp == 5
    assert res.location == "San Francisco"
    assert res.education_level == "BACHELORS"

def test_resume_2(parser):
    res = parser.execute(SAMPLE_RESUME_2)
    assert "Java" in res.parsed_skills
    assert res.years_exp >= 10
    assert "London" in res.location
    assert res.education_level == "MASTERS"

def test_resume_3(parser):
    res = parser.execute(SAMPLE_RESUME_3)
    assert "React" in res.parsed_skills
    assert res.years_exp == 3
    assert res.location == "Remote"
    assert res.education_level == "BACHELORS"

def test_resume_4(parser):
    res = parser.execute(SAMPLE_RESUME_4)
    assert "Machine Learning" in res.parsed_skills # Multi-word check
    assert res.years_exp == 7
    assert res.education_level == "PHD"

def test_resume_5(parser):
    res = parser.execute(SAMPLE_RESUME_5)
    assert "Docker" in res.parsed_skills
    assert res.years_exp == 4
    assert res.location == "Berlin"

def test_resume_6(parser):
    res = parser.execute(SAMPLE_RESUME_6)
    assert "Ruby" in res.parsed_skills
    assert res.years_exp == 6
    assert res.education_level == "MASTERS"

def test_resume_7(parser):
    res = parser.execute(SAMPLE_RESUME_7)
    assert "C#" in res.parsed_skills
    assert res.location == "Remote" or "Austin" in res.location
    assert res.years_exp == 8

def test_resume_8(parser):
    res = parser.execute(SAMPLE_RESUME_8)
    assert "Java" in res.parsed_skills
    assert res.years_exp == 1
    assert res.location == "Bangalore"

def test_resume_9(parser):
    res = parser.execute(SAMPLE_RESUME_9)
    assert "Python" in res.parsed_skills
    assert res.years_exp == 20
    assert res.education_level == "PHD"

def test_resume_10(parser):
    res = parser.execute(SAMPLE_RESUME_10)
    assert "Python" in res.parsed_skills
    assert res.years_exp == 2
    assert "London" in res.location
    # High School / Diploma mapping
    assert res.education_level == "HIGH_SCHOOL"
