import os
import csv
import pandas as pd
import streamlit as st

# =========================
# Subjects List
# =========================
SUBJECTS = ["Physics", "Chemistry", "Math", "English", "Computer"]

# =========================
# Grading Function
# =========================
def get_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B+"
    elif percentage >= 60:
        return "B"
    elif percentage >= 50:
        return "C"
    elif percentage >= 40:
        return "D"
    else:
        return "Fail"

# =========================
# Utility function to load CSS
# =========================
def load_css(file_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(file_path):
        with open(file_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load custom CSS
load_css("assets/style.css")

# =========================
# Sidebar Menu
# =========================
st.sidebar.image("logo.png", use_column_width=True)
st.sidebar.title("🎓 Menu")
menu = st.sidebar.radio("Go to", ["Home", "Add Student", "Results", "About"])

# =========================
# Session State Storage
# =========================
if "students" not in st.session_state:
    st.session_state["students"] = []

# =========================
# Pages
# =========================

# --- Home Page ---
if menu == "Home":
    st.title("🏫 Welcome to Student Result App")
    st.write(
        """
        This app helps you manage student records.  
        👉 You can:
        - Add students manually  
        - Upload CSV/Excel files with student data  
        - View results with **Grades, Percentage, and Total Marks**  
        """
    )

# --- Add Student Page ---
elif menu == "Add Student":
    st.title("➕ Add Student")

    with st.form("student_form"):
        name = st.text_input("Student Name")
        roll = st.text_input("Roll Number")

        marks = {}
        for subject in SUBJECTS:
            marks[subject] = st.number_input(
                f"{subject} Marks", min_value=0, max_value=100, step=1, key=f"{subject}_{roll}"
            )

        submitted = st.form_submit_button("Add Student")

        if submitted:
            if name and roll:
                total = sum(marks.values())
                percentage = (total / (len(SUBJECTS) * 100)) * 100
                grade = get_grade(percentage)

                student_data = {
                    "Name": name,
                    "Roll": roll,
                    **marks,
                    "Total": total,
                    "Percentage": round(percentage, 2),
                    "Grade": grade,
                }
                st.session_state["students"].append(student_data)
                st.success(f"✅ {name} added successfully!")
            else:
                st.error("⚠️ Please fill all fields before adding")

    if st.session_state["students"]:
        st.subheader("📋 Current Students")
        st.dataframe(pd.DataFrame(st.session_state["students"]))

# --- Results Page ---
elif menu == "Results":
    st.title("📊 All Students Results")

    uploaded_file = st.file_uploader(
        "📂 Upload Student Data (CSV/Excel)", type=["csv", "xlsx"]
    )

    df_uploaded = None
    if uploaded_file is not None:
        try:
            uploaded_file.seek(0)

            if uploaded_file.name.endswith(".csv"):
                try:
                    # Auto-detect delimiter
                    sample = uploaded_file.read(2048).decode("utf-8", errors="ignore")
                    uploaded_file.seek(0)
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                    df_uploaded = pd.read_csv(uploaded_file, delimiter=delimiter)
                except Exception:
                    uploaded_file.seek(0)
                    df_uploaded = pd.read_csv(uploaded_file)  # fallback

            elif uploaded_file.name.endswith(".xlsx"):
                df_uploaded = pd.read_excel(uploaded_file)

            if df_uploaded is not None:
                # Ensure proper columns
                if all(sub in df_uploaded.columns for sub in SUBJECTS):
                    df_uploaded["Total"] = df_uploaded[SUBJECTS].sum(axis=1)
                    df_uploaded["Percentage"] = (
                        df_uploaded["Total"] / (len(SUBJECTS) * 100) * 100
                    ).round(2)
                    df_uploaded["Grade"] = df_uploaded["Percentage"].apply(get_grade)

                st.success("✅ File uploaded successfully!")
                st.dataframe(df_uploaded)

        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

    elif st.session_state["students"]:
        st.success("📋 Showing manually added students")
        st.dataframe(pd.DataFrame(st.session_state["students"]))
    else:
        st.info("📌 No students added yet. Please add students or upload a file.")

# --- About Page ---
elif menu == "About":
    st.title("ℹ️ About")
    st.write(
        """
        This Student Result Management App was built using **Streamlit**.  
        Features:
        - Add students manually  
        - Upload results via CSV or Excel  
        - Calculates **Total Marks, Percentage, and Grade**  

        👨‍💻 Developed by Muhammad
        """
    )
