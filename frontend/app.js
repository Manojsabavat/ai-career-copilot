const API_BASE = "http://127.0.0.1:8000";

const $ = (id) => document.getElementById(id);

const inputView = $("inputView");
const loadingView = $("loadingView");
const resultsView = $("resultsView");
const resumeFile = $("resumeFile");
const dropZone = $("dropZone");
const errorBox = $("errorBox");


/* =========================================================
   VIEW HELPERS
========================================================= */

function show(view) {
  [inputView, loadingView, resultsView].forEach(v =>
    v.classList.add("hidden")
  );

  view.classList.remove("hidden");

  window.scrollTo({
    top: 0,
    behavior: "smooth"
  });
}


function setError(message = "") {
  errorBox.textContent = message;
}


function selectedFile() {
  return resumeFile.files?.[0] || null;
}


function updateFileUI() {
  const file = selectedFile();

  $("fileTitle").textContent =
    file ? file.name : "Drop your PDF here";

  $("fileHint").textContent =
    file
      ? `${(file.size / 1024).toFixed(0)} KB selected`
      : "or click to browse";
}


/* =========================================================
   FILE UPLOAD
========================================================= */

$("browseBtn").addEventListener("click", () => {
  resumeFile.click();
});


dropZone.addEventListener("click", (e) => {
  if (e.target.tagName !== "BUTTON") {
    resumeFile.click();
  }
});


resumeFile.addEventListener("change", updateFileUI);


["dragenter", "dragover"].forEach(evt => {
  dropZone.addEventListener(evt, e => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });
});


["dragleave", "drop"].forEach(evt => {
  dropZone.addEventListener(evt, e => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
  });
});


dropZone.addEventListener("drop", e => {
  const file = e.dataTransfer.files?.[0];

  if (!file) return;

  if (file.type !== "application/pdf") {
    setError("Please upload a PDF resume.");
    return;
  }

  const dt = new DataTransfer();
  dt.items.add(file);

  resumeFile.files = dt.files;

  updateFileUI();
});


/* =========================================================
   API STATUS
========================================================= */

async function checkApi() {
  try {
    const r = await fetch(`${API_BASE}/health`);

    if (!r.ok) {
      throw new Error();
    }

    $("apiStatus").textContent = "API online";
    $("apiStatus").className = "status-pill online";

  } catch {
    $("apiStatus").textContent = "API offline";
    $("apiStatus").className = "status-pill offline";
  }
}

checkApi();


/* =========================================================
   GENERAL HELPERS
========================================================= */

function pct(value) {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(Number(value))
  ) {
    return "—";
  }

  return `${Number(value).toFixed(2)}%`;
}


function safeArray(value) {
  return Array.isArray(value) ? value : [];
}


function cleanText(value) {
  return String(value || "")
    .replace(/\s+/g, " ")
    .trim();
}


/* =========================================================
   CHIP RENDERING
========================================================= */

function renderChips(id, items) {
  const el = $(id);

  el.innerHTML = "";

  safeArray(items).forEach(item => {
    const span = document.createElement("span");

    span.className = "chip";
    span.textContent = item;

    el.appendChild(span);
  });

  if (!el.children.length) {
    el.innerHTML =
      '<span class="chip">None listed</span>';
  }
}


/* =========================================================
   PROFILE FORMATTING
========================================================= */

function renderCandidateEducation(education) {
  const el = $("profileSummary");

  el.innerHTML = "";

  const title = document.createElement("div");
  title.className = "summary-section-title";
  title.textContent = "Education";

  el.appendChild(title);

  const educationLines = String(education || "")
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean);

  if (!educationLines.length) {
    const empty = document.createElement("div");
    empty.textContent = "Not available";
    el.appendChild(empty);
    return;
  }

  educationLines.forEach(line => {
    const item = document.createElement("div");

    item.className = "summary-line";
    item.textContent = line;

    el.appendChild(item);
  });
}


