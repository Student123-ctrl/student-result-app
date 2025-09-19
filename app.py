import streamlit as st
import pandas as pd
import os
from PIL import Image

# --------------------------
# Load custom CSS
# --------------------------
def load_css(file_name):
    path = os.path.join("assets", file_name)
    if os.path.exists(path):
        try:
            with open(path) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"⚠️ Cannot load CSS {file_name}: {e}")

# Safe image loader
def safe_image(file_name, width=None):
    path = os.path.join("images", file_name)
    if os.path.exists(path):
        try:
            img = Image.open(path)
            st.image(img, width=width)
        except Exception as e:
            st.warning(f"⚠️ Cannot open {file_name}: {e}")
            st.text(f"[Image placeholder: {file_name}]")
    else:
        st.warning(f"⚠️ Image not found: {file_name}")
        st.text(f"[Image placeholder: {file_name}]")

# Load CSS
load_css("style.css")

# --------------------------
# Sidebar Navigation
# --------------------------
st.sidebar.title("🎓 Menu")
page = st.sidebar.radio("Go to", ["Home", "Add Student", "Results", "About"])

# --------------------------
# Utility functions
# --------------------------
def calculate_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 80: return "A"
    elif percentage >= 70: return "B"
    elif percentage >= 60: return "C"
    else: return "F"

# Subjects and max marks
SUBJECTS = {"Physics":100, "Math":100, "Chemistry":100, "English":100, "Computer":100}
DATA_FILE = os.path.join("data", "students.csv")
os.makedirs("data", exist_ok=True)

# --------------------------
# Home Page
# --------------------------
if page == "Home":
    safe_image("home.png", width=100)
    st.title("🏫 Welcome to Student Result Management System")
    st.write("Manage students, record marks, and generate result reports easily!")

# --------------------------
# Add Student Page
# --------------------------
elif page == "Add Student":
    safe_image("add.png", width=100)
    st.header("➕ Add New Student")

    with st.form("student_form"):
        name = st.text_input("Student Name")
        roll = st.text_input("Roll Number")
        marks = {subject: st.number_input(f"{subject} Marks (out of {max_marks})", min_value=0, max_value=max_marks)
                 for subject, max_marks in SUBJECTS.items()}

        submitted = st.form_submit_button("Add Student")
        if submitted:
            obtained_total = sum(marks.values())
            max_total = sum(SUBJECTS.values())
            percentage = round((obtained_total / max_total) * 100, 2)
            grade = calculate_grade(percentage)

            student_data = {"Name": name, "Roll No": roll, **marks,
                            "Total Obtained": obtained_total,
                            "Total Marks": max_total,
                            "Percentage": percentage,
                            "Grade": grade}

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

    # Load data
    df = None
    uploaded_file = st.file_uploader("📂 Upload Student Data (CSV/Excel)", type=["csv","xlsx"])
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
            safe_image("student_icon.png", width=80)

            # Prepare table
            rows = []
            total_obtained = 0
            total_marks = 0
            for subject, max_marks in SUBJECTS.items():
                obtained = student[subject]
                total_obtained += obtained
                total_marks += max_marks
                perc = round((obtained / max_marks) * 100, 2)
                grade = calculate_grade(perc)
                rows.append({"Subject": subject, 
                             "Marks Obtained": obtained,
                             "Total Marks": max_marks,
                             "Percentage": f"{perc}%",
                             "Grade": grade})

            # Add overall row
            overall_percentage = round((total_obtained / total_marks) * 100, 2)
            rows.append({"Subject": "Overall", 
                         "Marks Obtained": total_obtained,
                         "Total Marks": total_marks,
                         "Percentage": f"{overall_percentage}%",
                         "Grade": "-"})

            df_results = pd.DataFrame(rows)
            st.dataframe(df_results, use_container_width=True)

    else:
        st.info("ℹ️ No students added yet. Please go to 'Add Student' or upload data.")

# --------------------------
# About Page
# --------------------------
elif page == "About":
    safe_image("about.png", width=100)
    st.header("ℹ️ About")
    st.write("This Student Result Management App is built with **Streamlit**.")
    st.write("Developed to manage marks, calculate grades, and display results in a clean format.")
