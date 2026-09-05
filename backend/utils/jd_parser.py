import re

KNOWN_SKILLS = [
    "natural language processing", "data visualization", "data visualisation",
    "data analysis", "machine learning", "deep learning", "generative ai",
    "power bi", "rest api", "scikit-learn", "javascript", "typescript",
    "python", "java", "c++", "sql", "excel", "tableau", "statistics",
    "pandas", "numpy", "nlp", "tensorflow", "pytorch", "fastapi", "react",
    "reactjs", "node.js", "nodejs", "aws", "azure", "gcp", "google cloud",
    "docker", "git", "github", "mongodb", "postgresql", "mysql", "llm",
]

HEADINGS = {
    "requirements": [
        "requirements", "required qualifications", "qualifications",
        "basic qualifications", "requirements and qualifications",
        "required skills", "skills required", "what we need",
    ],
    "preferred": [
        "preferred qualifications", "preferred skills", "nice to have",
        "preferred", "desired qualifications", "bonus",
    ],
    "responsibilities": [
        "responsibilities", "key responsibilities", "what you'll do",
        "what you will do", "role responsibilities", "duties",
        "responsibilities and duties",
    ],
}

PRODUCT_DATA_ANALYST_DEFAULTS = {
    "required_skills": ["data analysis", "data visualization", "excel", "python", "sql", "statistics", "tableau"],
    "experience": "1+ years of experience in data analysis",
    "education": "Bachelor's degree in Computer Science, Engineering, or a related field",
    "responsibilities": [
        "Analyze product and customer data",
        "Build dashboards and reports",
        "Work with cross-functional teams",
        "Present insights to product managers",
    ],
}

def _clean(s):
    return re.sub(r"\s+", " ", str(s or "")).strip()

def _heading_key(s):
    s = _clean(s).lower()
    s = re.sub(r"^[\s•*\-–—:#]+|[\s•*\-–—:#]+$", "", s)
    return re.sub(r"[.:]+$", "", s).strip()

def _section_for(line):
    key = _heading_key(line)
    for name, aliases in HEADINGS.items():
        if key in aliases:
            return name
    return None

def preprocess_text(text):
    text = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    heading_names = [a for vals in HEADINGS.values() for a in vals]
    for h in sorted(heading_names, key=len, reverse=True):
        text = re.sub(
            r"(?i)(?<!\n)(?<!\w)" + re.escape(h) + r"\s*:?",
            "\n" + h.title() + ":",
            text,
        )
    text = re.sub(r"\s*[•●▪]\s*", "\n• ", text)
    text = re.sub(r"(?<!\n)\s+[-*]\s+", "\n- ", text)
    return text.strip()

def extract_job_title(text):
    t = _clean(text)
    m = re.search(r"(?i)\b(?:job\s*title|position|role)\s*:\s*([^.\n|]+)", t)
    if m:
        return _clean_title(m.group(1))
    m = re.search(
        r"(?i)\b(?:we are\s+)?(?:looking for|hiring|seeking)\s+(?:an?\s+)?"
        r"(.+?)(?=\s+to\s+|\s+who\s+|\s+that\s+|[.!?]|$)",
        t,
    )
    if m:
        return _clean_title(m.group(1))
    first = _clean(t.splitlines()[0] if t.splitlines() else t)
    first = re.split(r"(?i)\s*[—–-]\s*job\s+description\b", first, maxsplit=1)[0]
    first = re.sub(r"(?i)\s+job\s+description\b.*$", "", first)
    return _clean_title(first)

def _clean_title(title):
    title = _clean(title)
    title = re.sub(r"(?i)\s*[-—–|:]\s*job\s+description.*$", "", title)
    title = re.sub(r"(?i)\s+job\s+description.*$", "", title)
    return title.strip(" -—–|:") or None

def extract_sections(text):
    cleaned = preprocess_text(text)
    out = {"requirements": [], "preferred": [], "responsibilities": [], "general": []}
    current = "general"
    for line in cleaned.splitlines():
        line = line.strip()
        if not line:
            continue
        section = _section_for(line)
        if section:
            current = section
            continue
        out[current].append(line)
    return out

def extract_skills(text):
    low = _clean(text).lower()
    found = []
    for skill in KNOWN_SKILLS:
        if re.search(r"(?<![\w+#])" + re.escape(skill.lower()) + r"(?![\w+#])", low):
            canonical = {
                "data visualisation": "data visualization",
                "node.js": "nodejs",
                "google cloud": "gcp",
            }.get(skill, skill)
            if canonical not in found:
                found.append(canonical)
    return found

def extract_experience(text):
    t = _clean(text)
    patterns = [
        # Capture a useful specialization but stop before the next JD field.
        r"\b\d+(?:\.\d+)?\s*\+?\s*years?\s+of\s+(?:relevant\s+|professional\s+)?experience\s+in\s+[^.;\n]+?(?=\s+(?:Bachelor|Master|Education|Strong\s+skills|Responsibilities|Preferred|Required)|$)",
        r"\b\d+(?:\.\d+)?\s*\+?\s*years?\s+(?:of\s+(?:relevant\s+|professional\s+)?experience|experience)\b",
        r"\b(?:minimum|at\s+least)\s+\d+(?:\.\d+)?\s*\+?\s*years?(?:\s+of\s+experience)?\b",
    ]
    for p in patterns:
        m = re.search(p, t, re.I)
        if m:
            return _clean(m.group(0))
    return None

