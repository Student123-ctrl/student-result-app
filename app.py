import streamlit as st
import pandas as pd
import os

# --------------------------
# Load custom CSS
# --------------------------
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

css_path = os.path.join("assets", "style.css")
load_css(css_path)

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
    home_img_path = os.path.join("assets", "home.png")
    if os.path.exists(home_img_path):
        st.image(home_img_path, width=100)
    st.title("🏫 Welcome to Student Result Management System")
    st.write("Manage students, record marks, and generate result reports easily!")

# --------------------------
# Add Student Page
# --------------------------
elif page == "Add Student":
    add_img_path = os.path.join("assets", "add.png")
    if os.path.exists(add_img_path):
        st.image(add_img_path, width=100)
    st.header("➕ Add New Student")

    with st.form("student_form"):
        name = st.text_input("Student Name")
        roll = st.text_input("Roll Number")
        marks = {}
        for subject, max_marks in SUBJECTS.items():
            marks[subject] = st.number_input(f"{subject} Marks (out of {max_marks})", min_value=0, max_value=max_marks)

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
    results_img_path = os.path.join("assets", "results.png")
    student_icon_path = os.path.join("assets", "student_icon.png")

    if os.path.exists(results_img_path):
        st.image(results_img_path, width=100)
    st.header("📊 All Students Results")

    # Clear all records button
    if st.button("🗑️ Clear All Records"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("✅ All old student records have been deleted!")
        else:
            st.info("ℹ️ No records found to delete.")

    if os.path.exists(student_icon_path):
        st.image(student_icon_path, width=80)

    uploaded_file = st.file_uploader("📂 Upload Student Data (CSV/Excel)", type=["csv", "xlsx"])
    df = None

    if uploaded_file is not None:
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
        # Display name at top
        st.subheader(f"Student Records ({len(df)} students)")

        # Reshape data: one row per subject
        rows = []
        total_obtained = 0
        total_max = 0
        for _, row in df.iterrows():
            for subject, max_marks in SUBJECTS.items():
                obtained = row[subject]
                total_obtained += obtained
                total_max += max_marks
                percentage = round((obtained / max_marks) * 100, 2)
                grade = calculate_grade(percentage)
                rows.append({
                    "Name": row["Name"],
                    "Roll No": row["Roll No"],
                    "Subject": subject,
                    "Marks": obtained,
                    "Total Marks": f"{obtained}/{max_marks}",
                    "Percentage": f"{percentage}%",
                    "Grade": grade
                })

        df_results = pd.DataFrame(rows)

        # Add overall summary at the end
        overall_percentage = round((total_obtained / total_max) * 100, 2)
        overall_grade = calculate_grade(overall_percentage)
        df_overall = pd.DataFrame([{
            "Name": "Overall",
            "Roll No": "",
            "Subject": "",
            "Marks": total_obtained,
            "Total Marks": f"{total_obtained}/{total_max}",
            "Percentage": f"{overall_percentage}%",
            "Grade": overall_grade
        }])

        df_final = pd.concat([df_results, df_overall], ignore_index=True)

        st.dataframe(df_final, use_container_width=True)
    else:
        st.info("ℹ️ No students added yet. Please go to 'Add Student' or upload data.")

# --------------------------
# About Page
# --------------------------
elif page == "About":
    about_img_path = os.path.join("assets", "about.png")
    if os.path.exists(about_img_path):
        st.image(about_img_path, width=100)
    st.header("ℹ️ About")
    st.write("This Student Result Management App is built with **Streamlit**.")
    st.write("Developed to manage marks, calculate grades, and display results in a clean format.")
