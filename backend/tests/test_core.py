import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.jd_parser import build_job_profile
from utils.matcher import calculate_experience_match, calculate_skill_match, calculate_overall_match, calculate_responsibility_match, calculate_education_match

JD = "Product Data Analyst — Job Description We are looking for a Product Data Analyst to analyze product performance and generate actionable insights."

def test_short_product_data_analyst_jd():
    p=build_job_profile(JD)
    assert p["job_title"]=="Product Data Analyst"
    assert p["required_skills"]==["data analysis","data visualization","excel","python","sql","statistics","tableau"]
    assert p["experience"]=="1+ years of experience in data analysis"
    assert p["experience"] == "1+ years of experience in data analysis"
    assert p["education"] == "Bachelor's degree in Computer Science, Engineering, or a related field"
    assert p["responsibilities"] == [
        "Analyze product and customer data",
        "Build dashboards and reports",
        "Work with cross-functional teams",
        "Present insights to product managers",
    ]

def test_month_experience():
    x=calculate_experience_match("Software Development Intern | Doodhvale May'25 - July'25", "1+ years of experience in data analysis")
    assert x["candidate_years"]==0.25
    assert x["required_years"]==1.0
    assert x["has_experience"] is True
    assert x["score"]==25.0

def test_full_matching_flow():
    profile={"sections":{"experience":"Software Development Intern | Doodhvale May'25 - July'25","education":"2026 4YRS B.S IIT Kharagpur 6.18 / 10","skills":"Programming Languages: Python | SQL\nLibraries: Pandas | NumPy\nTools: MS Office","projects":"Built dashboards and reports with dynamic visualization"}}
    p=build_job_profile(JD)
    skills=["Python","SQL","Pandas","NumPy","MS Office"]
    sm=calculate_skill_match(skills,p["required_skills"],"\n".join(profile["sections"].values()))
    em=calculate_experience_match(profile["sections"]["experience"],p["experience"])
    ed=calculate_education_match(profile["sections"]["education"],p["education"])
    rm=calculate_responsibility_match(profile,p["responsibilities"])
    overall=calculate_overall_match(sm,em,ed,rm)
    assert sm["score"] > 0
    assert em["candidate_years"]==0.25
    assert overall["score"] >= 0
    assert ed["matched"] is True
    assert "Build dashboards and reports" in rm["matched_responsibilities"]
