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

css_path = os.path.join("images", "style.css")
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

def is_valid_name(name):
    return name.replace(" ", "").isalpha()

def is_valid_roll(roll):
    return roll.isdigit() and int(roll) > 0

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
    logo_path = os.path.join("images", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)
    st.title("🏫 Welcome to Student Result Management System")
    st.write("Manage students, record marks, and generate result reports easily!")

# --------------------------
# Add Student Page
# --------------------------
elif page == "Add Student":
    add_img_path = os.path.join("images", "add.png")
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
            if not is_valid_name(name):
                st.error("❌ Invalid Name! Name must contain only alphabets and spaces.")
            elif name.strip() == "":
                st.error("❌ Name cannot be empty.")
            elif not is_valid_roll(roll):
                st.error("❌ Invalid Roll Number! Roll number must be a positive integer.")
            else:
                obtained_total = sum(marks.values())
                max_total = sum(SUBJECTS.values())
                percentage = round((obtained_total / max_total) * 100, 2)
                grade = calculate_grade(percentage)

                student_data = {
                    "Name": name,
                    "Roll No": int(roll),
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
    results_img_path = os.path.join("images", "results.png")
    student_icon_path = os.path.join("images", "student_icon.png")

    if os.path.exists(results_img_path):
        st.image(results_img_path, width=100)

    # Session info at top-left
    st.markdown("<h4 style='text-align:left;'>Session: 2025</h4>", unsafe_allow_html=True)

    # Clear all records button
    if st.button("🗑️ Clear All Records"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
            st.success("✅ All old student records have been deleted!")
        else:
            st.info("ℹ️ No records found to delete.")

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
        for _, row in df.iterrows():
            st.subheader(f"📌 {row['Name']} (Roll No: {row['Roll No']})")
            if os.path.exists(student_icon_path):
                st.image(student_icon_path, width=80)

            student_rows = []
            total_obtained = 0
            total_max = 0
            for subject, max_marks in SUBJECTS.items():
                obtained = row[subject]
                total_obtained += obtained
                total_max += max_marks
                percentage = round((obtained / max_marks) * 100, 2)
                grade = calculate_grade(percentage)
                student_rows.append({
                    "Subject": subject,
                    "Marks": obtained,
                    "Total Marks": f"{obtained}/{max_marks}",
                    "Percentage": f"{percentage}%",
                    "Grade": grade
                })

            df_student = pd.DataFrame(student_rows)

            # Add overall row
            overall_percentage = round((total_obtained / total_max) * 100, 2)
            overall_grade = calculate_grade(overall_percentage)
            df_overall = pd.DataFrame([{
                "Subject": "Overall",
                "Marks": total_obtained,
                "Total Marks": f"{total_obtained}/{total_max}",
                "Percentage": f"{overall_percentage}%",
                "Grade": overall_grade
            }])

            df_final = pd.concat([df_student, df_overall], ignore_index=True)

            # --------------------------
            # Display dark table with black bold text in columns
            # --------------------------
            st.markdown(
                df_final.to_html(index=False, escape=False),
                unsafe_allow_html=True
            )
            st.markdown("""
                <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    background-color: #2b2b2b;
                }
                th {
                    background-color: #1f1f1f;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }
                td {
                    background-color: #ffffff;
                    color: #000000;
                    font-weight: bold;
                    padding: 8px;
                    text-align: center;
                }
                tr:nth-child(even) td {
                    background-color: #f0f0f0;
                }
                tr:hover td {
                    background-color: #dcdcdc;
                }
                </style>
            """, unsafe_allow_html=True)

    else:
        st.info("ℹ️ No students added yet. Please go to 'Add Student' or upload data.")

# --------------------------
# About Page
# --------------------------
elif page == "About":
    about_img_path = os.path.join("images", "about.png")
    if os.path.exists(about_img_path):
        st.image(about_img_path, width=100)
    st.header("ℹ️ About")
    st.write("This Student Result Management App is built with **Streamlit**.")
    st.write("Developed to manage marks, calculate grades, and display results in a clean format.")
