import re
from datetime import datetime


# ============================================================
# SKILL NORMALIZATION
# ============================================================

SKILL_ALIASES = {
    "postgres": "postgresql",
    "postgres sql": "postgresql",
    "ms excel": "excel",
    "microsoft excel": "excel",
    "py": "python",
    "js": "javascript",
    "ts": "typescript",
    "ml": "machine learning",
    "dl": "deep learning",
    "nlp": "natural language processing",
}


SKILL_EVIDENCE_ALIASES = {
    "excel": [
        "excel",
        "microsoft excel",
        "ms excel",
        "pivot table",
        "pivottable",
        "xlookup",
        "vlookup",
    ],
    "sql": [
        "sql",
        "mysql",
        "postgresql",
        "postgres",
        "sqlite",
        "mssql",
    ],
    "python": [
        "python",
    ],
    "statistics": [
        "statistics",
        "statistical",
        "anova",
        "probability and statistics",
    ],
    "data analysis": [
        "data analysis",
        "data analytics",
        "data analyst",
        "pandas",
        "numpy",
        "statistical analysis",
        "analyzing data",
        "analysis of data",
        "dataset",
        "datasets",
    ],
    "data visualization": [
        "data visualization",
        "data visualisation",
        "visualization",
        "visualisation",
        "dynamic visualization",
        "matplotlib",
        "plotly",
        "power bi",
        "dashboard",
        "dashboards",
    ],
    "tableau": [
        "tableau",
    ],
}


def normalize_skill(x):
    x = re.sub(r"\s+", " ", str(x or "").strip().lower())
    return SKILL_ALIASES.get(x, x)


def _contains(text, phrase):
    if not phrase:
        return False

    return bool(
        re.search(
            r"(?<!\w)" + re.escape(phrase.lower()) + r"(?!\w)",
            str(text or "").lower(),
        )
    )


def find_skill_evidence(skill, resume_text):
    normalized = normalize_skill(skill)

    aliases = SKILL_EVIDENCE_ALIASES.get(
        normalized,
        [normalized],
    )

    return [
        alias
        for alias in aliases
        if _contains(resume_text, alias)
    ]