function renderCandidateProfile(profile) {
  const el = $("profileSummary");

  el.innerHTML = "";

  /* Education */
  const educationTitle = document.createElement("div");
  educationTitle.className = "summary-section-title";
  educationTitle.textContent = "Education";

  el.appendChild(educationTitle);

  const educationLines = String(profile.education || "")
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean);

  if (educationLines.length) {
    educationLines.forEach(line => {
      const item = document.createElement("div");

      item.className = "summary-line";
      item.textContent = line;

      el.appendChild(item);
    });
  } else {
    const item = document.createElement("div");
    item.className = "summary-line";
    item.textContent = "Not available";
    el.appendChild(item);
  }


  /* Experience */
  const experienceTitle = document.createElement("div");
  experienceTitle.className = "summary-section-title";
  experienceTitle.textContent = "Experience";

  el.appendChild(experienceTitle);

  const experienceLines = String(profile.experience || "")
    .split(/\n+/)
    .map(line => line.trim())
    .filter(Boolean);

  if (experienceLines.length) {
    experienceLines.forEach(line => {
      const item = document.createElement("div");

      item.className = "summary-line";
      item.textContent = line;

      el.appendChild(item);
    });
  } else {
    const item = document.createElement("div");
    item.className = "summary-line";
    item.textContent = "Not available";
    el.appendChild(item);
  }


  /* Skills */
  const skillsTitle = document.createElement("div");
  skillsTitle.className = "summary-section-title";
  skillsTitle.textContent = "Skills";

  el.appendChild(skillsTitle);

  const skillsText = String(profile.skills || "")
    .replace(/^Skills:\s*/i, "")
    .trim();

  if (skillsText) {
    const skillsLines = skillsText
      .split(/\n+/)
      .map(line => line.trim())
      .filter(Boolean);

    skillsLines.forEach(line => {
      const item = document.createElement("div");

      item.className = "summary-line";
      item.textContent = line;

      el.appendChild(item);
    });
  } else {
    const item = document.createElement("div");
    item.className = "summary-line";
    item.textContent = "Not available";
    el.appendChild(item);
  }
}


/* =========================================================
   JOB TITLE
========================================================= */

function formatJobTitle(title) {
  let value = cleanText(title);

  if (!value) {
    return "Job Match";
  }

  /*
   * Handles titles accidentally extracted as:
   * Product Data Analyst Job Summary: ...
   */

  value = value.split(/\s+Job Summary\s*:/i)[0];

  value = value.split(/\s+Job Description\s*:/i)[0];

  return value.trim() || "Job Match";
}


/* =========================================================
   JOB REQUIREMENTS
========================================================= */

function renderJobRequirements(job) {
  const el = $("jobSummary");

  el.innerHTML = "";


  /* Required Skills */
  const skillsTitle = document.createElement("div");
  skillsTitle.className = "summary-section-title";
  skillsTitle.textContent = "Required Skills";

  el.appendChild(skillsTitle);


  const skillContainer = document.createElement("div");
  skillContainer.className = "summary-chip-list";

  safeArray(job.required_skills).forEach(skill => {
    const chip = document.createElement("span");

    chip.className = "chip";
    chip.textContent = skill;

    skillContainer.appendChild(chip);
  });

  if (!skillContainer.children.length) {
    const empty = document.createElement("span");
    empty.className = "chip";
    empty.textContent = "None listed";

    skillContainer.appendChild(empty);
  }

  el.appendChild(skillContainer);


  /* Experience */
  const experienceTitle = document.createElement("div");
  experienceTitle.className = "summary-section-title";
  experienceTitle.textContent = "Experience";

  el.appendChild(experienceTitle);


  const experience = document.createElement("div");
  experience.className = "summary-line";
  experience.textContent =
    job.experience || "Not specified";

  el.appendChild(experience);


  /* Education */
  const educationTitle = document.createElement("div");
  educationTitle.className = "summary-section-title";
  educationTitle.textContent = "Education";

  el.appendChild(educationTitle);


  const education = document.createElement("div");
  education.className = "summary-line";
  education.textContent =
    job.education || "Not specified";

  el.appendChild(education);


  /* Responsibilities */
  const responsibilitiesTitle = document.createElement("div");
  responsibilitiesTitle.className = "summary-section-title";
  responsibilitiesTitle.textContent = "Responsibilities";

  el.appendChild(responsibilitiesTitle);


  const responsibilities = document.createElement("div");
  responsibilities.className = "summary-responsibilities";

  safeArray(job.responsibilities).forEach(item => {
    const row = document.createElement("div");

    row.className = "summary-responsibility";
    row.textContent = `• ${item}`;

    responsibilities.appendChild(row);
  });


  if (!responsibilities.children.length) {
    const empty = document.createElement("div");

    empty.className = "summary-line";
    empty.textContent = "None listed";

    responsibilities.appendChild(empty);
  }

  el.appendChild(responsibilities);
}


