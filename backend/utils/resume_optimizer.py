from backend.utils.recommendation_engine import build_recommendation_report


def _extract_bullets(text):
    """Extract bullet-style resume lines while preserving the original wording."""
    bullets = []

    if not text:
        return bullets

    for raw_line in str(text).splitlines():
        line = raw_line.strip()
        if not line:
            continue

        # Support common resume bullet markers.
        if line.startswith(("•", "●", "▪", "‣", "-", "–", "—", "*")):
            line = line.lstrip("•●▪‣-*–— ").strip()

        if len(line) >= 20:
            bullets.append(line)

    return bullets


def _normalize(text):
    return " ".join(str(text or "").lower().split())


def _tokens(text):
    """Small, conservative tokenization for evidence matching."""
    import re

    stopwords = {
        "the", "and", "for", "with", "using", "use", "to", "of", "in",
        "on", "a", "an", "as", "by", "from", "into", "through", "this",
        "that", "work", "working", "developed", "develop", "built",
        "build", "implemented", "created", "improved", "improving",
        "project", "projects", "role", "team", "teams",
    }

    words = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.-]{1,}", _normalize(text))
    return {word for word in words if word not in stopwords and len(word) > 2}


def _contains_any(text, phrases):
    text = _normalize(text)
    return any(_normalize(p) in text for p in phrases)


def _responsibility_terms(responsibility):
    """
    Extract meaningful terms from a JD responsibility and add conservative
    domain phrases. This helps avoid selecting a random Python/SQL bullet.
    """
    text = _normalize(responsibility)
    terms = _tokens(text)

    # Common responsibility concepts.
    groups = {
        "analysis": {
            "analyze", "analysis", "analytics", "insights", "data",
            "customer", "product", "kpi", "metrics", "trend",
        },
        "visualization": {
            "dashboard", "dashboards", "visualization", "visualize",
            "report", "reports", "tableau", "powerbi", "excel",
        },
        "collaboration": {
            "collaborate", "collaboration", "cross-functional",
            "stakeholder", "stakeholders", "requirements", "product",
            "manager", "managers",
        },
        "modeling": {
            "model", "models", "machine", "learning", "deep",
            "training", "train", "evaluate", "accuracy",
        },
        "data_preparation": {
            "dataset", "datasets", "preprocess", "preprocessing",
            "clean", "cleaning", "prepare", "preparation",
        },
        "deployment": {
            "deploy", "deployment", "production", "pipeline",
            "pipelines", "maintain", "maintaining",
        },
    }

    for group_terms in groups.values():
        if terms.intersection(group_terms):
            terms.update(group_terms.intersection(terms))

    return terms


def _bullet_score(bullet, responsibility, matched_skills):
    """
    Score whether a resume bullet is actually useful for a JD responsibility.

    Responsibility evidence is weighted more heavily than a generic skill
    mention, so unrelated Python/SQL bullets are not preferred.
    """
    bullet_text = _normalize(bullet)
    bullet_terms = _tokens(bullet)
    req_terms = _responsibility_terms(responsibility)

    overlap = bullet_terms.intersection(req_terms)
    score = len(overlap) * 3.0

    # Exact responsibility phrases are strong evidence.
    req_text = _normalize(responsibility)
    if req_text and len(req_text) > 10:
        important_phrase = req_text.replace("analyze", "").strip()
        if important_phrase and important_phrase in bullet_text:
            score += 5.0

    # Matched JD skills provide supporting evidence, but not enough by
    # themselves to make an unrelated bullet a good candidate.
    skill_hits = 0
    for skill in matched_skills:
        skill_norm = _normalize(skill)
        if skill_norm and skill_norm in bullet_text:
            skill_hits += 1

    score += min(skill_hits, 3) * 0.75

    # Prefer action-oriented bullets.
    action_words = {
        "developed", "built", "created", "implemented", "designed",
        "analyzed", "improved", "optimized", "collaborated", "delivered",
        "automated", "evaluated", "integrated", "deployed", "led",
    }
    if bullet_terms.intersection(action_words):
        score += 0.5

    return score