def calculate_skill_match(
    candidate_skills,
    required_skills,
    resume_text="",
):
    candidate = {
        normalize_skill(x)
        for x in (candidate_skills or [])
        if str(x).strip()
    }

    required = []

    for x in required_skills or []:
        normalized = normalize_skill(x)

        if normalized and normalized not in required:
            required.append(normalized)

    matched = []
    missing = []
    evidence = {}

    for skill in required:
        ev = find_skill_evidence(
            skill,
            resume_text,
        )

        ok = skill in candidate or bool(ev)

        evidence[skill] = {
            "matched": ok,
            "evidence": ev,
            "source": (
                "candidate_skills_and_resume_evidence"
                if ok
                else None
            ),
        }

        if ok:
            matched.append(skill)
        else:
            missing.append(skill)

    score = (
        100.0
        if not required
        else len(matched) / len(required) * 100
    )

    return {
        "score": round(score, 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "evidence": evidence,
    }


# ============================================================
# EXPERIENCE PARSING
# ============================================================

MONTH_ALIASES = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


MONTH_PATTERN = (
    r"(?:"
    r"January|February|March|April|May|June|July|August|"
    r"September|October|November|December|"
    r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
    r")"
)


# ------------------------------------------------------------
# Month + year ranges
#
# Examples:
# May'25 - July'25
# May 2025 - July 2025
# May'25 – July'25
# May 2025 to July 2025
# May'25 - Present
# ------------------------------------------------------------

MONTH_YEAR_RANGE_PATTERN = re.compile(
    rf"""
    (?P<start_month>{MONTH_PATTERN})
    \s*['’]?\s*
    (?P<start_year>\d{{2,4}})
    \s*
    (?:-|–|—|to)
    \s*
    (?:
        (?P<end_month>{MONTH_PATTERN})
        \s*['’]?\s*
        (?P<end_year>\d{{2,4}})
        |
        (?P<end_present>Present|Current|Now)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


# ------------------------------------------------------------
# Year-only ranges
#
# Examples:
# 2022 - 2024
# 2023–2025
# 2024 to Present
# ------------------------------------------------------------

YEAR_RANGE_PATTERN = re.compile(
    r"""
    (?P<start_year>\b\d{4}\b)
    \s*
    (?:-|–|—|to)
    \s*
    (?:
        (?P<end_year>\d{4})
        |
        (?P<end_present>Present|Current|Now)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def _normalize_year(value):
    """
    Convert:
        25 -> 2025
        24 -> 2024
        2025 -> 2025
    """

    year = int(value)

    if year < 100:
        return 2000 + year

    return year


def _parse_month(month):
    if not month:
        return None

    return MONTH_ALIASES.get(
        month.strip().lower()
    )


def _current_year_month():
    now = datetime.now()

    return now.year, now.month


def _months_between(
    start_year,
    start_month,
    end_year,
    end_month,
):
    """
    Inclusive month calculation.

    Example:
        May 2025 -> July 2025

    May, June, July = 3 months

    Therefore:
        3 / 12 = 0.25 years
    """

    months = (
        (end_year - start_year) * 12
        + (end_month - start_month)
        + 1
    )

    return max(0, months)


def extract_experience_ranges(text):
    """
    Extract all recognizable experience ranges.

    Returns a list like:

    [
        {
            "start_year": 2025,
            "start_month": 5,
            "end_year": 2025,
            "end_month": 7,
            "months": 3
        }
    ]
    """

    text = str(text or "")

    ranges = []

    # --------------------------------------------------------
    # MONTH + YEAR RANGES
    # --------------------------------------------------------

    for match in MONTH_YEAR_RANGE_PATTERN.finditer(text):

        start_month = _parse_month(
            match.group("start_month")
        )

        start_year = _normalize_year(
            match.group("start_year")
        )

        if match.group("end_present"):

            end_year, end_month = _current_year_month()

        else:

            end_month = _parse_month(
                match.group("end_month")
            )

            end_year = _normalize_year(
                match.group("end_year")
            )

        if not start_month or not end_month:
            continue

        months = _months_between(
            start_year,
            start_month,
            end_year,
            end_month,
        )

        if months <= 0:
            continue

        item = {
            "start_year": start_year,
            "start_month": start_month,
            "end_year": end_year,
            "end_month": end_month,
            "months": months,
        }

        if item not in ranges:
            ranges.append(item)

    # --------------------------------------------------------
    # YEAR-ONLY RANGES
    #
    # Only process ranges that were NOT already captured as
    # month-year ranges.
    # --------------------------------------------------------

    for match in YEAR_RANGE_PATTERN.finditer(text):

        start_year = int(
            match.group("start_year")
        )

        if match.group("end_present"):

            end_year, _ = _current_year_month()

        else:

            end_year = int(
                match.group("end_year")
            )

        # Year-only experience is represented as
        # January -> December.
        months = _months_between(
            start_year,
            1,
            end_year,
            12,
        )

        if months <= 0:
            continue

        item = {
            "start_year": start_year,
            "start_month": 1,
            "end_year": end_year,
            "end_month": 12,
            "months": months,
        }

        if item not in ranges:
            ranges.append(item)

    return ranges


def extract_years_from_text(text):
    """
    Return total experience in YEARS.

    Internally calculates months for accuracy,
    but the public result is always years.

    Examples:

        May'25 - July'25
        -> 3 months
        -> 0.25 years

        2022 - 2024
        -> 36 months
        -> 3.0 years
    """

    ranges = extract_experience_ranges(text)

    if not ranges:
        return 0.0

    total_months = sum(
        item["months"]
        for item in ranges
    )

    return round(
        total_months / 12,
        2,
    )


# ============================================================
# REQUIRED EXPERIENCE PARSER
# ============================================================

def extract_required_years(text):
    """
    Extract required experience from job description.

    Supported examples:

        1+ years
        2+ years
        1 year
        2 years
        minimum 1 year
        at least 2 years
        1.5+ years
    """

    if not text:
        return 0.0

    text = str(text)

    patterns = [
        # 1+ years
        r"(\d+(?:\.\d+)?)\s*\+\s*years?",

        # 1 year / 2 years
        r"(\d+(?:\.\d+)?)\s*years?",

        # minimum 1 year
        r"(?:minimum|min\.?|at\s+least)\s+"
        r"(\d+(?:\.\d+)?)\s*years?",
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        for value in matches:

            try:
                values.append(
                    float(value)
                )
            except ValueError:
                pass

    return max(values, default=0.0)


def calculate_experience_match(
    candidate_experience,
    required_experience,
    full_resume_text="",
):
    """
    Compare candidate experience against job requirement.

    IMPORTANT:
    - Experience is calculated from actual date ranges.
    - Months are used internally.
    - Final candidate_years is always expressed in years.
    """

    required = extract_required_years(
        required_experience
    )

    source = (
        str(candidate_experience or "").strip()
        or str(full_resume_text or "")
    )

    candidate = extract_years_from_text(
        source
    )

    if required <= 0:
        score = 100.0
    else:
        score = min(
            (candidate / required) * 100,
            100,
        )

    return {
        "score": round(score, 2),
        "required_years": round(required, 2),
        "candidate_years": round(candidate, 2),
        "has_experience": candidate > 0,
    }


# ============================================================
# EDUCATION MATCHING
# ============================================================

def calculate_education_match(
    candidate_education,
    required_education,
):
    if not required_education:
        return {
            "score": 100.0,
            "matched": True,
            "required": required_education,
        }

    candidate = str(
        candidate_education or ""
    ).lower()

    required = str(
        required_education or ""
    ).lower()

    degree_ok = any(
        keyword in candidate
        for keyword in [
            "bachelor",
            "b.s",
            "b.s.",
            "btech",
            "b.tech",
            "undergraduate",
            "engineering degree",
        ]
    )

    if any(
        keyword in required
        for keyword in [
            "master",
            "m.tech",
            "mtech",
            "m.s",
            "postgraduate",
        ]
    ):
        degree_ok = any(
            keyword in candidate
            for keyword in [
                "master",
                "m.tech",
                "mtech",
                "m.s",
                "postgraduate",
            ]
        )

    elif "mba" in required:
        degree_ok = "mba" in candidate

    elif (
        "phd" in required
        or "doctorate" in required
    ):
        degree_ok = (
            "phd" in candidate
            or "doctorate" in candidate
        )

    if not degree_ok:
        return {
            "score": 0.0,
            "matched": False,
            "required": required_education,
        }

    # A technical STEM degree is considered related
    # for broad requirements such as:
    #
    # Bachelor's degree in Computer Science,
    # Engineering, or a related field.

    field_ok = True

    if (
        "computer science" in required
        or "engineering" in required
        or "related field" in required
    ):

        technical_terms = [
            "computer",
            "engineering",
            "technology",
            "science",
            "geophysics",
            "physics",
            "mathematics",
            "statistics",
            "data",
            "information",
            "electrical",
            "mechanical",
            "electronics",
            "instrumentation",
        ]

        field_ok = (
            any(
                keyword in candidate
                for keyword in technical_terms
            )
            or "b.s" in candidate
            or "bachelor" in candidate
        )

    return {
        "score": 100.0 if field_ok else 0.0,
        "matched": bool(field_ok),
        "required": required_education,
    }


# ============================================================
# RESPONSIBILITY MATCHING
# ============================================================

def _tokens(text):
    return set(
        re.findall(
            r"[a-z0-9]+(?:-[a-z0-9]+)?",
            str(text or "").lower(),
        )
    )


RESPONSIBILITY_CONCEPTS = {

    "analyze product and customer data": [
        "analyz",
        "analysis",
        "analyzing",
        "data",
        "dataset",
        "datasets",
        "customer",
    ],

    "build dashboards and reports": [
        "dashboard",
        "dashboards",
        "report",
        "reports",
        "visualization",
        "visualisation",
        "visualize",
        "visualise",
    ],

    "work with cross-functional teams": [
        "cross-functional",
        "collaborated",
        "collaboration",
        "team",
        "teams",
    ],

    "present insights to product managers": [
        "present",
        "presented",
        "insights",
        "stakeholder",
        "stakeholders",
        "manager",
        "managers",
        "product manager",
    ],
}


def _has_analysis_word(text):
    return bool(
        re.search(
            r"\banaly(?:ze|zed|zes|zing|sis|sis)\b"
            r"|\banalysis\b"
            r"|\banalyzing\b"
            r"|\banalyzed\b",
            text,
            re.IGNORECASE,
        )
    )


def calculate_responsibility_match(
    candidate_profile,
    responsibilities,
):
    sections = (
        candidate_profile.get(
            "sections",
            {},
        )
        if isinstance(candidate_profile, dict)
        else {}
    )

    resume = "\n".join(
        map(
            str,
            sections.values(),
        )
    )

    resume_low = resume.lower()

    matched = []
    missing = []
    evidence = {}

    for responsibility in (
        responsibilities or []
    ):

        r = str(
            responsibility
        ).strip()

        key = re.sub(
            r"\s+",
            " ",
            r.lower(),
        )

        concepts = RESPONSIBILITY_CONCEPTS.get(
            key
        )

        hits = []

        if concepts is None:

            words = [
                word
                for word in _tokens(r)
                if len(word) > 3
                and word not in {
                    "with",
                    "from",
                    "that",
                    "this",
                    "your",
                    "into",
                    "and",
                    "the",
                    "for",
                    "work",
                    "build",
                    "present",
                }
            ]

            resume_tokens = _tokens(
                resume
            )

            hits = [
                word
                for word in words
                if word in resume_tokens
            ]

        else:

            for concept in concepts:

                if concept == "analyz":

                    if _has_analysis_word(
                        resume_low
                    ):
                        hits.append(
                            "analysis"
                        )

                elif concept in {
                    "dashboard",
                    "dashboards",
                    "report",
                    "reports",
                    "visualization",
                    "visualisation",
                    "visualize",
                    "visualise",
                }:

                    if re.search(
                        r"\b"
                        + re.escape(concept)
                        + r"\b",
                        resume_low,
                    ):
                        hits.append(
                            concept
                        )

                else:

                    if re.search(
                        r"(?<!\w)"
                        + re.escape(concept)
                        + r"(?!\w)",
                        resume_low,
                    ):
                        hits.append(
                            concept
                        )

        unique_hits = list(
            dict.fromkeys(hits)
        )

        # Practical matching rules
        if key in {
            "build dashboards and reports",
            "work with cross-functional teams",
        }:
            ok = len(unique_hits) >= 1

        elif key == "present insights to product managers":
            # Require actual evidence of presentation/stakeholder
            # communication rather than merely "manager".
            has_present = any(
                x in resume_low
                for x in [
                    "present",
                    "presented",
                    "presentation",
                ]
            )

            has_insight_or_stakeholder = any(
                x in resume_low
                for x in [
                    "insight",
                    "insights",
                    "stakeholder",
                    "stakeholders",
                    "product manager",
                ]
            )

            ok = (
                has_present
                and has_insight_or_stakeholder
            )

        else:
            ok = len(unique_hits) >= 2

        evidence[r] = {
            "matched_concepts": unique_hits,
            "score": round(
                100
                if ok
                else min(
                    100,
                    len(unique_hits) * 25,
                ),
                2,
            ),
        }

        if ok:
            matched.append(r)
        else:
            missing.append(r)

    score = (
        100
        if not responsibilities
        else len(matched)
        / len(responsibilities)
        * 100
    )

    return {
        "score": round(score, 2),
        "matched_responsibilities": matched,
        "missing_responsibilities": missing,
        "evidence": evidence,
    }


# ============================================================
# OVERALL MATCH
# ============================================================

def calculate_overall_match(
    skill_match,
    experience_match,
    education_match,
    responsibility_match,
):
    weights = {
        "skills": 50,
        "responsibilities": 20,
        "experience": 20,
        "education": 10,
    }

    score = (
        skill_match.get("score", 0) * 0.50
        + responsibility_match.get("score", 0) * 0.20
        + experience_match.get("score", 0) * 0.20
        + education_match.get("score", 0) * 0.10
    )

    return {
        "score": round(score, 2),
        "weights": weights,
    }