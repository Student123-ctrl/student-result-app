import streamlit as st
import pandas as pd
import os

# --------------------------
# Helper: safe image loader
# --------------------------
def safe_image(path, **kwargs):
    if os.path.exists(path):
        st.image(path, **kwargs)
    else:
        st.warning(f"⚠️ Image not found: {path}")

# --------------------------
# Load custom CSS
# --------------------------
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css(os.path.join("assets", "style.css"))

# --------------------------
# Sidebar Navigation
# --------------------------
st.sidebar.title("🎓 Menu")
page = st.sidebar.radio("Go to", ["Home", "Add Student", "Results", "About"])

# --------------------------
# Utility functions
# --------------------------
def calculate_grade(percentage):
    if percentage >= 90:
        return "A+"
    elif percentage >= 80:
        return "A"
    elif percentage >= 70:
        return "B"
    elif percentage >= 60:
        return "C"
    else:
        return "F"

# Subjects and max marks
SUBJECTS = {
    "Physics": 100,
    "Math": 100,
    "Chemistry": 100,
    "English": 100,
    "Computer": 100
}

DATA_FILE = os.path.join("data", "students.csv")
os.makedirs("data", exist_ok=True)

# --------------------------
# Home Page
# --------------------------
if page == "Home":
    safe_image(os.path.join("images", "home.png"), width=100)
    st.title("🏫 Welcome to Student Result Management System")
    st.write("Manage students, record marks, and generate result reports easily!")

# --------------------------
# Add Student Page
# --------------------------
elif page == "Add Student":
    safe_image(os.path.join("images", "add.png"), width=100)
    st.header("➕ Add New Student")

    with st.form("student_form"):
        name = st.text_input("Student Name")
        roll = st.text_input("Roll Number")
        marks = {}
        for subject, max_marks in SUBJECTS.items():
            marks[subject] = st.number_input(
                f"{subject} Marks (out of {max_marks})", min_value=0, max_value=max_marks
            )

        submitted = st.form_submit_button("Add Student")

        if submitted:
            obtained_total = sum(marks.values())
            max_total = sum(SUBJECTS.values())
            percentage = round((obtained_total / max_total) * 100, 2)
            grade = calculate_grade(percentage)

            student_data = {
                "Name": name,
                "Roll No": roll,
                **marks,
                "Total Obtained": obtained_total,
                "Total Marks": max_total,
                "Percentage": percentage,
                "Grade": grade
            }

            df_new = pd.DataFrame([student_data])

            if os.path.exists(DATA_FILE):
                df_old = pd.read_csv(DATA_FILE)
                df = pd.concat([df_old, df_new], ignore_index=True)
            else:
                df = df_new

            df.to_csv(DATA_FILE, index=False)
            st.success(f"✅ Student {name} added successfully!")

# --------------------------
# Results Page
# --------------------------
elif page == "Results":
    st.header("📊 All Students Results")
    uploaded_file = st.file_uploader("📂 Upload Student Data (CSV/Excel)", type=["csv","xlsx"])

    df = None
    if uploaded_file:
        try:
            uploaded_file.seek(0)
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            st.success("✅ File uploaded successfully!")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
    elif os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

    if df is not None and not df.empty:
        for _, student in df.iterrows():
            st.subheader(f"🧑 {student['Name']}")
            safe_image(os.path.join("images", "student_icon.png"), width=80)

            rows = []
            total_obtained = 0
            total_max = 0
            for subject, max_marks in SUBJECTS.items():
                obtained = student[subject]
                total_obtained += obtained
                total_max += max_marks
                perc = round((obtained / max_marks) * 100, 2)
                grade = calculate_grade(perc)
                rows.append({
                    "Subject": subject,
                    "Marks Obtained": str(obtained),
                    "Total Marks": f"{obtained}/{max_marks}",
                    "Percentage": f"{perc}%",
                    "Grade": grade
                })

            # Overall row
            overall_percentage = round((total_obtained / total_max) * 100, 2)
            overall_grade = calculate_grade(overall_percentage)
            rows.append({
                "Subject": "Overall",
                "Marks Obtained": str(total_obtained),
                "Total Marks": f"{total_obtained}/{total_max}",
                "Percentage": f"{overall_percentage}%",
                "Grade": overall_grade
            })

            df_results = pd.DataFrame(rows).astype(str)
            st.dataframe(df_results, use_container_width=True)

    else:
        st.info("ℹ️ No students added yet. Please go to 'Add Student' or upload data.")

# --------------------------
# About Page
# --------------------------
elif page == "About":
    safe_image(os.path.join("images", "about.png"), width=100)
    st.header("ℹ️ About")
    st.write("This Student Result Management App is built with **Streamlit**.")
    st.write("Developed to manage marks, calculate grades, and display results in a clean format.")
