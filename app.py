import streamlit as st
from uuid import uuid4
import pandas as pd
from io import BytesIO
import os

# ---------------------------
# App Config
# ---------------------------
st.set_page_config(page_title="Student Result Management", page_icon="🎓", layout="centered")

# ---------------------------
# Load CSS safely
# ---------------------------
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {file_name}")

load_css("assets/style.css")

# ---------------------------
# Assets
# ---------------------------
LOGO_URL = "logo.png"               # local logo
STUDENT_ICON = "assets/student_icon.png"  # student icon

# ---------------------------
# Sidebar
# ---------------------------
if os.path.exists(LOGO_URL):
    st.sidebar.image(LOGO_URL, width=120)
st.sidebar.title("🎓 Menu")
page = st.sidebar.radio("Go to", ["Home", "Add Student", "Results", "About"])

# ---------------------------
# Subjects & Grade Function
# ---------------------------
subjects = ["Physics", "Computer", "Math", "English", "Chemistry"]

def get_grade(percentage: float) -> str:
    if percentage > 90:
        return "A+"
    elif percentage > 81:
        return "A"
    elif percentage >= 71:
        return "B+"
    elif percentage >= 61:
        return "B"
    elif percentage >= 51:
        return "C+"
    elif percentage >= 41:
        return "C"
    elif percentage >= 31:
        return "D+"
    elif percentage >= 21:
        return "E+"
    else:
        return "Fail"

# ---------------------------
# Session Storage
# ---------------------------
if "students" not in st.session_state:
    st.session_state.students = {}

# ---------------------------
# Pages
# ---------------------------
if page == "Home":
    st.image(LOGO_URL, width=120)
    st.title("Welcome to Student Result Management")
    st.markdown(
        """
        ✅ Add unlimited students  
        ✅ Validate marks (0–100)  
        ✅ Calculate percentage & grades  
        ✅ View results in expandable cards  
        ✅ Download all results as Excel  
        ✅ Upload CSV/Excel to import students
        """
    )

elif page == "Add Student":
    st.header("➕ Add Student Marks")
    form_id = uuid4().hex[:8]

    with st.form(f"student_form_{form_id}", clear_on_submit=True):
        name = st.text_input("Student Name", key=f"name_{form_id}")
        marks_inputs = {}
        for subject in subjects:
            marks = st.number_input(
                f"{subject} marks (0–100)",
                min_value=-10000, max_value=10000, step=1,
                key=f"{form_id}_{subject}"
            )
            marks_inputs[subject] = marks

        submitted = st.form_submit_button("Add Student")

        if submitted:
            if not name.strip():
                st.error("❌ Please enter the student's name.")
            else:
                invalid = [s for s, m in marks_inputs.items() if m < 0 or m > 100]
                if invalid:
                    details = ", ".join(f"{s} ({marks_inputs[s]})" for s in invalid)
                    st.error(f"❌ Marks must be between 0 and 100. Problem with: {details}")
                else:
                    # Save student into session_state
                    st.session_state.students[name.strip()] = {s: int(m) for s, m in marks_inputs.items()}
                    st.success(f"✅ {name.strip()} added successfully!")

elif page == "Results":
    st.header("📊 All Students Results")

    # Optional: Upload CSV/Excel
    uploaded_file = st.file_uploader("📂 Upload Student Data (CSV/Excel)", type=["csv","xlsx"])
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df_uploaded = pd.read_csv(uploaded_file)
        else:
            df_uploaded = pd.read_excel(uploaded_file)
        st.subheader("Uploaded Student Data")
        st.dataframe(df_uploaded)

        # Import into session state
        for i, row in df_uploaded.iterrows():
            name = row["Name"]
            st.session_state.students[name] = {sub: int(row[sub]) for sub in subjects}

    if not st.session_state.students:
        st.info("No students added yet. Go to 'Add Student' first or upload data.")
    else:
        results_data = []
        for name, marks_dict in st.session_state.students.items():
            total_possible = len(subjects) * 100
            total = sum(marks_dict.values())
            percentage = (total / total_possible) * 100
            grade = get_grade(percentage)

            with st.expander(f"{name} — {percentage:.2f}% — {grade}"):
                st.markdown(f'<div class="result-card">', unsafe_allow_html=True)
                if os.path.exists(STUDENT_ICON):
                    st.image(STUDENT_ICON, width=60)
                st.write(f"**Total:** {total}/{total_possible}")
                st.write(f"**Percentage:** {percentage:.2f}%")
                st.write(f"**Grade:** {grade}")
                st.markdown("**Subject-wise marks:**")
                for subject, marks in marks_dict.items():
                    st.write(f"- {subject}: {marks}")
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("---")

            # Add to export
            row = {"Name": name, "Total": total, "Percentage": round(percentage,2), "Grade": grade}
            row.update(marks_dict)
            results_data.append(row)

        # Export to Excel
        df_export = pd.DataFrame(results_data)
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_export.to_excel(writer, index=False, sheet_name="Results")

        st.download_button(
            label="📥 Download Results as Excel",
            data=buffer,
            file_name="Student_Results.xlsx",
            mime="application/vnd.ms-excel"
        )

elif page == "About":
    st.header("ℹ️ About This App")
    st.markdown(
        """
        This Student Result Management System was built with **Streamlit**.  

        ✅ Unlimited students can be added  
        ✅ Marks validated (0–100)  
        ✅ Results shown with percentages & grades  
        ✅ Excel export for all students  
        ✅ CSV/Excel import supported  
        ✅ Blue-themed sidebar & custom CSS  

        🎓 *Perfect for schools, colleges, or practice projects.*
        """
    )