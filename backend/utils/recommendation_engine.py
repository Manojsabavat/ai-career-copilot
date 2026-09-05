def _classification(score):
    if score >= 80:
        return "Strong match"
    if score >= 65:
        return "Good match"
    if score >= 50:
        return "Moderate match"
    return "Weak match"

def build_recommendation_report(
    skill_match,
    experience_match,
    education_match,
    responsibility_match,
    overall_match=None,
    job_profile=None,
    **kwargs,
):
    overall_match = overall_match or kwargs.get("match_result") or {}
    job_profile = job_profile or kwargs.get("job_profile") or {}

    score = float(overall_match.get("score", 0))

    missing_skills = list(
        skill_match.get("missing_skills", [])
    )

    missing_responsibilities = list(
        responsibility_match.get("missing_responsibilities", [])
    )

    candidate_years = float(
        experience_match.get("candidate_years", 0)
    )

    required_years = float(
        experience_match.get("required_years", 0)
    )

    gap = max(
        0.0,
        required_years - candidate_years
    )

    recommendations = []
    improvements = []
    projects = []

    # ---------------------------------------------------------
    # SKILL-BASED RECOMMENDATIONS
    # ---------------------------------------------------------

    if "excel" in missing_skills:
        recommendations.append(
            "Strengthen Excel through PivotTables, XLOOKUP, data cleaning and dashboard creation."
        )

        improvements.append(
            "Add practical Excel experience using PivotTables, XLOOKUP, data cleaning and dashboard creation."
        )

    if "tableau" in missing_skills:
        recommendations.append(
            "Learn Tableau and build a dashboard project demonstrating practical data visualization."
        )

        improvements.append(
            "Add a Tableau dashboard project demonstrating practical data visualization."
        )

    for skill in missing_skills:
        if skill not in {"excel", "tableau"}:
            recommendations.append(
                f"Develop practical experience with {skill} and add measurable resume evidence."
            )

    # ---------------------------------------------------------
    # RESPONSIBILITY-BASED RECOMMENDATIONS
    # ---------------------------------------------------------

    if missing_responsibilities:
        clean_responsibilities = [
            str(x).strip().rstrip(".")
            for x in missing_responsibilities
        ]

        for responsibility in clean_responsibilities:
            recommendations.append(
                f"Strengthen evidence for the responsibility: '{responsibility}'."
            )

        improvements.extend(
            [
                f"Add direct resume evidence demonstrating: {x}."
                for x in clean_responsibilities
            ]
        )

    # ---------------------------------------------------------
    # EXPERIENCE GAP
    # ---------------------------------------------------------

    if gap > 0:
        recommendations.append(
            f"Gain approximately {gap:.2f} more year(s) of relevant experience through internships, projects or freelance work."
        )

    # ---------------------------------------------------------
    # JD-SPECIFIC PROJECT IDEAS
    # ---------------------------------------------------------

    if missing_skills or missing_responsibilities:
        job_title = str(
            job_profile.get("job_title", "")
        ).lower()

        if (
            "machine learning" in job_title
            or "ml engineer" in job_title
        ):
            projects.append(
                "Build an end-to-end machine learning project using Python, Pandas, NumPy and Scikit-learn, covering data preprocessing, model training, evaluation and deployment."
            )

        elif (
            "data analyst" in job_title
            or "business analyst" in job_title
        ):
            projects.append(
                "Build an end-to-end data analytics project using Python, SQL, Excel/Tableau, KPI tracking and stakeholder-focused insights."
            )

        elif "data scientist" in job_title:
            projects.append(
                "Build an end-to-end data science project using Python, Pandas, NumPy and Scikit-learn, covering data preparation, modeling, evaluation and actionable insights."
            )

        else:
            projects.append(
                "Build an end-to-end project that demonstrates the missing technical skills and responsibilities identified from the job description."
            )

    # ---------------------------------------------------------
    # KEYWORD SUGGESTIONS
    # ---------------------------------------------------------

    keyword_suggestions = sorted(
        set(
            skill_match.get("matched_skills", [])
            + missing_skills
        )
    )

    # ---------------------------------------------------------
    # PRIORITY ACTIONS
    # ---------------------------------------------------------

    priority_actions = []

    for skill in missing_skills:
        priority_actions.append(
            {
                "priority": "high",
                "type": "missing_skill",
                "item": skill,
                "action": f"Develop and demonstrate practical {skill} experience.",
            }
        )

    for item in missing_responsibilities:
        clean_item = str(item).strip().rstrip(".")

        priority_actions.append(
            {
                "priority": "high",
                "type": "missing_responsibility",
                "item": clean_item,
                "action": f"Add direct resume evidence for: {clean_item}.",
            }
        )

    if gap > 0:
        priority_actions.append(
            {
                "priority": "medium",
                "type": "experience_gap",
                "item": "Relevant experience",
                "action": f"Build approximately {gap:.2f} additional year(s) of relevant experience.",
            }
        )

    # ---------------------------------------------------------
    # CLASSIFICATION
    # ---------------------------------------------------------

    classification = _classification(score)

    summary = {
        "Strong match": (
            "Strong match. Your profile aligns well with the role."
        ),
        "Good match": (
            "Good match. You satisfy many important requirements, with a few gaps to address."
        ),
        "Moderate match": (
            "Moderate match. Your profile has relevant strengths, but several requirements need improvement."
        ),
        "Weak match": (
            "Weak match. Your profile currently has several important gaps for this role."
        ),
    }[classification]

    # ---------------------------------------------------------
    # FINAL REPORT
    # ---------------------------------------------------------

    return {
        "summary": summary,
        "classification": classification,
        "overall_score": round(score, 2),
        "recommendations": recommendations,
        "missing_skills": missing_skills,
        "missing_responsibilities": missing_responsibilities,
        "experience_gap_years": round(gap, 2),
        "resume_improvements": improvements,
        "keyword_suggestions": keyword_suggestions,
        "project_ideas": projects,
        "priority_actions": priority_actions,
        "skill_analysis": skill_match,
        "experience_analysis": experience_match,
        "education_analysis": education_match,
        "responsibility_analysis": responsibility_match,
    }