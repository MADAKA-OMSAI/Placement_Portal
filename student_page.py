import streamlit as st
import json
import os
import hashlib
import smtplib
from email.message import EmailMessage
import base64
from dotenv import load_dotenv
import base64


load_dotenv()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_confirmation_email(to_email, student_name):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    msg = EmailMessage()
    msg['Subject'] = "🎓 Registration Successful - Placement Portal"
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(f"""
Hi {student_name},

✅ You have successfully registered on the Placement Cell Management System.

You can now log in using your credentials and start applying to companies that match your profile.

Best wishes,  
Placement Team
""")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.warning(f"Email not sent: {e}")
        return False

def send_application_email(to_email, student_name, company_name, role):
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    msg = EmailMessage()
    msg['Subject'] = f"📩 Application Submitted - {company_name}"
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg.set_content(f"""
Hi {student_name},

✅ You have successfully applied to **{company_name}** for the role of **{role}**.

We wish you the best for the recruitment process!

Regards,  
Placement Cell Team
""")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.warning(f"Email not sent for application: {e}")
        return False

def register_student():
    st.subheader("📝 Student Registration")
    name = st.text_input("Name", key="reg_name")
    student_id = st.text_input("Student ID", key="reg_id")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_pass")
    cgpa = st.text_input("CGPA", key="reg_cgpa")
    branch = st.selectbox("Branch", ["CSE", "ECE", "MECH", "CIVIL", "EEE"], key="reg_branch")
    profile_pic = st.file_uploader("Upload Profile Picture (jpg/png)", type=["jpg", "png"], key="reg_pic")

    if st.button("Register", key="reg_submit"):
        if not all([name, student_id, email, password, cgpa, branch]):
            st.error("Please fill in all fields")
            return

        file_path = "students.json"
        students = []
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    students = json.load(f)
                except:
                    students = []

            if any(s.get("student_id") == student_id or s.get("email") == email for s in students):
                st.error("Student with this ID or Email already exists!")
                return

        pic_path = None
        if profile_pic:
            os.makedirs("profile_pics", exist_ok=True)
            pic_path = f"profile_pics/{student_id}.png"
            with open(pic_path, "wb") as f:
                f.write(profile_pic.read())

        student_data = {
            "name": name,
            "student_id": student_id,
            "email": email,
            "password": hash_password(password),
            "cgpa": cgpa,
            "branch": branch,
            "applications": [],
            "placed": False,
            "profile_pic": pic_path,
            "resume": ""
        }

        students.append(student_data)
        with open(file_path, "w") as f:
            json.dump(students, f, indent=4)

        st.success("Registration successful! Please login now.")
        if send_confirmation_email(email, name):
            st.info("📧 A confirmation email has been sent.")

def student_login():
    st.subheader("🔐 Student Login")
    student_id = st.text_input("Student ID", key="login_id")
    password = st.text_input("Password", type="password", key="login_pass")

    if st.button("Login", key="login_btn"):
        try:
            with open("students.json", "r") as f:
                students = json.load(f)

            for student in students:
                if (
                    student.get("student_id") == student_id and
                    student.get("password") == hash_password(password)
                ):
                    st.session_state["student"] = student
                    st.success("Login successful!")
                    st.experimental_rerun()
                    return
            st.error("Invalid Student ID or Password.")
        except FileNotFoundError:
            st.error("No students registered yet.")
        except json.JSONDecodeError:
            st.error("Student data corrupted. Please check the JSON file.")

def apply_to_company(student_id, company_name):
    with open("students.json", "r") as f:
        students = json.load(f)

    with open("companies.json", "r") as f:
        companies = json.load(f)

    student = next((s for s in students if s.get("student_id") == student_id), None)
    company = next((c for c in companies if c.get("name") == company_name), None)

    if student and company:
        if company_name not in student.get("applications", []):
            student["applications"].append(company_name)

            with open("students.json", "w") as f:
                json.dump(students, f, indent=4)

            send_application_email(
                to_email=student["email"],
                student_name=student["name"],
                company_name=company["name"],
                role=company.get("role", "N/A")
            )

            return student

