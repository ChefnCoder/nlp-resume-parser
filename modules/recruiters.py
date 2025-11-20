import streamlit as st
import csv
import spacy
from resume_parser import (
    extract_resume_info_from_pdf,
    extract_resume_info,
    extract_skills
)

# Load SpaCy model (fallback only)
nlp = spacy.load('en_core_web_sm')


# =============================== MAIN PANEL ===============================
def process_recruiters_mode():
    # Title section with style
    st.markdown(
        """
        <h1 style="text-align:center; color:#4f46e5;">
            👩‍💼 Recruiter's Smart Resume Panel
        </h1>
        <p style="text-align:center; color:gray;">
            Upload resumes, check skills, and view AI-based match scores ⚡
        </p>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<hr style="border: 2px solid #4f46e5;">', unsafe_allow_html=True)

    # File upload
    uploaded_files = st.file_uploader("📁 **Upload Resumes (PDF)**", accept_multiple_files=True)

    # Input skills
    st.markdown("### 🎯 Required Skills")
    required_skills_input = st.text_input("Enter required skills (comma-separated):", "")
    required_skills = [skill.strip().lower() for skill in required_skills_input.split(',') if skill.strip()]

    # Save required skills
    if st.button("💾 Save Required Skills"):
        save_required_skills(required_skills)

    # Process resumes
    if uploaded_files:
        st.markdown('<hr style="border: 1px solid #ddd;">', unsafe_allow_html=True)
        all_skills_found = set()

        for idx, file in enumerate(uploaded_files, start=1):
            # Extract info
            doc = extract_resume_info_from_pdf(file)
            parsed_info = extract_resume_info(doc)

            candidate_name = f"{parsed_info.get('first_name', '')} {parsed_info.get('last_name', '')}".strip() or "Candidate name not found"
            candidate_skills = {s.lower() for s in parsed_info.get('skills', [])}
            degree_major = parsed_info.get('degree_major', 'Not found')
            email = parsed_info.get('email', 'Not found')
            experience_level = parsed_info.get('experience', {}).get('level_of_experience', 'Not found')
            suggested_position = parsed_info.get('experience', {}).get('suggested_position', 'Not identified')

            # =================== Candidate Card ===================
            st.markdown(
                f"""
                <div style="
                    background: #f9fafb;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                    margin-bottom: 20px;">
                    <h3 style="color:#4f46e5;">📄 Candidate {idx}: {candidate_name}</h3>
                    <p style="margin:0;"><b>📧 Email:</b> {email}</p>
                    <p style="margin:0;"><b>🎓 Degree/Major:</b> {degree_major}</p>
                    <p style="margin:0;"><b>💼 Experience:</b> {experience_level}</p>
                    <p style="margin:0;"><b>💡 Suggested Role:</b> {suggested_position}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Display extracted skills
            display_parsed_skills(candidate_skills)

            # Compare and calculate match
            matched_skills, missing_skills = match_required_skills(candidate_skills, required_skills)
            match_score = calculate_match_score(matched_skills, required_skills)

            # Styled match score bar
            display_match_score(match_score, candidate_name)

            # Show skill comparison
            display_skills_match(matched_skills, missing_skills)

            all_skills_found.update(candidate_skills)

        if all_skills_found:
            st.markdown('<hr>', unsafe_allow_html=True)
            st.success("✅ All resumes processed successfully!")


# =============================== UTILITIES ===============================
def save_required_skills(required_skills):
    """Save required skills list"""
    with open('data/UpdatedSkills.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for skill in required_skills:
            writer.writerow([skill])
    st.success("✅ Required skills saved successfully!")


def match_required_skills(candidate_skills, required_skills):
    """Match candidate skills with recruiter requirements"""
    required_set = set(s.lower() for s in required_skills)
    matched = candidate_skills.intersection(required_set)
    missing = required_set - candidate_skills
    return matched, missing


def calculate_match_score(matched_skills, required_skills):
    """Calculate skill match score"""
    if not required_skills:
        return 0
    score = (len(matched_skills) / len(required_skills)) * 100
    return round(score, 2)


def display_match_score(score, candidate_name):
    """Show a colored score bar with emoji indicators"""
    st.markdown("### 📊 Match Score")
    if score == 0:
        st.info("ℹ️ Enter required skills to calculate match score.")
        return

    # Color coding
    if score >= 80:
        color = "#22c55e"  # green
        emoji = "🟢 Excellent Fit"
    elif score >= 50:
        color = "#facc15"  # yellow
        emoji = "🟡 Moderate Fit"
    else:
        color = "#ef4444"  # red
        emoji = "🔴 Low Fit"

    bar_html = f"""
    <div style="background:#e5e7eb; border-radius:8px; height:25px;">
        <div style="
            width:{score}%;
            height:25px;
            background:linear-gradient(90deg,{color},#6366f1);
            border-radius:8px;
            display:flex;
            align-items:center;
            justify-content:center;
            color:white;
            font-weight:bold;">
            {score}% Match
        </div>
    </div>
    <p style="color:{color}; font-weight:bold;">{emoji}</p>
    """
    st.markdown(bar_html, unsafe_allow_html=True)


def display_parsed_skills(parsed_skills):
    """Show extracted skills"""
    st.markdown("### 🧠 Extracted Skills")
    if parsed_skills:
        skills_list = " ".join(
            f"<span style='background:#e0e7ff; color:#1e3a8a; padding:5px 10px; border-radius:15px; margin:3px; display:inline-block;'>{skill}</span>"
            for skill in sorted(parsed_skills)
        )
        st.markdown(skills_list, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No skills detected.")


def display_skills_match(matched_skills, missing_skills):
    """Show found/missing skills with colored badges"""
    st.markdown("### 🔍 Skills Match Report")

    if matched_skills:
        st.markdown(
            "<h4 style='color:#22c55e;'>✅ Found Skills:</h4>"
            + " ".join(
                f"<span style='background:#dcfce7; color:#166534; padding:5px 10px; border-radius:15px; margin:3px; display:inline-block;'>{skill}</span>"
                for skill in sorted(matched_skills)
            ),
            unsafe_allow_html=True
        )

    if missing_skills:
        st.markdown(
            "<h4 style='color:#ef4444;'>❌ Missing Skills:</h4>"
            + " ".join(
                f"<span style='background:#fee2e2; color:#7f1d1d; padding:5px 10px; border-radius:15px; margin:3px; display:inline-block;'>{skill}</span>"
                for skill in sorted(missing_skills)
            ),
            unsafe_allow_html=True
        )


# =============================== ENTRY POINT ===============================
if __name__ == "__main__":
    process_recruiters_mode()
