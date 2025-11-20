import streamlit as st
import sqlite3
from resume_parser import (
    extract_resume_info_from_pdf, 
    extract_contact_number_from_resume, 
    extract_education_from_resume, 
    extract_experience, 
    suggest_skills_for_job, 
    show_colored_skills, 
    calculate_resume_score, 
    extract_resume_info
)

# ============================== DATABASE SETUP ==============================
def create_table():
    conn = sqlite3.connect('data/user_pdfs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_uploaded_pdfs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            data BLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_pdf(name, data):
    conn = sqlite3.connect('data/user_pdfs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_uploaded_pdfs (name, data) VALUES (?, ?)', (name, data))
    conn.commit()
    conn.close()


# ============================== MAIN APP ====================================
def process_user_mode():
    create_table()  # Ensure table exists

    # App title with gradient
    st.markdown(
        """
        <h1 style="text-align:center; color:#f63366; font-size:40px;">
        📄 AI-Powered Resume Parser <span style="color:#6366f1;">✨</span>
        </h1>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<hr style="border: 2px solid #6366f1;">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📤 **Upload your Resume (PDF format)**", type="pdf")

    if uploaded_file:
        st.success("✅ File uploaded successfully!")

        pdf_name = uploaded_file.name
        pdf_data = uploaded_file.getvalue()
        insert_pdf(pdf_name, pdf_data)

        # Extract resume data
        pdf_text = extract_resume_info_from_pdf(uploaded_file)
        resume_info = extract_resume_info(pdf_text)

        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader("🧾 Extracted Information")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**👤 First Name:** {resume_info['first_name']}")
            st.write(f"**📧 Email:** {resume_info['email']}")
            contact_number = extract_contact_number_from_resume(pdf_text)
            st.write(f"**📞 Phone:** +{contact_number}")
        with col2:
            st.write(f"**🧑‍💼 Last Name:** {resume_info['last_name']}")
            st.write(f"**🎓 Degree/Major:** {resume_info['degree_major']}")

        # ================= EDUCATION =================
        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader("🏫 Education Details")

        education_info = extract_education_from_resume(pdf_text)
        if education_info:
            st.markdown(
                "".join(f"<li style='color:#6366f1;'>{edu}</li>" for edu in education_info),
                unsafe_allow_html=True
            )
        else:
            st.warning("⚠️ No education information found.")

        # ================= SKILLS =================
        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader("💡 Key Skills Identified")
        show_colored_skills(resume_info['skills'])

        # ================= RESUME SCORE =================
        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader("📊 Resume Quality Score")

        resume_score = calculate_resume_score(resume_info)
        st.markdown(f"**⭐ Resume Score:** {resume_score}/100")

        # Modern Gradient Progress Bar
        percentage = resume_score
        color = "#4ade80" if percentage >= 75 else "#facc15" if percentage >= 50 else "#f87171"
        bar_html = f"""
        <div style="background: #e5e7eb; border-radius: 10px; height: 30px;">
            <div style="
                width: {percentage}%;
                height: 30px;
                background: linear-gradient(90deg, {color}, #6366f1);
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;">
                {percentage}%
            </div>
        </div>
        """
        st.markdown(bar_html, unsafe_allow_html=True)

        # ================= SUGGESTED SKILLS =================
        st.markdown('<hr>', unsafe_allow_html=True)
        st.subheader("🎯 AI-Suggested Skills for Desired Job Role")

        desired_job = st.text_input("💼 Enter your target job role (e.g., Backend Developer, Data Scientist):")
        if desired_job:
            suggested_skills = suggest_skills_for_job(desired_job)
            if suggested_skills:
                st.success(f"🌟 **Recommended Skills for {desired_job}:**")
                st.markdown(
                    "".join(f"<li style='color:#22c55e;'>{skill}</li>" for skill in suggested_skills),
                    unsafe_allow_html=True
                )
            else:
                st.warning("⚠️ No suggested skills found for that role. Try another title.")

        # ================= FOOTER =================
        st.markdown('<hr style="border: 1px solid #ddd;">', unsafe_allow_html=True)
        st.markdown(
            """
            <p style="text-align:center; color:#6b7280;">
            🚀 Built with ❤️ using <b>Streamlit</b> and <b>spaCy NLP</b>
            </p>
            """,
            unsafe_allow_html=True
        )


# ============================== ENTRY POINT ==============================
if __name__ == '__main__':
    process_user_mode()