def get_eligible_company_count(student, return_list=False):
    try:
        with open("companies.json", "r") as f:
            companies = json.load(f)

        student_cgpa = float(student.get("cgpa", 0))
        student_branch = student.get("branch", "").strip().upper()

        eligible = []
        for c in companies:
            try:
                min_cgpa = float(c.get("min_cgpa", 0))
                departments = [d.strip().upper() for d in c.get("eligible_departments", [])]
                if student_cgpa >= min_cgpa and student_branch in departments:
                    eligible.append(c)
            except:
                continue

        return eligible if return_list else len(eligible)
    except:
        return [] if return_list else 0

import os
import json
import base64
import streamlit as st

def upload_resume(student):
    st.subheader("📄 Upload / View Resume")

    if "student_id" not in student:
        st.error("⚠️ Invalid student session. Please re-login.")
        return

    resume_path = student.get("resume", "")
    uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"], key="resume_uploader")

    if uploaded_file:
        resume_dir = "resumes"
        os.makedirs(resume_dir, exist_ok=True)

        filename = f"{student['student_id']}_{uploaded_file.name.replace(' ', '_')}"
        saved_path = os.path.join(resume_dir, filename)

        with open(saved_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Update student resume path in students.json
        with open("students.json", "r") as f:
            students = json.load(f)

        for s in students:
            if s["student_id"] == student["student_id"]:
                s["resume"] = saved_path
                student = s
                break

        with open("students.json", "w") as f:
            json.dump(students, f, indent=4)

        st.session_state["student"] = student
        st.success("✅ Resume uploaded successfully!")
        resume_path = saved_path  # Update the local variable

    # Show and download section
    if resume_path and os.path.exists(resume_path):
        show_resume = st.button("👁️ Show Resume")
        if show_resume:
            with open(resume_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

        with open(resume_path, "rb") as f:
            st.download_button(
                label="📥 Download Resume",
                data=f,
                file_name=os.path.basename(resume_path),
                mime="application/pdf"
            )
    else:
        st.info("ℹ️ No resume uploaded yet.")

import streamlit as st
import os
import json
import base64

def student_dashboard(student):
    student_id = student.get("student_id")
    st.title(f"👋 Welcome, {student.get('name', 'Student')}")

    if student.get("profile_pic") and os.path.exists(student["profile_pic"]):
        with open(student["profile_pic"], "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(f"""
        <div style='text-align: center;'>
            <img src="data:image/png;base64,{encoded}" 
                 style='width: 150px; height: 150px; object-fit: cover; border-radius: 50%; border: 3px solid #3399ff; margin-bottom: 10px;'/>
        </div>
        """, unsafe_allow_html=True)
    

    st.markdown(f"<p style='text-align:center;'><strong>Branch:</strong> {student.get('branch')} | <strong>CGPA:</strong> {student.get('cgpa')}</p>", unsafe_allow_html=True)
    
    # View session init
    if "student_view" not in st.session_state:
        st.session_state.student_view = None

    # Determine update count
    update_count = 0
    if student.get("selected_company"):
        update_count += 1
    if student.get("shortlists"):
        for rounds in student["shortlists"].values():
            if any(rounds.values()):
                update_count += 1
                break

    st.markdown("## 📌 Dashboard")
    # First row
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Analytics"):
            st.session_state.student_view = "analytics"
        if st.button("🏢 Available Companies"):
            st.session_state.student_view = "companies"
    with col2:
        if st.button("📁 Applications"):
            st.session_state.student_view = "applications"
        if st.button("✏️ Edit Profile"):
            st.session_state.student_view = "edit_profile"

    # Second row for Resume and Updates
        # Second row for Resume, Updates, Notifications
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📄 Resume"):
            st.session_state.student_view = "upload_resume"
        if st.button("🔔 Notifications"):
            st.session_state.student_view = "notifications"
    with col4:
        if st.button("📣 Updates"):
            st.session_state.student_view = "updates"
    col5,col6=st.columns(2)
    with col5:
        if st.button("📬 Queries"):
            st.session_state.student_view = "queries"
    with col6:
        if st.button("📥 Responses"):
            st.session_state.student_view = "responses"

        


    # Conditional view rendering
    if st.session_state.student_view == "analytics":
        st.subheader("📊 My Analytics")
        st.write(f"**Eligible Companies:** {get_eligible_company_count(student)}")
        st.write(f"**Applications Submitted:** {len(student.get('applications', []))}")

    elif st.session_state.student_view == "companies":
        st.subheader("🏢 Eligible Companies")
        eligible_companies = get_eligible_company_count(student, return_list=True)

        search_query = st.text_input("🔍 Search by company name or role")
        min_package = st.slider("💰 Minimum Package (LPA)", 0, 50, 0)

        for comp in eligible_companies:
            if ((search_query.lower() in comp["name"].lower() or search_query.lower() in comp["role"].lower()) and
                    float(comp.get("package", 0)) >= min_package):
                st.markdown(f"**{comp['name']}**  \nRole: {comp['role']}  \nPackage: ₹{comp['package']} LPA")
                if comp["name"] not in student.get("applications", []):
                    if st.button(f"Apply to {comp['name']}", key=f"apply_{comp['name']}"):
                        updated_student = apply_to_company(student["student_id"], comp["name"])
                        if updated_student:
                            st.session_state["student"] = updated_student
                            st.success(f"✅ Successfully applied to {comp['name']}")
                            st.session_state.student_view = "companies"
                            st.experimental_rerun()
                else:
                    st.info("Already Applied")

    elif st.session_state.student_view == "upload_resume":
        upload_resume(student)

    elif st.session_state.student_view == "applications":
        st.subheader("📁 Your Applications")
        try:
            with open("companies.json", "r") as f:
                companies = json.load(f)
            applied_companies = [c for c in companies if c.get("name") in student.get("applications", [])]
            for comp in applied_companies:
                st.markdown(f"✅ **{comp['name']}** - {comp['role']} - ₹{comp['package']} LPA")
        except:
            st.warning("⚠️ Could not load application data.")

    elif st.session_state.student_view == "edit_profile":
        st.subheader("✏️ Edit Profile")
        updated_name = st.text_input("Name", value=student.get("name", ""))
        updated_email = st.text_input("Email", value=student.get("email", ""))
        updated_cgpa = st.text_input("CGPA", value=student.get("cgpa", ""))
        updated_branch = st.selectbox("Branch", ["CSE", "ECE", "EEE", "MECH", "CIVIL"],
                                      index=["CSE", "ECE", "EEE", "MECH", "CIVIL"].index(student.get("branch", "CSE")))
        uploaded_file = st.file_uploader("📸 Upload New Profile Picture", type=["png", "jpg", "jpeg"])

        if st.button("💾 Save Changes"):
            with open("students.json", "r") as f:
                students = json.load(f)

            for s in students:
                if s.get("student_id") == student["student_id"]:
                    s["name"] = updated_name
                    s["email"] = updated_email
                    s["cgpa"] = updated_cgpa
                    s["branch"] = updated_branch
                    if uploaded_file:
                        pic_path = f"profile_pics/{student['student_id']}.png"
                        with open(pic_path, "wb") as f_img:
                            f_img.write(uploaded_file.read())
                        s["profile_pic"] = pic_path
                    st.session_state["student"] = s
                    break

            with open("students.json", "w") as f:
                json.dump(students, f, indent=4)

            st.success("Profile updated successfully!")
            st.experimental_rerun()

    elif st.session_state.student_view == "updates":
        st.subheader("📣 Updates")
        has_updates = False

        if student.get("selected_company"):
            st.success(f"🎉 Congratulations! You have been selected by **{student['selected_company']}**.")
            has_updates = True

        if student.get("shortlists"):
            for comp_key, rounds in student["shortlists"].items():
                comp_name = comp_key.replace("_", " ").title()
                cleared_rounds = [r for r, status in rounds.items() if status]
                if cleared_rounds:
                    st.info(f"✅ You cleared {', '.join(cleared_rounds)} for **{comp_name}**.")
                    has_updates = True

        if not has_updates:
            st.write("No new updates at the moment.")
    elif st.session_state.student_view == "notifications":
        show_notifications()
    elif st.session_state.student_view == "responses":
        view_admin_responses(student_id)

    
    elif st.session_state.student_view == "queries":
        st.subheader("📬 Submit a Query to Admin")

        subject = st.text_input("Subject", key="query_subject")
        message = st.text_area("Message", key="query_message")

        if st.button("📤 Submit Query"):
            if subject and message:
                submit_query(student['name'], student['student_id'], subject, message)
                st.success("✅ Your query has been submitted!")
            else:
                st.warning("⚠️ Please fill out both the subject and message.")

NOTIFICATIONS_FILE = 'notifications.json'

def load_notifications():
    if os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, 'r') as file:
            return json.load(file)
    return []

def show_notifications():
    st.subheader("📢 Notifications")
    notifications = load_notifications()

    if not notifications:
        st.info("No notifications available.")
        return

    for notif in notifications:
        with st.container():
            st.markdown(
                f"""
                <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                    <h5>📌 {notif['company_name']} - {notif['role']}</h5>
                    <p><strong>Round:</strong> {notif['round']}</p>
                    <p><strong>Venue:</strong> {notif['venue']}</p>
                    <p><strong>Time:</strong> {notif['time']}</p>
                    <p><strong>Description:</strong> {notif['description']}</p>
                    {"<p><strong>Meeting Link:</strong> <a href='" + notif["meeting_link"] + "' target='_blank'>" + notif["meeting_link"] + "</a></p>" if notif["meeting_link"] else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
import os
import json
from datetime import datetime

QUERIES_FILE = "queries.json"
RESPONSES_FILE = "responses.json"

# --------- Helper Functions ---------
def load_queries():
    if not os.path.exists(QUERIES_FILE):
        return []
    with open(QUERIES_FILE, "r") as f:
        return json.load(f)

def save_queries(queries):
    with open(QUERIES_FILE, "w") as f:
        json.dump(queries, f, indent=4)

def load_responses():
    if not os.path.exists(RESPONSES_FILE):
        return []
    with open(RESPONSES_FILE, "r") as f:
        return json.load(f)

def submit_query(student_name, student_id, subject, message):
    queries = load_queries()
    query = {
        "student_name": student_name,
        "student_id": student_id,
        "subject": subject,
        "message": message,
        "timestamp": str(datetime.now())
    }
    queries.append(query)
    save_queries(queries)

# --------- Student UI ---------
def student_query_section(student_name, student_id):
    st.subheader("📬 Submit a Query to Admin")

    subject = st.text_input("Subject")
    message = st.text_area("Message")

    if st.button("Submit Query"):
        if subject and message:
            query = {
                "student_name": student_name,
                "student_id": student_id,
                "subject": subject,
                "message": message,
                "date": str(datetime.now())
            }
            queries = []
            if os.path.exists("queries.json"):
                with open("queries.json", "r") as f:
                    queries = json.load(f)

            queries.append(query)

            with open("queries.json", "w") as f:
                json.dump(queries, f, indent=4)

            st.success("✅ Your query has been submitted!")
        else:
            st.warning("Please fill in both subject and message.")
import streamlit as st
import os
import json

import streamlit as st
import os
import json

def view_admin_responses(student_id):
    st.subheader("📥 Responses from Admin")

    file_path = "responses.json"  

    if not os.path.exists(file_path):
        st.info("No response file found.")
        return

    try:
        with open(file_path, "r") as f:
            responses = json.load(f)
    except json.JSONDecodeError:
        st.error("Error reading the responses file.")
        return

    # Filter for this student's responses
    student_responses = [r for r in responses if r.get("student_id") == student_id]

    if student_responses:
        for r in student_responses:
            with st.expander(f"📨 Query: {r.get('original_query', 'No query')}"):
                st.markdown(f"**Response:** {r.get('response', 'No response provided')}")
                st.markdown(f"📅 **Responded on:** {r.get('response_date', 'No date')}")
    else:
        st.info("No responses from admin yet.")
import streamlit as st
import os
import json
import hashlib

# File path for storing student data
STUDENTS_FILE = "students.json"  # Make sure this path matches your project structure

# Helper: Load JSON data
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

# Helper: Save JSON data
def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

# Helper: Hash password securely
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Main Forgot Password Function
def forgot_password():
    st.title("🔐 Forgot Password")

    student_id = st.text_input("Enter your Student ID")
    new_password = st.text_input("Enter New Password", type="password")
    confirm_password = st.text_input("Confirm New Password", type="password")

    if st.button("Reset Password"):
        if not student_id or not new_password or not confirm_password:
            st.warning("⚠️ Please fill in all fields.")
            return

        if new_password != confirm_password:
            st.error("❌ Passwords do not match.")
            return

        students = load_json(STUDENTS_FILE)
        for student in students:
            if student["student_id"] == student_id:
                student["password"] = hash_password(new_password)
                save_json(STUDENTS_FILE, students)
                st.success("✅ Password reset successfully! You can now log in.")
                st.session_state.student_view = "login"
                st.experimental_rerun()
                return

        st.error("❌ Student ID not found.")

    if st.button("🔙 Back to Login"):
        st.session_state.student_view = "login"
        st.experimental_rerun()
