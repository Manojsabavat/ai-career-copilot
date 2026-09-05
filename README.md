# AI Career Copilot

AI Career Copilot is a resume intelligence and job-match analysis web application that evaluates how well a candidate's resume aligns with a target job description.

> An evidence-based resume intelligence platform that evaluates candidate–job fit and generates actionable, JD-specific resume optimization insights.

## Project Highlights

- **Resume Intelligence:** Extracts structured candidate information from PDF resumes.
- **JD Intelligence:** Parses job descriptions into skills, experience, education, and responsibilities.
- **Explainable Matching:** Calculates separate skill, experience, education, and responsibility scores before producing an overall job-fit score.
- **Resume Optimization:** Identifies missing requirements, suggests relevant keywords and projects, and improves the visibility of existing resume evidence.
- **Evidence-Aware Suggestions:** Avoids fabricating achievements, metrics, tools, or experience when the resume lacks supporting evidence.
- **Role-Aware Recommendations:** Adapts project ideas and recommendations to different target roles.

## Features

- Resume PDF parsing and candidate-profile extraction
- Job-description parsing
- Skill, experience, education, and responsibility matching
- Weighted overall match score
- Actionable career recommendations
- JD-specific project ideas and keyword suggestions
- Evidence-preserving resume bullet optimization
- Priority actions for identified gaps
- Candidate and job requirement summaries
- Automated backend tests with pytest

## Architecture

```text
Resume PDF ──> Resume Parser ──> Candidate Profile ──┐
                                                     │
Job Description ──> JD Parser ──> Job Profile ──────┤
                                                     ▼
                                      ┌─────────────────────────┐
                                      │       Match Engine      │
                                      │ Skills / Experience     │
                                      │ Education / Duties      │
                                      │ Overall Match Score     │
                                      └────────────┬────────────┘
                                                   ▼
                                      ┌─────────────────────────┐
                                      │ Recommendation Engine   │
                                      │ Next Steps / Keywords   │
                                      │ Projects / Priorities   │
                                      └────────────┬────────────┘
                                                   ▼
                                      ┌─────────────────────────┐
                                      │ Resume Optimization     │
                                      │ Evidence-aware bullets  │
                                      └────────────┬────────────┘
                                                   ▼
                                      FastAPI REST Backend
                                                   │
                                                   ▼
                                      HTML / CSS / JavaScript
```

## Project Structure

```text
ai-career-copilot/
├── backend/
│   ├── main.py
│   ├── utils/
│   │   ├── jd_parser.py
│   │   ├── matcher.py
│   │   ├── profile_extractor.py
│   │   ├── recommendation_engine.py
│   │   ├── resume_optimizer.py
│   │   └── resume_parser.py
│   └── tests/
├── frontend/
│   ├── index.html
│   ├── app.js
│   ├── style.css
│   └── resume_optimization.css
└── README.md
```

## Tech Stack

**Backend:** Python, FastAPI, Pydantic, PyMuPDF, pytest

**Frontend:** HTML5, CSS3, Vanilla JavaScript

**Core intelligence:** section-aware parsing, skill normalization, evidence matching, date-range extraction, education matching, responsibility matching, rule-based recommendations, and evidence-preserving resume optimization.

## Matching Methodology

| Component | Weight |
|---|---:|
| Skills | 50% |
| Responsibilities | 20% |
| Experience | 20% |
| Education | 10% |

The application exposes both the overall score and individual component scores so users can understand the reasons behind a match result.

## Resume Optimization

The optimization layer provides:

1. **Resume Improvements** — concrete gaps to address.
2. **Suggested Keywords** — relevant JD terminology.
3. **JD-Aligned Bullet Suggestions** — makes existing evidence clearer without inventing achievements.
4. **Project Ideas** — recommendations tailored to the target role.
5. **Priority Actions** — specific actions for missing requirements.

The bullet optimizer is intentionally evidence-preserving. It does not invent metrics, tools, achievements, responsibilities, or experience. If suitable evidence is not present, it explicitly reports that instead of fabricating a resume bullet.

## API Endpoints

- `GET /` — basic API information
- `GET /health` — backend health check
- `POST /upload-resume` — upload and parse a resume PDF
- `POST /analyze-job` — parse a job description
- `POST /match` — calculate matching results
- `POST /analyze` — run the complete analysis pipeline

## Local Setup

### 1. Activate the virtual environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Run the backend

From the project root:

```powershell
python -m uvicorn backend.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

### 3. Run the frontend

Open a second terminal:

```powershell
cd frontend
python -m http.server 5500 --bind 127.0.0.1
```

Frontend:

```text
http://127.0.0.1:5500
```

## Testing

From the project root with the virtual environment activated:

```powershell
python -m pytest -q
```

Verified result:

```text
3 passed
```

## End-to-End Workflow

```text
Upload Resume
      ↓
Paste Job Description
      ↓
Parse Resume + JD
      ↓
Extract Candidate + Job Profiles
      ↓
Calculate Match Components
      ↓
Generate Overall Score
      ↓
Generate Recommendations
      ↓
Optimize Resume Evidence
      ↓
Display Results
```

## Validation

The application has been tested with multiple job categories, including:

- Product Data Analyst
- Machine Learning Engineer
- Data Scientist
- Data Analyst

The validation confirmed that recommendations and project ideas adapt to the target role and that unsupported resume evidence is not fabricated.

## Design Principle

The core principle is **evidence-based career guidance**.

The application explains:

- what the candidate already matches,
- what is missing,
- why the gap matters,
- what can be improved,
- which keywords are relevant,
- which projects could address skill gaps,
- and where existing resume evidence can be made clearer.

## Current Status

**MVP complete and validated.**

- Backend tests: passing
- Frontend/backend integration: working
- Resume parsing: working
- JD parsing: working
- Matching pipeline: working
- Recommendation engine: working
- Resume optimization: working
- Multi-JD validation: completed

## Future Enhancements

- LLM-assisted semantic matching
- Resume version generation
- ATS compatibility scoring
- Job-application tracking
- Multiple resume comparison
- Authentication and user profiles
- Persistent application history
- Cloud deployment
