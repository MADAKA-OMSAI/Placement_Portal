import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
import os
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import hashlib
import json
from datetime import datetime, date

# Set page configuration as the first command
st.set_page_config(page_title="Placement Cell", page_icon=":guardsman:", layout="wide")

# Load environment variables from .env file
load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

# Admin credentials
ADMIN_CREDENTIALS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest()
}

# Send email about shortlisting or selection
def send_shortlist_email(to_email, student_name, company_name, role, job_id, round_name, status):
    try:
        msg = EmailMessage()
        msg["Subject"] = f"You have been {status.upper()} - {company_name} ({round_name})"
        msg["From"] = EMAIL_USER
        msg["To"] = to_email

        status_line = "shortlisted" if status == "shortlisted" else "SELECTED"
        msg.set_content(f"""
Hello {student_name},

🎉 Congratulations! You have been {status_line.upper()} for the following opportunity:

Company: {company_name}
Role: {role}
Job ID: {job_id}
Round: {round_name}
Status: {status_line.upper()}

Please stay updated for the next steps.

Best regards,  
Placement Cell
""")

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Error sending email:", e)
        return False

def load_students():
    if os.path.exists("students.json"):
        with open("students.json", "r") as file:
            return json.load(file)
    return []

def save_students(data):
    with open("students.json", "w") as file:
        json.dump(data, file, indent=4)

def load_companies():
    try:
        with open("companies.json", "r") as file:
            companies = json.load(file)
            for company in companies:
                if 'date_of_drive' in company and company['date_of_drive']:
                    company['date_of_drive'] = date.fromisoformat(company['date_of_drive'])
            return companies
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_companies(companies):
    for company in companies:
        if isinstance(company['date_of_drive'], date):
            company['date_of_drive'] = company['date_of_drive'].strftime('%Y-%m-%d')

    with open("companies.json", "w") as file:
        json.dump(companies, file, indent=4)

def admin_login():
    if st.session_state.get("admin_logged_in"):
        return

    st.subheader("🔐 Admin Login")
    username = st.text_input("Username", key="admin_username")
    password = st.text_input("Password", type="password", key="admin_password")

    if st.button("Login", key="admin_login_btn"):
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == hashlib.sha256(password.encode()).hexdigest():
            st.session_state["admin_logged_in"] = True
            st.success("✅ Login successful!")
            st.experimental_rerun()
        else:
            st.error("❌ Invalid username or password")

def generate_job_id(company_name, role):
    return f"{company_name.lower().replace(' ', '_')}_{role.lower().replace(' ', '_')}"