def _suggestion_for_bullet(bullet, responsibility):
    """
    Make an evidence-preserving suggestion.

    The optimizer does not invent metrics, tools, achievements, or outcomes.
    It only makes the connection to the JD requirement more explicit when
    the existing bullet already provides supporting evidence.
    """
    original = bullet.strip().rstrip(".")
    req = _normalize(responsibility)

    # Product/data-analysis style responsibilities.
    if _contains_any(req, ["analyze product and customer data", "data analysis"]):
        if _contains_any(original, ["data", "analysis", "analytics", "customer", "product"]):
            return (
                f"{original} — make the data-analysis, product, or customer "
                f"insight contribution explicit."
            )

    if _contains_any(req, ["build dashboards and reports", "dashboard", "reports"]):
        if _contains_any(original, ["dashboard", "visual", "report", "excel", "tableau"]):
            return (
                f"{original} — make the dashboard/reporting output and "
                f"visualization contribution explicit."
            )

    if _contains_any(req, ["cross-functional", "work with cross-functional teams", "stakeholder"]):
        if _contains_any(original, ["collaborat", "team", "requirement", "stakeholder"]):
            return (
                f"{original} — make the cross-functional collaboration and "
                f"requirements contribution explicit."
            )

    if _contains_any(req, ["present insights", "product managers", "present"]):
        if _contains_any(original, ["present", "insight", "manager", "stakeholder", "communicat"]):
            return (
                f"{original} — make the communication or presentation of "
                f"insights to stakeholders explicit."
            )

    # ML/data-science responsibilities.
    if _contains_any(req, ["develop", "train", "ml model", "machine learning"]):
        if _contains_any(original, ["model", "machine learning", "training", "trained"]):
            return (
                f"{original} — make the model-development or training "
                f"contribution explicit."
            )

    if _contains_any(req, ["preprocess", "prepare", "datasets", "data preparation"]):
        if _contains_any(original, ["data", "dataset", "preprocess", "clean"]):
            return (
                f"{original} — make the dataset preparation or preprocessing "
                f"work explicit."
            )

    if _contains_any(req, ["evaluate", "accuracy", "performance"]):
        if _contains_any(original, ["evaluate", "accuracy", "performance", "benchmark"]):
            return (
                f"{original} — make the model evaluation, performance, or "
                f"improvement impact explicit."
            )

    if _contains_any(req, ["deploy", "production", "deployment"]):
        if _contains_any(original, ["deploy", "production", "pipeline"]):
            return (
                f"{original} — make the production deployment or pipeline "
                f"contribution explicit."
            )

    # Generic fallback: preserve the bullet and explain what to clarify.
    return (
        f"{original} — explicitly connect this existing work to "
        f"the target requirement."
    )


def _build_bullet_optimizations(candidate_profile, match_result):
    sections = (candidate_profile or {}).get("sections", {})
    match_result = match_result or {}

    skills_result = match_result.get("skills", {})
    responsibilities_result = match_result.get("responsibilities", {})

    matched_skills = list(skills_result.get("matched_skills", []))
    missing_responsibilities = list(
        responsibilities_result.get("missing_responsibilities", [])
    )

    # Only use actual experience/project evidence from the candidate profile.
    resume_bullets = []
    for section_name in ("experience", "projects"):
        for bullet in _extract_bullets(sections.get(section_name, "")):
            resume_bullets.append((section_name, bullet))

    if not resume_bullets:
        return []

    items = []
    used_bullets = set()

    # First priority: missing JD responsibilities.
    for responsibility in missing_responsibilities:
        ranked = sorted(
            (
                (_bullet_score(bullet, responsibility, matched_skills), section, bullet)
                for section, bullet in resume_bullets
                if bullet not in used_bullets
            ),
            key=lambda x: x[0],
            reverse=True,
        )

        if not ranked or ranked[0][0] < 2.0:
            # No sufficiently relevant evidence. Do not force an unrelated
            # bullet into the recommendation.
            continue

        score, section, bullet = ranked[0]
        used_bullets.add(bullet)

        suggested = _suggestion_for_bullet(bullet, responsibility)

        # Avoid presenting an unchanged sentence as a "suggestion".
        if suggested == bullet:
            suggested = (
                f"{bullet.rstrip('.')} — make the relevance to "
                f"'{responsibility}' explicit."
            )

        items.append(
            {
                "section": section.title(),
                "requirement": responsibility,
                "current": bullet,
                "suggested": suggested,
                "why": (
                    "This keeps the existing evidence but makes its relevance "
                    "to the target responsibility clearer for a recruiter or ATS."
                ),
            }
        )

    # Second priority: strong matched-skill evidence only when it is useful
    # for a JD responsibility and we still have room.
    if len(items) < 6:
        all_responsibilities = list(
            responsibilities_result.get("matched_responsibilities", [])
        )

        for responsibility in all_responsibilities:
            ranked = sorted(
                (
                    (_bullet_score(bullet, responsibility, matched_skills), section, bullet)
                    for section, bullet in resume_bullets
                    if bullet not in used_bullets
                ),
                key=lambda x: x[0],
                reverse=True,
            )

            if not ranked or ranked[0][0] < 4.0:
                continue

            score, section, bullet = ranked[0]
            used_bullets.add(bullet)

            suggested = _suggestion_for_bullet(bullet, responsibility)

            items.append(
                {
                    "section": section.title(),
                    "requirement": responsibility,
                    "current": bullet,
                    "suggested": suggested,
                    "why": (
                        "This bullet already contains relevant evidence; the "
                        "suggestion makes that evidence easier to recognize "
                        "against the job requirement."
                    ),
                }
            )

            if len(items) >= 6:
                break

    return items[:6]


def build_resume_optimization_report(
    match_result=None,
    recommendation=None,
    candidate_profile=None,
    job_profile=None,
    **kwargs,
):
    """
    Build the resume optimization layer without changing the existing
    recommendation engine output.
    """
    if recommendation is not None:
        report = dict(recommendation)
    else:
        report = build_recommendation_report(
            match_result=match_result,
            job_profile=job_profile,
            candidate_profile=candidate_profile,
            **kwargs,
        )

    report["bullet_optimizations"] = (
        _build_bullet_optimizations(candidate_profile, match_result)
        if candidate_profile is not None
        else []
    )

    return report
