import re
import fitz
import base64
import streamlit as st
import spacy
import csv
import nltk

# ---------------------------------- Setup ----------------------------------
nltk.download('punkt', quiet=True)
nlp = spacy.load('en_core_web_sm')

# ------------------------------ Helper Functions ---------------------------
def load_keywords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        return set(row[0].strip() for row in reader if row)

# ============================== NAME EXTRACTION =============================
BLACKLIST_TITLE_WORDS = {
    "intern", "internship", "trainee", "vocational", "project", "based",
    "engineer", "developer", "student", "fresher", "manager", "consultant",
    "associate", "analyst", "software", "graduate", "director", "founder",
    "cofounder", "co-founder", "company", "inc", "llc", "school", "college",
    "department", "team", "lead", "senior", "junior"
}

def _clean_tokens(s):
    return [t for t in re.sub(r"[^A-Za-z\s]", " ", s).split() if t]

def _looks_like_name(tokens):
    if not (2 <= len(tokens) <= 4):
        return False
    if any(tok.lower() in BLACKLIST_TITLE_WORDS for tok in tokens):
        return False
    upper_tokens = sum(1 for t in tokens if t[0].isupper() or t.isupper())
    return (upper_tokens / len(tokens)) >= 0.6

def extract_name(doc):
    """
    Extract likely first and last name from the top of the resume.
    """
    text = doc.text.strip()
    email_m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    phone_m = re.search(r"(\+?\d[\d\s\-\(\)]{6,}\d)", text)
    header_limit = min(email_m.start() if email_m else len(text),
                       phone_m.start() if phone_m else len(text),
                       500)

    # Check PERSON entities first (before header limit)
    candidates = []
    for ent in doc.ents:
        if ent.label_ == "PERSON" and ent.start_char < header_limit:
            tokens = _clean_tokens(ent.text)
            if _looks_like_name(tokens):
                candidates.append((ent.start_char, " ".join(tokens)))

    if candidates:
        candidates.sort(key=lambda x: (x[0], -len(x[1])))
        name = candidates[0][1].strip()
        parts = name.split()
        return parts[0], " ".join(parts[1:]) if len(parts) > 1 else ""

    # Fallback: top few lines
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:6]:
        tokens = _clean_tokens(ln)
        if _looks_like_name(tokens):
            return tokens[0], " ".join(tokens[1:])

    # Fallback: derive from email prefix
    if email_m:
        prefix = email_m.group(0).split("@")[0]
        parts = [p.capitalize() for p in re.split(r"[._\-]", prefix) if p]
        if len(parts) >= 2:
            return parts[0], " ".join(parts[1:])
        return parts[0], ""

    return "", ""

# ============================== EMAIL EXTRACTION ============================
def extract_email(doc):
    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    match = re.search(pattern, doc.text)
    return match.group() if match else ""

# ============================== PHONE EXTRACTION ===========================
def extract_contact_number_from_resume(doc):
    text = doc.text
    pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}"
    match = re.search(pattern, text)
    if match:
        return re.sub(r"\D", "", match.group())
    return ""

# ============================= EDUCATION EXTRACTION ========================
def extract_education_from_resume(doc):
    universities = set()
    for entity in doc.ents:
        if entity.label_ == "ORG" and any(
            kw in entity.text.lower() for kw in ["university", "college", "institute", "school"]
        ):
            universities.add(entity.text.strip())
    return list(universities)

# =============================== SKILLS EXTRACTION =========================
def csv_skills(doc):
    skills_keywords = load_keywords('data/newSkills.csv')
    text = doc.text.lower()
    return {kw for kw in skills_keywords if kw.lower() in text}

nlp_skills = spacy.load('TrainedModel/skills')

def extract_skills_from_ner(doc):
    non_skill_labels = {'DATE', 'TIME', 'PERCENT', 'MONEY', 'QUANTITY', 'ORDINAL', 'CARDINAL', 'EMAIL', 'PLACE'}
    skills = set()
    for ent in nlp_skills(doc.text).ents:
        if ent.label_ == 'SKILL' and ent.label_ not in non_skill_labels:
            skill = re.sub(r"[^A-Za-z+# ]", "", ent.text.strip())
            if 2 <= len(skill) <= 40:
                skills.add(skill)
    return skills