def admin_dashboard():
    st.title("📊 Admin Dashboard")

    students = load_students()
    companies = load_companies()

    for company in companies:
        if 'job_id' not in company:
            company['job_id'] = generate_job_id(company['name'], company['role'])
    save_companies(companies)
    menu = ["View Students", "Add a New Company", "Placement Analytics", "View All Companies", "Shortlisted Students", "Send Notification","Student Queries"]

    # menu = ["View Students", "Add a New Company", "Placement Analytics", "View All Companies", "Shortlisted Students"]
    choice = st.radio("Choose Action", menu, horizontal=True)

    if choice == "View Students":
        st.subheader("📋 Registered Students")
        search_query = st.text_input("Search by Name or Student ID")
        filtered_students = [
            s for s in students
            if search_query.lower() in s['name'].lower()
            or search_query.lower() in s.get('student_id', '').lower()
            or search_query.lower() in s.get('id', '').lower()
        ]

        if filtered_students:
            for s in filtered_students:
                student_id = s.get('student_id') or s.get('id')
                with st.expander(f"{s['name']} ({student_id})"):
                    st.write(f"**Branch:** {s['branch']}")
                    st.write(f"**CGPA:** {s['cgpa']}")
                    st.write(f"**Email:** {s['email']}")
                    resume_path = s.get("resume")
                    if resume_path and os.path.exists(resume_path):
                        with open(resume_path, "rb") as f:
                            st.download_button("📄 Download Resume", data=f, file_name=os.path.basename(resume_path), mime="application/pdf")
        else:
            st.info("No students found with that search.")

    elif choice == "Add a New Company":
        st.subheader("➕ Add New Company")

        company_name = st.text_input("Company Name")
        role = st.text_input("Role")
        package = st.number_input("Package", min_value=0)
        min_cgpa = st.number_input("Minimum CGPA", min_value=0.0, format="%.2f")
        eligible_departments = st.multiselect("Eligible Departments", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"])
        date_of_drive = st.date_input("Date of Drive")

        if st.button("Add Company"):
            if company_name and role and package and min_cgpa and eligible_departments:
                job_id = generate_job_id(company_name, role)
                new_company = {
                    "name": company_name,
                    "role": role,
                    "package": package,
                    "min_cgpa": min_cgpa,
                    "eligible_departments": eligible_departments,
                    "date_of_drive": str(date_of_drive),
                    "completed": False,
                    "job_id": job_id
                }
                companies.append(new_company)
                save_companies(companies)
                st.success(f"Company '{company_name}' added successfully!")
            else:
                st.error("Please fill all required fields correctly.")

    elif choice == "View All Companies":
        st.subheader("🏢 All Companies")

        if not companies:
            st.info("No companies available.")
        else:
            for i, company in enumerate(companies):
                with st.expander(f"{company['name']} - {company['role']}"):
                    st.write(f"**Package:** {company['package']} LPA")
                    st.write(f"**Min CGPA:** {company['min_cgpa']}")
                    st.write(f"**Departments:** {', '.join(company['eligible_departments'])}")
                    st.write(f"**Drive Date:** {company['date_of_drive']}")
                    st.write(f"**Job ID:** `{company['job_id']}`")
                    st.write(f"**Drive Completed:** {'✅ Yes' if company.get('completed') else '❌ No'}")

                    if st.button("✅ Mark Drive as Completed", key=f"completed_{i}"):
                        companies[i]['completed'] = True
                        save_companies(companies)
                        st.success(f"Drive marked as completed for {company['name']}.")

                    if st.button("🗑️ Delete Company", key=f"delete_{i}"):
                        del companies[i]
                        save_companies(companies)
                        st.warning(f"Company '{company['name']}' deleted.")
                        st.experimental_rerun()

    elif choice == "Placement Analytics":
        st.subheader("📈 Placement Analytics")
        # Summary boxes
        st.markdown("### 📊 Summary")

        colA, colB = st.columns(2)

        with colA:
            st.success(f"🏢 **Total Companies:** {len(companies)}")

        with colB:
            placed_students = [s for s in students if s.get("selected_company")]
            st.info(f"🎓 **Students Placed:** {len(placed_students)}")


        col1, col2 = st.columns(2)

        # 1. Students Placed per Company
        with col1:
            st.markdown("**🏢 Students Placed per Company**")
            placed_company_counts = {}
            for student in students:
                if student.get("selected_company"):
                    company = student["selected_company"]
                    placed_company_counts[company] = placed_company_counts.get(company, 0) + 1

            if placed_company_counts:
                df_company = pd.DataFrame(list(placed_company_counts.items()), columns=["Company", "Count"])
                st.bar_chart(df_company.set_index("Company"))
            else:
                st.info("No placement data available.")

        # 2. Students Placed per Year
        import datetime  # Ensure the datetime module is imported properly

# 2. Students Placed per Year
        with col2:
            st.markdown("**📅 Students Placed per Year**")
            company_year_map = {}
            for company in companies:
                try:
                    year = datetime.datetime.strptime(company["date_of_drive"], "%Y-%m-%d").year
                    company_year_map[company["job_id"]] = year
                except:
                    continue

            year_selection_count = {}
            for student in students:
                if "selected" in student and isinstance(student["selected"], list):
                    for job_id in student["selected"]:
                        year = company_year_map.get(job_id)
                        if year:
                            year_selection_count[year] = year_selection_count.get(year, 0) + 1
                elif "selected_company" in student:
                    for comp in companies:
                        if comp["name"].lower() == student["selected_company"].lower():
                            year = datetime.datetime.strptime(comp["date_of_drive"], "%Y-%m-%d").year
                            year_selection_count[year] = year_selection_count.get(year, 0) + 1

            if year_selection_count:
                df_year = pd.DataFrame(list(year_selection_count.items()), columns=["Year", "Count"])
                st.bar_chart(df_year.set_index("Year"))
            else:
                st.info("No year-wise data available.")

        col3, col4 = st.columns(2)
        # 3. Students Placed per Branch
        with col3:
            st.markdown("**🎓 Students Placed per Branch**")
            branch_count = {}
            for student in students:
                if student.get("selected_company"):
                    branch = student.get("branch", "Unknown")
                    branch_count[branch] = branch_count.get(branch, 0) + 1

            if branch_count:
                df_branch = pd.DataFrame(list(branch_count.items()), columns=["Branch", "Count"])
                st.bar_chart(df_branch.set_index("Branch"))
            else:
                st.info("No branch placement data available.")

        # 4. Applications per Company
            st.markdown("### 🗂️ Company-wise Applications & Placements")

            company_stats = []

            for company in companies:
                comp_name = company["name"]
                
                # Count how many students applied to this company
                applied_count = sum(1 for student in students if comp_name in student.get("applications", []))

                # Count how many students are placed in this company
                placed_count = sum(1 for student in students if student.get("selected_company") == comp_name)

                company_stats.append((comp_name, applied_count, placed_count))

            # Display as info boxes
            for i in range(0, len(company_stats), 2):
                col1, col2 = st.columns(2)
                for idx, col in enumerate([col1, col2]):
                    if i + idx < len(company_stats):
                        name, apps, placed = company_stats[i + idx]
                        col.success(
                            f"📌 **{name}**\n\n"
                            f"- 📝 Applications: `{apps}`\n"
                            f"- 🎯 Placed: `{placed}`"
                        )

            




    elif choice == "Student Queries":
        admin_queries_section()



    elif choice == "Shortlisted Students":
        st.subheader("✅ Shortlisted Students by Company & Round")

        if not companies:
            st.info("No companies available.")
        else:
            for company in companies:
                company_title = f"{company['name']} - {company['role']}"
                job_id = company['job_id']
                with st.expander(company_title):
                    rounds = ["Round 1", "Round 2", "Round 3", "HR Round", "Final Round"]
                    selected_round = st.selectbox(f"Select Round for {company_title}", rounds, key=job_id)

                    shortlisted_students = []
                    for student in students:
                        shortlists = student.get("shortlists", {})
                        if job_id in shortlists and shortlists[job_id].get(selected_round):
                            shortlisted_students.append(student)

                    if shortlisted_students:
                        st.write(f"### 👥 Students shortlisted for {selected_round}")
                        for s in shortlisted_students:
                            sid = s.get("student_id", s.get("id", "N/A"))
                            st.markdown(f"- **{s['name']}** (ID: {sid}) | Branch: {s['branch']} | CGPA: {s['cgpa']}")
                    else:
                        st.warning("No students shortlisted yet.")

                    st.markdown("#### ➕ Add a student to this round:")
                    student_id_input = st.text_input(f"Enter Student ID for {selected_round}", key=f"{job_id}_{selected_round}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Shortlist Student", key=f"shortlist_{job_id}_{selected_round}"):
                            found = False
                            for s in students:
                                sid = s.get("student_id") or s.get("id")
                                if sid == student_id_input:
                                    if "shortlists" not in s:
                                        s["shortlists"] = {}
                                    if job_id not in s["shortlists"]:
                                        s["shortlists"][job_id] = {}
                                    s["shortlists"][job_id][selected_round] = True
                                    save_students(students)
                                    st.success(f"{s['name']} shortlisted for {selected_round} of {company_title}.")
                                    send_shortlist_email(
                                        to_email=s["email"],
                                        student_name=s["name"],
                                        company_name=company["name"],
                                        role=company["role"],
                                        job_id=job_id,
                                        round_name=selected_round,
                                        status="shortlisted"
                                    )
                                    found = True
                                    break
                            if not found:
                                st.error("Student ID not found.")

                    with col2:
                        if st.button("Mark as Selected", key=f"select_{job_id}_{selected_round}"):
                            found = False
                            for s in students:
                                sid = s.get("student_id") or s.get("id")
                                if sid == student_id_input:
                                    if "selected" not in s:
                                        s["selected"] = []
                                    if job_id not in s["selected"]:
                                        s["selected"].append(job_id)
                                    if "shortlists" not in s:
                                        s["shortlists"] = {}
                                    if job_id not in s["shortlists"]:
                                        s["shortlists"][job_id] = {}
                                    s["shortlists"][job_id][selected_round] = True
                                    save_students(students)
                                    st.success(f"{s['name']} marked as SELECTED for {company_title}.")
                                    send_shortlist_email(
                                        to_email=s["email"],
                                        student_name=s["name"],
                                        company_name=company["name"],
                                        role=company["role"],
                                        job_id=job_id,
                                        round_name=selected_round,
                                        status="selected"
                                    )
                                    found = True
                                    break
                            if not found:
                                st.error("Student ID not found.")
    elif choice == "Send Notification":
        st.subheader("📢 Send Notification to Students")

        company_options = [f"{c['name']} - {c['role']} ({c['job_id']})" for c in companies]
        selected_company = st.selectbox("Select Company", company_options)
        selected_company_data = next(c for c in companies if f"{c['name']} - {c['role']} ({c['job_id']})" == selected_company)

        venue = st.text_input("Venue")
        round_number = st.selectbox("Round", ["Round 1", "Round 2", "Round 3", "HR Round", "Final Round"])
        round_time = st.time_input("Time of the Round")
        description = st.text_area("Description")
        meeting_link = st.text_input("Meeting Link (optional)")

        if st.button("📤 Send Notification"):
            new_notification = {
                "company_name": selected_company_data["name"],
                "job_id": selected_company_data["job_id"],
                "role": selected_company_data["role"],
                "venue": venue,
                "round": round_number,
                "time": str(round_time),
                "description": description,
                "meeting_link": meeting_link
            }

            notifications = load_notifications()
            notifications.append(new_notification)
            save_notifications(notifications)
            st.success("Notification sent successfully!")


NOTIFICATIONS_FILE = "notifications.json"

def load_notifications():
    if os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, "r") as f:
            return json.load(f)
    return []