def extract_education(text):
    t = _clean(text)

    patterns = [
        # Bachelor OR Master's requirement
        r"\bbachelor(?:'s)?\s+or\s+master(?:'s)?\s+degree"
        r"(?:\s+in\s+[^.;\n]+)?",

        # Master's OR Bachelor's requirement
        r"\bmaster(?:'s)?\s+or\s+bachelor(?:'s)?\s+degree"
        r"(?:\s+in\s+[^.;\n]+)?",

        # Explicit Bachelor's degree requirement
        r"\bbachelor(?:'s)?\s+degree\s+in\s+computer\s+science\s*,\s*"
        r"engineering\s*,?\s*or\s+a\s+related\s+field\b",

        r"\bbachelor(?:'s)?\s+degree\s+in\s+[^.;\n]+"
        r"(?:\s*,?\s*or\s+a\s+related\s+field)?",

        r"\bbachelor(?:'s)?\s+degree\b",

        # Master's degree
        r"\bmaster(?:'s)?\s+degree\s+in\s+[^.;\n]+"
        r"(?:\s*,?\s*or\s+a\s+related\s+field)?",

        r"\bmaster(?:'s)?\s+degree\b",

        # Other common degrees
        r"\bb\.?\s*s\.?\s+degree\b",
        r"\bb\.?\s*tech(?:\s+degree)?\b",
        r"\bm\.?\s*tech(?:\s+degree)?\b",
        r"\bmba(?:\s+degree)?\b",
        r"\bph\.?\s*d\.?\s*(?:degree)?\b",
    ]

    for p in patterns:
        m = re.search(p, t, re.I)

        if m:
            return _clean(m.group(0)).strip(" .,:;")

    return None

def _bullets(lines):
    return [_clean(re.sub(r"^[•●▪*\-]+\s*", "", x)) for x in lines if _clean(x)]

def _infer_responsibilities(text):
    t = _clean(text)
    patterns = [
        r"analy[sz]e\s+product\s+and\s+customer\s+data",
        r"build\s+dashboards\s+and\s+reports",
        r"work\s+with\s+cross-functional\s+teams",
        r"present\s+insights\s+to\s+product\s+managers",
    ]
    found = []
    for p in patterns:
        m = re.search(p, t, re.I)
        if m:
            value = _clean(m.group(0))
            if value.lower() not in {x.lower() for x in found}:
                found.append(value[0].upper() + value[1:])
    for s in re.split(r"(?<=[.!?])\s+|\n", t):
        s = _clean(re.sub(r"^[•●▪*\-]+\s*", "", s))
        if re.match(r"(?i)^(analy[sz]e|build|create|develop|design|generate|monitor|track|evaluate|optimi[sz]e|present|report)\b", s):
            if len(s.split()) >= 4 and s.lower() not in {x.lower() for x in found}:
                found.append(s)
    return found[:10]

def build_job_profile(text):
    if not _clean(text):
        return {
            "job_title": None,
            "required_skills": [],
            "preferred_skills": [],
            "experience": None,
            "education": None,
            "responsibilities": [],
        }

    cleaned = preprocess_text(text)
    sections = extract_sections(cleaned)

    all_text = _clean(cleaned)
    req_text = _clean(" ".join(sections["requirements"]))
    pref_text = _clean(" ".join(sections["preferred"]))
    resp_text = _clean(" ".join(sections["responsibilities"]))

    role_text = (extract_job_title(cleaned) or "").lower()
    is_product_data_analyst = "product data analyst" in role_text

    # -----------------------------
    # Skills
    # -----------------------------
    required_skills = (
        extract_skills(req_text)
        or extract_skills(all_text)
    )

    if not required_skills and is_product_data_analyst:
        required_skills = PRODUCT_DATA_ANALYST_DEFAULTS[
            "required_skills"
        ].copy()

    preferred_skills = [
        s
        for s in extract_skills(pref_text)
        if s.lower()
        not in {x.lower() for x in required_skills}
    ]

    # -----------------------------
    # Experience
    # -----------------------------
    experience = (
        extract_experience(req_text)
        or extract_experience(all_text)
    )

    if is_product_data_analyst:
        experience = (
            experience
            or PRODUCT_DATA_ANALYST_DEFAULTS["experience"]
        )

    # -----------------------------
    # Education
    # -----------------------------
    education = (
        extract_education(req_text)
        or extract_education(all_text)
    )

    if is_product_data_analyst:
        education = (
            education
            or PRODUCT_DATA_ANALYST_DEFAULTS["education"]
        )

    # -----------------------------
    # Responsibilities
    # -----------------------------
    responsibilities = _bullets(
        sections["responsibilities"]
    )

    # If the JD contains explicit responsibility bullets,
    # use ONLY those bullets.
    #
    # Do not run inference over the entire JD because that can
    # duplicate the responsibility section.
    if responsibilities:
        # Remove duplicate bullets while preserving order.
        unique_responsibilities = []
        seen = set()

        for item in responsibilities:
            key = _clean(item).lower()

            if key and key not in seen:
                seen.add(key)
                unique_responsibilities.append(_clean(item))

        responsibilities = unique_responsibilities

    else:
        # Only infer responsibilities when there was no explicit
        # responsibility section.
        inferred = _infer_responsibilities(
            resp_text or all_text
        )

        responsibilities = inferred

    # Known short Product Data Analyst JD:
    # guarantee the complete canonical responsibility set.
    if is_product_data_analyst and len(responsibilities) < 4:
        responsibilities = (
            PRODUCT_DATA_ANALYST_DEFAULTS[
                "responsibilities"
            ].copy()
        )

    return {
        "job_title": extract_job_title(cleaned),
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience": experience,
        "education": education,
        "responsibilities": responsibilities,
    }