def is_valid_skill(skill):
    banned = {
    # months
    "may","june","july","august","september","october","november","december",
    "january","february","march","april","jan","feb","mar","apr","aug","sep","oct","nov","dec",
    # action verbs / resume noise
    "led","supervised","managed","directed","coordinated","oversaw","executed","developed",
    "designed","implemented","built","engineered","created","launched","mentored","constructed",
    "enhanced","optimized","organized","analyzed","tested","documented","supported","collaborated",
    "improved","communicated","achieved","presented","increased","deployed","configured",
    # section titles or generic
    "technical skills","other skills","education","experience","project","projects","summary",
    "profile","school","college","university","secondary","higher secondary","details"
    }
    return len(skill) > 1 and not any(c.isdigit() for c in skill) and skill.lower() not in banned

def extract_skills(doc):
    csv_s = csv_skills(doc)
    ner_s = extract_skills_from_ner(doc)
    combined = {s for s in csv_s.union(ner_s) if is_valid_skill(s)}
    return sorted(combined)

# =============================== MAJOR EXTRACTION ==========================
def extract_major(doc):
    major_keywords = load_keywords('data/majors.csv')
    for kw in major_keywords:
        if kw.lower() in doc.text.lower():
            return kw
    return ""

# ============================= EXPERIENCE EXTRACTION =======================
def extract_experience(doc):
    verbs = [token.lemma_.lower() for token in doc if token.pos_ == 'VERB']
    senior = {'lead', 'manage', 'direct', 'oversee', 'supervise'}
    mid = {'develop', 'design', 'analyze', 'implement', 'execute'}
    junior = {'assist', 'support', 'collaborate', 'participate'}

    if any(v in verbs for v in senior):
        level = "Senior"
    elif any(v in verbs for v in mid):
        level = "Mid-Senior"
    elif any(v in verbs for v in junior):
        level = "Mid-Junior"
    else:
        level = "Entry Level"

    return {'level_of_experience': level, 'suggested_position': suggest_position(verbs)}

# ============================= POSITION SUGGESTION ========================
def load_positions_keywords(file_path):
    positions_keywords = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            position = row['position'].strip()
            keywords = [k.strip().lower() for k in row['keywords'].split(',')]
            positions_keywords[position] = keywords
    return positions_keywords

def suggest_position(verbs):
    verbs = [v.lower() for v in verbs]
    positions = load_positions_keywords('data/position.csv')
    for pos, keywords in positions.items():
        if any(k in verbs for k in keywords):
            return pos
    return "Position Not Identified"

# ============================= PDF TEXT EXTRACTION ========================
def extract_resume_info_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return nlp(text)

# ============================= DISPLAY UTILITIES ==========================
def show_colored_skills(skills):
    st.markdown(", ".join(sorted(skills)))

def calculate_resume_score(resume_info):
    score = 0
    if resume_info.get('first_name') and resume_info.get('last_name'):
        score += 25
    if resume_info.get('email'):
        score += 25
    if resume_info.get('degree_major'):
        score += 25
    if resume_info.get('skills'):
        score += 25
    return score

# ============================= MASTER PARSER ===============================
def extract_resume_info(doc):
    first_name, last_name = extract_name(doc)
    email = extract_email(doc)
    skills = extract_skills(doc)
    degree_major = extract_major(doc)
    experience = extract_experience(doc)

    return {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'degree_major': degree_major,
        'skills': skills,
        'experience': experience
    }

# ============================= SKILL SUGGESTION ===========================
def suggest_skills_for_job(desired_job):
    job_skills_mapping = {}
    with open('data/sugestedSkills.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if not row:
                continue
            job_title = row[0].lower()
            job_skills_mapping[job_title] = [s.strip() for s in row[1:] if s.strip()]
    return job_skills_mapping.get(desired_job.lower(), [])