def save_notifications(notifications):
    with open(NOTIFICATIONS_FILE, "w") as f:
        json.dump(notifications, f, indent=4)


def plt_pie_chart(df):
    fig, ax = plt.subplots(figsize=(4, 4))
    ax.pie(df["Count"], labels=df["Status"], autopct="%1.1f%%", colors=["#4CAF50", "#FF5722"])
    ax.axis("equal")
    return fig


QUERIES_FILE = "queries.json"

import streamlit as st
import os
import json
import datetime

QUERIES_FILE = "queries.json"
RESPONSES_FILE = "responses.json"

def load_queries():
    if not os.path.exists(QUERIES_FILE):
        return []
    with open(QUERIES_FILE, "r") as f:
        return json.load(f)

def save_queries(queries):
    with open(QUERIES_FILE, "w") as f:
        json.dump(queries, f, indent=4)

def save_response(student_id, student_name, original_query, response):
    response_entry = {
        "student_id": student_id,
        "student_name": student_name,
        "original_query": original_query,
        "response": response,
        "response_date": str(datetime.date.today())
    }

    # Load existing responses or initialize
    if os.path.exists(RESPONSES_FILE):
        with open(RESPONSES_FILE, "r") as f:
            try:
                responses = json.load(f)
            except json.JSONDecodeError:
                responses = []
    else:
        responses = []

    responses.append(response_entry)
    with open(RESPONSES_FILE, "w") as f:
        json.dump(responses, f, indent=4)

def admin_queries_section():
    st.subheader("📬 Student Queries")

    queries = load_queries()

    if not queries:
        st.info("No queries submitted by students.")
    else:
        for idx, query in enumerate(queries):
            with st.expander(f"{query['student_name']} (ID: {query['student_id']})"):
                st.write(f"**Query:** {query['message']}")
                date = query.get("date")
                if date and date.strip():
                    st.write(f"**Date:** {date}")
                else:
                    st.write("**Date:** Not provided")

                # Admin response input
                response = st.text_area(f"Enter your response to {query['student_name']}:", key=f"response_{idx}")
                if st.button("Send Response", key=f"send_{idx}"):
                    if response.strip():
                        save_response(query['student_id'], query['student_name'], query['message'], response)
                        st.success("✅ Response sent and saved!")
                    else:
                        st.warning("Please enter a response before sending.")