/* =========================================================
   RESULTS
========================================================= */

function renderResults(data) {
  const match = data.match_result || {};

  const overall = match.overall || {};
  const skills = match.skills || {};
  const experience = match.experience || {};
  const education = match.education || {};
  const responsibilities = match.responsibilities || {};

  const rec = data.recommendation || {};

  const job = data.job_profile || {};
  const profile = data.candidate_profile?.sections || {};


  /* -----------------------------------------
     Job title
  ----------------------------------------- */

  $("jobTitle").textContent =
    formatJobTitle(job.job_title);


  /* -----------------------------------------
     Summary
  ----------------------------------------- */

  $("summary").textContent =
    rec.summary || "Analysis completed.";


  /* -----------------------------------------
     Scores
  ----------------------------------------- */

  $("overallScore").textContent =
    pct(overall.score);

  $("skillScore").textContent =
    pct(skills.score);

  $("experienceScore").textContent =
    pct(experience.score);

  $("educationScore").textContent =
    pct(education.score);

  $("responsibilityScore").textContent =
    pct(responsibilities.score);


  /* -----------------------------------------
     Skills
  ----------------------------------------- */

  renderChips(
    "matchedSkills",
    skills.matched_skills
  );

  renderChips(
    "missingSkills",
    skills.missing_skills
  );

  $("skillCount").textContent =
    `${safeArray(skills.matched_skills).length} matched`;


  /* -----------------------------------------
     Responsibilities
  ----------------------------------------- */

  const responsibilityList =
    $("responsibilityList");

  responsibilityList.innerHTML = "";


  safeArray(
    responsibilities.matched_responsibilities
  ).forEach(item => {

    const div = document.createElement("div");

    div.className = "resp ok";
    div.textContent = `✓ ${item}`;

    responsibilityList.appendChild(div);
  });


  safeArray(
    responsibilities.missing_responsibilities
  ).forEach(item => {

    const div = document.createElement("div");

    div.className = "resp missing";
    div.textContent = `× ${item}`;

    responsibilityList.appendChild(div);
  });


  if (!responsibilityList.children.length) {
    responsibilityList.innerHTML =
      '<div class="resp">No responsibility details returned.</div>';
  }


  /* -----------------------------------------
     Recommendations
  ----------------------------------------- */

  const recList =
    $("recommendationList");

  recList.innerHTML = "";


  safeArray(rec.recommendations)
    .forEach(item => {

      const li = document.createElement("li");

      li.textContent = item;

      recList.appendChild(li);
    });


  if (!recList.children.length) {
    recList.innerHTML =
      "<li>No recommendations returned.</li>";
  }

  /* -----------------------------------------
   Resume Optimization
----------------------------------------- */

const optimization =
  data.resume_optimization || {};

const optimizationEl =
  $("resumeOptimization");

optimizationEl.innerHTML = "";

const improvements =
  safeArray(optimization.resume_improvements);

const keywords =
  safeArray(optimization.keyword_suggestions);

const projects =
  safeArray(optimization.project_ideas);

const priorityActions =
  safeArray(optimization.priority_actions);


if (improvements.length) {
  const title = document.createElement("h3");
  title.textContent = "Resume Improvements";
  optimizationEl.appendChild(title);

  const list = document.createElement("ul");

  improvements.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });

  optimizationEl.appendChild(list);
}


