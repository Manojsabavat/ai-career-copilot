import traceback

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.utils.resume_parser import extract_text_from_pdf
from backend.utils.profile_extractor import build_candidate_profile
from backend.utils.jd_parser import build_job_profile
from backend.utils.matcher import (
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
    calculate_responsibility_match,
    calculate_overall_match,
)
from backend.utils.recommendation_engine import build_recommendation_report
from backend.utils.resume_optimizer import build_resume_optimization_report

class MatchRequest(BaseModel):
    candidate_skills: list[str]
    required_skills: list[str]

class JobDescriptionRequest(BaseModel):
    text: str

app = FastAPI(
    title="AI Career Copilot API",
    description="Backend API for AI Career Copilot",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Career Copilot API is running", "status": "success", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

def _validate_pdf(file):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported for now.")

def _extract_candidate_skills(candidate_profile):
    text = candidate_profile.get("sections", {}).get("skills", "")
    skills = []
    for line in text.splitlines():
        if ":" not in line:
            continue
        _, values = line.split(":", 1)
        for skill in values.split("|"):
            skill = skill.strip()
            if skill:
                skills.append(skill)
    return list(dict.fromkeys(skills))

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    _validate_pdf(file)
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded resume is empty.")
    text = extract_text_from_pdf(data)
    if not text:
        raise HTTPException(status_code=400, detail="Could not extract text from this PDF.")
    profile = build_candidate_profile(text)
    return {"filename": file.filename, "content_type": file.content_type,
            "text_length": len(text), "candidate_profile": profile}

@app.post("/analyze-job")
def analyze_job(request: JobDescriptionRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")
    return {"job_profile": build_job_profile(request.text)}

@app.post("/match")
def match_resume_to_job(request: MatchRequest):
    result = calculate_skill_match(request.candidate_skills, request.required_skills, "")
    return {"match_result": result}

@app.post("/analyze")
async def analyze_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    try:
        if not job_description.strip():
            raise HTTPException(status_code=400, detail="Job description cannot be empty.")
        _validate_pdf(file)
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Uploaded resume is empty.")
        resume_text = extract_text_from_pdf(pdf_bytes)
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from this PDF.")

        candidate_profile = build_candidate_profile(resume_text)
        job_profile = build_job_profile(job_description)
        candidate_skills = _extract_candidate_skills(candidate_profile)
        required_skills = job_profile.get("required_skills", [])

        skill_match = calculate_skill_match(candidate_skills, required_skills, resume_text)
        sections = candidate_profile.get("sections", {})
        experience_match = calculate_experience_match(
            sections.get("experience", ""), job_profile.get("experience"), resume_text
        )
        education_match = calculate_education_match(
            sections.get("education", ""), job_profile.get("education")
        )
        responsibility_match = calculate_responsibility_match(
            candidate_profile, job_profile.get("responsibilities", [])
        )
        overall_match = calculate_overall_match(
            skill_match, experience_match, education_match, responsibility_match
        )
        recommendation = build_recommendation_report(
            skill_match=skill_match,
            experience_match=experience_match,
            education_match=education_match,
            responsibility_match=responsibility_match,
            overall_match=overall_match,
            job_profile=job_profile,
        )
        match_result = {
            "overall": overall_match,
            "skills": skill_match,
            "experience": experience_match,
            "education": education_match,
            "responsibilities": responsibility_match,
        }
        resume_optimization = build_resume_optimization_report(
            match_result=match_result,
            recommendation=recommendation,
            candidate_profile=candidate_profile,
            job_profile=job_profile,
        )
        return {
            "candidate_profile": candidate_profile,
            "job_profile": job_profile,
            "match_result": match_result,
            "recommendation": recommendation,
            "resume_optimization": resume_optimization,
        }
    except HTTPException:
        raise
    except Exception as exc:
        print("\n========== ANALYZE ERROR ==========")
        print(f"{type(exc).__name__}: {exc}")
        traceback.print_exc()
        print("===================================\n")
        raise HTTPException(status_code=500, detail=f"{type(exc).__name__}: {exc}")
