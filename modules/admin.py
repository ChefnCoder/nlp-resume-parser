import base64
import sqlite3
import streamlit as st
import pandas as pd


# =============================== MAIN ADMIN PANEL ===============================
def process_admin_mode():
   

    st.markdown(
        """
        <h1 style="text-align:center; color:#4f46e5;">
            🛠️ Admin Control Panel
        </h1>
        <p style="text-align:center; color:gray;">
            Manage uploaded resumes, feedback, and system data 🔐
        </p>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<hr style="border: 2px solid #4f46e5;">', unsafe_allow_html=True)

    # Initialize session state
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    # ================= LOGIN LOGIC =================
    if not st.session_state["admin_logged_in"]:
        show_login_form()
    else:
        st.success("✅ Logged in as Admin")
        st.markdown('<hr style="border: 1px solid #ddd;">', unsafe_allow_html=True)

        display_uploaded_pdfs()

        st.markdown('<hr style="border: 1px solid #ddd;">', unsafe_allow_html=True)
        # display_feedback_data()


def show_login_form():
    """Login UI"""
    st.subheader("🔑 Authentication Required")
    col1, col2, col3 = st.columns([0.05, 0.9, 0.05])
    with col2:
        username = st.text_input("👤 Username:")
        password = st.text_input("🔒 Password:", type="password")

        if st.button("🚀 Login", use_container_width=True):
            if authenticate_admin(username, password):
                st.session_state["admin_logged_in"] = True
                st.experimental_rerun()  # Refresh UI and load admin dashboard
            else:
                st.error("❌ Authentication failed. Please try again.")


# =============================== AUTH FUNCTION ===============================
def authenticate_admin(username, password):
    hardcoded_username = "tanmay"
    hardcoded_password = "mait123"
    return username == hardcoded_username and password == hardcoded_password


# =============================== DB HELPERS ===============================
def get_uploaded_pdfs():
    try:
        conn = sqlite3.connect('data/user_pdfs.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM user_uploaded_pdfs")
        uploaded_pdfs = cursor.fetchall()
        conn.close()
        return uploaded_pdfs
    except sqlite3.Error as e:
        st.error(f"⚠️ Error fetching uploaded PDFs: {e}")
        return []


def get_pdf_data(pdf_id):
    try:
        conn = sqlite3.connect('data/user_pdfs.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, data FROM user_uploaded_pdfs WHERE id=?", (pdf_id,))
        pdf_data = cursor.fetchone()
        conn.close()
        return pdf_data
    except sqlite3.Error as e:
        st.error(f"⚠️ Error fetching PDF data: {e}")
        return None


def delete_selected_resumes(selected_ids):
    try:
        conn = sqlite3.connect('data/user_pdfs.db')
        cursor = conn.cursor()
        cursor.executemany("DELETE FROM user_uploaded_pdfs WHERE id=?", [(i,) for i in selected_ids])
        conn.commit()
        conn.close()
        st.success(f"🗑️ Deleted {len(selected_ids)} selected resume(s) successfully!")
    except sqlite3.Error as e:
        st.error(f"⚠️ Error deleting selected resumes: {e}")


# def delete_all_resumes():
#     try:
#         conn = sqlite3.connect('data/user_pdfs.db')
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM user_uploaded_pdfs;")
#         cursor.execute("DELETE FROM sqlite_sequence WHERE name='user_uploaded_pdfs';")
#         conn.commit()
#         conn.close()
#         st.warning("⚠️ All resumes deleted successfully!")
#     except sqlite3.Error as e:
#         st.error(f"⚠️ Error deleting all resumes: {e}")


# =============================== DISPLAY UPLOADED PDFs ===============================
def display_uploaded_pdfs():
    uploaded_pdfs = get_uploaded_pdfs()
    st.subheader("📂 Uploaded Resumes")

    if uploaded_pdfs:
        pdf_data_list = []
        for pdf_id, pdf_name in uploaded_pdfs:
            pdf_data = get_pdf_data(pdf_id)
            if pdf_data:
                pdf_b64 = base64.b64encode(pdf_data[1]).decode('utf-8')
                href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="{pdf_name}">📥 Download</a>'
                pdf_data_list.append({
                    "🆔 ID": pdf_id,
                    "📄 Resume Name": pdf_name,
                    "📎 Action": href
                })
            else:
                st.warning(f"⚠️ Could not retrieve data for {pdf_name}")

        pdf_table = pd.DataFrame(pdf_data_list)
        st.markdown(pdf_table.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Delete section
        st.markdown("---")
        st.markdown("### 🗑️ Delete Resumes")

        all_ids = [str(pdf_id) for pdf_id, _ in uploaded_pdfs]
        selected_to_delete = st.multiselect("Select resume IDs to delete:", all_ids)

        col1,col2 = st.columns(2)
        with col1:
            if st.button("🧹 Delete Selected Resumes", use_container_width=True):
                if selected_to_delete:
                    delete_selected_resumes(selected_to_delete)
                    st.experimental_rerun()
                else:
                    st.warning("⚠️ Please select at least one resume to delete.")

        with col2:
            if st.button("🔥 Delete All Resumes", use_container_width=True):
                delete_all_resumes()
                st.experimental_rerun()

    else:
        st.warning("📭 No uploaded resumes found.")


# =============================== FEEDBACK SECTION ===============================
# def display_feedback_data():
#     try:
#         feedback_data = pd.read_csv('data/feedback_data.csv')
#         latest_feedback = feedback_data.tail(10)

#         st.subheader("💬 Latest User Feedback")
#         st.dataframe(
#             latest_feedback,
#             use_container_width=True,
#             hide_index=True
#         )

#         if st.button("📜 View All Feedbacks"):
#             st.subheader("📋 All Feedback Records")
#             st.dataframe(feedback_data, use_container_width=True, hide_index=True)

#     except FileNotFoundError:
#         st.warning("⚠️ No feedback data available yet.")


# =============================== ENTRY POINT ===============================
if __name__ == "__main__":
    process_admin_mode()