if (keywords.length) {
  const title = document.createElement("h3");
  title.textContent = "Suggested Keywords";
  optimizationEl.appendChild(title);

  const chips = document.createElement("div");
  chips.className = "chips";

  keywords.forEach(item => {
    const chip = document.createElement("span");
    chip.className = "chip";
    chip.textContent = item;
    chips.appendChild(chip);
  });

  optimizationEl.appendChild(chips);
  const bullets = optimization.bullet_optimizations || [];

if (bullets.length) {
  const title = document.createElement("h3");
  title.textContent = "JD-Aligned Bullet Suggestions";
  optimizationEl.appendChild(title);

  bullets.forEach((item) => {
    const box = document.createElement("div");
    box.className = "resume-bullet-optimization";

    const requirement = document.createElement("div");
    requirement.className = "summary-line";
    requirement.innerHTML = `<strong>Requirement:</strong> ${item.requirement || ""}`;

    const current = document.createElement("div");
    current.className = "summary-line";
    current.innerHTML = `<strong>Current:</strong> ${item.current || ""}`;

    const suggested = document.createElement("div");
    suggested.className = "summary-line";
    suggested.innerHTML = `<strong>Suggested:</strong> ${item.suggested || ""}`;

    const why = document.createElement("div");
    why.className = "summary-line";
    why.innerHTML = `<strong>Why:</strong> ${item.why || ""}`;

    box.appendChild(requirement);
    box.appendChild(current);
    box.appendChild(suggested);
    box.appendChild(why);

    optimizationEl.appendChild(box);
  });
}

else {
  const title = document.createElement("h3");
  title.textContent = "JD-Aligned Bullet Suggestions";
  optimizationEl.appendChild(title);

  const message = document.createElement("div");
  message.className = "summary-line";
  message.textContent =
    "No strong existing resume evidence was found for the remaining JD responsibilities. Add evidence only if you have actually performed this work.";
  optimizationEl.appendChild(message);
}
}

if (projects.length) {
  const title = document.createElement("h3");
  title.textContent = "Project Ideas";
  optimizationEl.appendChild(title);

  const list = document.createElement("ul");

  projects.forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });

  optimizationEl.appendChild(list);
}


if (priorityActions.length) {
  const title = document.createElement("h3");
  title.textContent = "Priority Actions";
  optimizationEl.appendChild(title);

  const list = document.createElement("ul");

  priorityActions.forEach(item => {
    const li = document.createElement("li");
    li.textContent =
      `${item.priority.toUpperCase()}: ${item.action}`;
    list.appendChild(li);
  });

  optimizationEl.appendChild(list);
}


if (!optimizationEl.children.length) {
  optimizationEl.textContent =
    "No resume optimization suggestions available.";
}

  /* -----------------------------------------
     Candidate Profile
  ----------------------------------------- */

  renderCandidateProfile(profile);


  /* -----------------------------------------
     Job Requirements
  ----------------------------------------- */

  renderJobRequirements(job);
}


/* =========================================================
   ANALYZE
========================================================= */

$("analyzeBtn").addEventListener(
  "click",
  async () => {

    setError("");

    const file = selectedFile();

    const jd =
      $("jobDescription").value.trim();


    if (!file) {
      return setError(
        "Please upload a PDF resume."
      );
    }


    if (file.type !== "application/pdf") {
      return setError(
        "Only PDF resumes are supported."
      );
    }


    if (!jd) {
      return setError(
        "Please paste the job description."
      );
    }


    const form = new FormData();

    form.append("file", file);
    form.append("job_description", jd);


    show(loadingView);


    try {

      const response =
        await fetch(`${API_BASE}/analyze`, {
          method: "POST",
          body: form
        });


      const data =
        await response.json();


      if (!response.ok) {
        throw new Error(
          data.detail ||
          `Analysis failed (${response.status})`
        );
      }


      renderResults(data);

      show(resultsView);

    } catch (err) {

      show(inputView);

      setError(
        err.message ||
        "Unable to connect to the backend."
      );
    }
  }
);


/* =========================================================
   NEW ANALYSIS
========================================================= */

$("newAnalysisBtn").addEventListener(
  "click",
  () => {

    setError("");

    show(inputView);
  }
);


/* =========================================================
   PERIODIC API CHECK
========================================================= */

setInterval(checkApi, 10000);