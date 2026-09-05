import re


def extract_email(text: str) -> str | None:
    """Extract the first email address from resume text."""
    match = re.search(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text,
    )
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extract a likely Indian phone number from resume text."""
    patterns = [
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
        r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}(?!\d)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)

    return None


SECTION_ALIASES = {
    "education": [
        "education",
        "academic background",
        "educational qualifications",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "internships",
    ],
    "projects": [
        "projects",
        "project experience",
        "personal projects",
    ],
    "skills": [
        "skills",
        "skills and expertise",
        "technical skills",
        "technical expertise",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "certification",
    ],
    "achievements": [
        "achievements",
        "awards",
        "honors",
        "honours",
    ],
    "competitions": [
        "competition/conference",
        "competitions",
        "conference",
    ],
    "coursework": [
        "coursework information",
        "coursework",
    ],
    "extracurricular": [
        "extra curricular activities",
        "extracurricular activities",
        "extra-curricular activities",
    ],
}


def normalize_heading(line: str) -> str:
    """Normalize a possible section heading."""
    line = line.strip().lower()
    line = re.sub(r"\s+", " ", line)
    return line


def detect_section(line: str) -> str | None:
    """Identify whether a line represents a resume section heading."""
    normalized = normalize_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if normalized == alias:
                return section_name

    return None


def extract_sections(text: str) -> dict:
    """
    Extract common resume sections based on section headings.
    """
    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": "",
        "achievements": "",
        "competitions": "",
        "coursework": "",
        "extracurricular": "",
    }

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    current_section = None

    for line in lines:
        detected_section = detect_section(line)

        if detected_section:
            current_section = detected_section
            continue

        if current_section:
            sections[current_section] += line + "\n"

    sections = {
        key: value.strip()
        for key, value in sections.items()
    }

    # Clean only the education section.
    # Other sections remain unchanged.
    sections["education"] = clean_education_section(
        sections["education"]
    )

    return sections


def clean_education_section(education_text: str) -> str:
    """
    Convert table-like education extraction into readable entries.

    Example input:
        Year
        Degree/Exam
        Institute
        CGPA/Marks
        2026
        4YRS B.S
        IIT Kharagpur
        6.18 / 10

    Output:
        B.S. — IIT Kharagpur | 2026 | CGPA: 6.18 / 10
    """

    if not education_text.strip():
        return ""

    lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in education_text.splitlines()
        if line.strip()
    ]

    # Remove common table headers.
    header_values = {
        "year",
        "degree/exam",
        "degree",
        "exam",
        "institute",
        "institution",
        "cgpa/marks",
        "cgpa",
        "marks",
    }

    cleaned_lines = [
        line
        for line in lines
        if line.lower() not in header_values
    ]

    # Expected structure from the IIT resume:
    # Year -> Degree -> Institute -> CGPA/Marks
    entries = []

    i = 0

    while i < len(cleaned_lines):
        if (
            i + 3 < len(cleaned_lines)
            and re.fullmatch(r"(19|20)\d{2}", cleaned_lines[i])
        ):
            year = cleaned_lines[i]
            degree = cleaned_lines[i + 1]
            institute = cleaned_lines[i + 2]
            marks = cleaned_lines[i + 3]

            degree_clean = degree

            # Make common degree formatting cleaner.
            degree_clean = re.sub(
                r"^\s*\d+\s*YRS?\s+",
                "",
                degree_clean,
                flags=re.IGNORECASE,
            )

            if degree_clean.upper() == "B.S":
                degree_clean = "B.S."

            entry = (
                f"{degree_clean} — {institute} | "
                f"{year} | CGPA/Marks: {marks}"
            )

            entries.append(entry)
            i += 4

        else:
            # Keep unexpected education lines rather than deleting them.
            entries.append(cleaned_lines[i])
            i += 1

    return "\n".join(entries)


def build_candidate_profile(text: str) -> dict:
    """Convert raw resume text into a structured candidate profile."""
    sections = extract_sections(text)

    return {
        "email": extract_email(text),
        "phone": extract_phone(text),
        "sections": sections,
    }