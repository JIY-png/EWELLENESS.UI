from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session, flash
from datetime import datetime
from io import BytesIO
from functools import wraps
import os
import csv
import json
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

# pyrefly: ignore [missing-import]
from supabase import create_client, Client


app = Flask(__name__)
app.secret_key = "ewellness_frontend_demo_secret"


# --------------------------------------------------
# SUPABASE CONFIGURATION
# --------------------------------------------------

# Load environment variables
load_dotenv()

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

try:
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Supabase initialized successfully")
    else:
        print("Supabase initialization error: Missing credentials")
        print("Please ensure SUPABASE_URL and SUPABASE_KEY are set in .env file")
        supabase = None
except Exception as e:
    print(f"Supabase initialization error: {e}")
    print("Please ensure SUPABASE_URL and SUPABASE_KEY are set correctly in .env file")
    supabase = None


# --------------------------------------------------
# SUPABASE HELPER FUNCTIONS
# --------------------------------------------------

def get_patients():
    if supabase is None:
        return []
    try:
        response = supabase.table('patients').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error getting patients: {e}")
        return []

def get_patient_by_id(patient_id):
    if supabase is None:
        return None
    try:
        response = supabase.table('patients').select('*').eq('id', patient_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting patient by id: {e}")
        return None

def add_patient(patient_data):
    if supabase is None:
        return None
    try:
        response = supabase.table('patients').insert(patient_data).execute()
        if response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Error adding patient: {e}")
        return None

def update_patient(patient_id, patient_data):
    if supabase is None:
        return False
    try:
        response = supabase.table('patients').update(patient_data).eq('id', patient_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating patient: {e}")
        return False

def delete_patient(patient_id):
    if supabase is None:
        return False
    try:
        response = supabase.table('patients').delete().eq('id', patient_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return False

def get_records():
    if supabase is None:
        return []
    try:
        response = supabase.table('records').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error getting records: {e}")
        return []

def get_records_for_patient(patient_id):
    if supabase is None:
        return []
    try:
        response = supabase.table('records').select('*').eq('patient_id', patient_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting records for patient: {e}")
        return []

def add_record(record_data):
    if supabase is None:
        return None
    try:
        response = supabase.table('records').insert(record_data).execute()
        if response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Error adding record: {e}")
        return None

def get_admin_users():
    if supabase is None:
        return []
    try:
        response = supabase.table('admin_users').select('*').execute()
        return response.data
    except Exception as e:
        print(f"Error getting admin users: {e}")
        return []

def get_admin_by_username(username):
    if supabase is None:
        return None
    try:
        response = supabase.table('admin_users').select('*').eq('username', username.lower()).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting admin by username: {e}")
        return None

def get_admin_by_id(admin_id):
    if supabase is None:
        return None
    try:
        response = supabase.table('admin_users').select('*').eq('id', admin_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error getting admin by id: {e}")
        return None

def add_admin_user(user_data):
    if supabase is None:
        return None
    try:
        response = supabase.table('admin_users').insert(user_data).execute()
        if response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Error adding admin user: {e}")
        return None

def update_admin_user(admin_id, user_data):
    if supabase is None:
        return False
    try:
        response = supabase.table('admin_users').update(user_data).eq('id', admin_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error updating admin user: {e}")
        return False

def delete_admin_user(admin_id):
    if supabase is None:
        return False
    try:
        response = supabase.table('admin_users').delete().eq('id', admin_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"Error deleting admin user: {e}")
        return False

def get_access_logs():
    if supabase is None:
        return []
    try:
        response = supabase.table('access_logs').select('*').order('date_time', desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Error getting access logs: {e}")
        return []

def add_access_log(user, role, action):
    if supabase is None:
        return None
    try:
        log_data = {
            "user": user,
            "role": role,
            "action": action,
            "date_time": datetime.now().strftime("%Y-%m-%d %I:%M %p")
        }
        response = supabase.table('access_logs').insert(log_data).execute()
        if response.data:
            return response.data[0]['id']
        return None
    except Exception as e:
        print(f"Error adding access log: {e}")
        return None

def get_next_patient_id():
    patients = get_patients()
    if not patients:
        return 1
    return max(patient['id'] for patient in patients) + 1

def get_next_record_id():
    records = get_records()
    if not records:
        return 1
    return max(record['id'] for record in records) + 1

def get_next_admin_id():
    admin_users = get_admin_users()
    if not admin_users:
        return 1
    return max(user['id'] for user in admin_users) + 1


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def calculate_bmi(height_cm, weight_kg):
    if height_cm <= 0:
        return 0

    height_m = height_cm / 100
    bmi = weight_kg / (height_m * height_m)
    return round(bmi, 1)


def calculate_age(birth_date):
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except:
        return 0


def get_bmi_category(bmi):
    if bmi <= 0:
        return "Invalid"
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def get_detailed_status(temperature, heart_rate, oxygen_saturation, systolic, diastolic, bmi):
    issues = []

    # Check temperature
    if temperature > 37.5:
        issues.append("High Temp")
    elif temperature < 36.0:
        issues.append("Low Temp")

    # Check heart rate
    if heart_rate > 100:
        issues.append("High HR")
    elif heart_rate < 60:
        issues.append("Low HR")

    # Check oxygen saturation
    if oxygen_saturation < 95:
        issues.append("Low SpO2")

    # Check blood pressure
    if systolic > 140 or diastolic > 90:
        issues.append("High BP")
    elif systolic < 90 or diastolic < 60:
        issues.append("Low BP")

    # Check BMI
    bmi_cat = get_bmi_category(bmi)
    if bmi_cat != "Normal":
        issues.append(bmi_cat)

    # If no issues, return "Normal"
    if not issues:
        return "Normal"

    # If there are issues, return them as comma-separated list
    return ", ".join(issues)


def get_record_status(temperature, heart_rate, oxygen_saturation, systolic, diastolic, bmi_category):
    abnormal_vitals = (
        temperature < 36.0 or temperature > 37.5 or
        heart_rate < 60 or heart_rate > 100 or
        oxygen_saturation < 95 or
        systolic >= 140 or
        diastolic >= 90
    )

    abnormal_bmi = bmi_category in ["Underweight", "Overweight", "Obese"]

    if abnormal_vitals or abnormal_bmi:
        return "Needs Attention"

    return "Normal"


def get_patient_name(patient_id):
    patient = get_patient_by_id(patient_id)
    if patient:
        return f'{patient["first_name"]} {patient["last_name"]}'
    return "Unknown Patient"


def create_health_record(patient_id, temperature, heart_rate, oxygen_saturation, systolic, diastolic, height, weight):
    bmi = calculate_bmi(height, weight)
    bmi_category = get_bmi_category(bmi)

    status = get_detailed_status(temperature, heart_rate, oxygen_saturation, systolic, diastolic, bmi)

    abnormal_reasons = []

    if temperature < 36.0:
        abnormal_reasons.append("low body temperature")

    if temperature > 37.5:
        abnormal_reasons.append("high body temperature")

    if heart_rate < 60:
        abnormal_reasons.append("low heart rate")

    if heart_rate > 100:
        abnormal_reasons.append("high heart rate")

    if oxygen_saturation < 95:
        abnormal_reasons.append("low oxygen saturation")

    if systolic >= 140 or diastolic >= 90:
        abnormal_reasons.append("high blood pressure")

    if bmi_category == "Underweight":
        abnormal_reasons.append("underweight BMI")

    if bmi_category == "Overweight":
        abnormal_reasons.append("overweight BMI")

    if bmi_category == "Obese":
        abnormal_reasons.append("obese BMI")

    if status != "Normal":
        remarks = "Needs health personnel review due to " + ", ".join(abnormal_reasons) + "."
    else:
        remarks = "Vital signs and BMI are within normal range."

    patient = get_patient_by_id(patient_id)
    age = calculate_age(patient["birth_date"]) if patient else 0

    new_record = {
        "id": get_next_record_id(),
        "patient_id": patient_id,
        "A": datetime.now().strftime("%Y-%m-%d"),  # Date
        "B": datetime.now().strftime("%I:%M %p"),  # Time
        "C": patient["first_name"] if patient else "",  # FirstName
        "D": patient["last_name"] if patient else "",  # LastName
        "E": age,  # Age
        "F": patient["gender"] if patient else "",  # Gender
        "G": f"{systolic}/{diastolic}",  # BloodPressure
        "H": heart_rate,  # HeartRate_BPM
        "I": oxygen_saturation,  # OxygenSaturation_pct
        "J": temperature,  # BodyTemp_C
        "K": weight,  # Weight_kg
        "L": height,  # Height_cm
        "M": bmi,  # BMI
        "bmi_category": bmi_category,
        "status": status,
        "remarks": remarks,
        "created_at": datetime.now().strftime("%Y-%m-%d %I:%M %p")
    }

    add_record(new_record)
    return new_record


def dashboard_stats():
    patients_list = get_patients()
    records_list = get_records()

    total_patients = len(patients_list)
    total_records = len(records_list)

    # Count normal and attention records based on actual status from database
    normal_records = len([record for record in records_list if record["status"] == "Normal"])
    attention_records = len([record for record in records_list if record["status"] != "Normal"])

    if total_records > 0:
        average_bmi = round(sum(record["M"] for record in records_list if record.get("M")) / total_records, 1)
    else:
        average_bmi = 0

    return {
        "total_patients": total_patients,
        "total_records": total_records,
        "normal_records": normal_records,
        "attention_records": attention_records,
        "average_bmi": average_bmi,
        "documentation_reduction": 70
    }


def bmi_trends():
    records_list = get_records()
    labels = ["Underweight", "Normal", "Overweight", "Obese"]
    total = len(records_list) if records_list else 1
    trend_data = []

    for label in labels:
        count = len([record for record in records_list if record["bmi_category"] == label])
        percentage = round((count / total) * 100)

        trend_data.append({
            "label": label,
            "count": count,
            "percentage": percentage
        })

    return trend_data


def bmi_chart_records():
    records_list = get_records()
    return [
        {
            "bmi": record["M"],
            "category": record["bmi_category"],
            "created_at": record["created_at"],
            "patient_name": f"{record.get('C', '')} {record.get('D', '')}"
        }
        for record in records_list
    ]


def status_trends():
    records_list = get_records()
    labels = ["Normal", "Needs Attention"]
    total = len(records_list) if records_list else 1
    trend_data = []

    for label in labels:
        if label == "Normal":
            count = len([record for record in records_list if record["status"] == "Normal"])
        else:
            count = len([record for record in records_list if record["status"] != "Normal"])
        percentage = round((count / total) * 100)

        trend_data.append({
            "label": label,
            "count": count,
            "percentage": percentage
        })

    return trend_data


def ehr_patient_summaries():
    summaries = []
    patients_list = get_patients()

    for patient in patients_list:
        patient_records = get_records_for_patient(patient["id"])
        latest_record = patient_records[-1] if patient_records else None

        summaries.append({
            "patient": patient,
            "record_count": len(patient_records),
            "latest_record": latest_record
        })

    return summaries


def make_safe_filename(text):
    safe_text = text.lower().strip()
    safe_text = safe_text.replace(" ", "_")

    allowed_characters = "abcdefghijklmnopqrstuvwxyz0123456789_"

    cleaned = "".join(
        character for character in safe_text
        if character in allowed_characters
    )

    if cleaned:
        return cleaned

    return "patient"


# --------------------------------------------------
# ADMIN AUTHENTICATION HELPERS
# --------------------------------------------------

def username_exists(username, current_admin_id=None):
    admin_users_list = get_admin_users()
    for admin in admin_users_list:
        same_username = admin["username"].lower() == username.lower()
        different_user = current_admin_id is None or admin["id"] != current_admin_id

        if same_username and different_user:
            return True

    return False


def get_current_admin_name():
    return session.get("admin_name", "Clinic Admin")


def get_current_admin_role():
    return session.get("admin_role", "System Admin")


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login_page"))

        return route_function(*args, **kwargs)

    return wrapper


def system_admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login_page"))

        if session.get("admin_role") != "System Admin":
            flash("Only System Admin can access user management.", "error")
            return redirect(url_for("dashboard"))

        return route_function(*args, **kwargs)

    return wrapper


# --------------------------------------------------
# AUTH ROUTES
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if "admin_id" in session:
        return redirect(url_for("dashboard"))

    error = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = get_admin_by_username(username)

        if admin and check_password_hash(admin["password_hash"], password):
            session["admin_id"] = admin["id"]
            session["admin_name"] = admin["full_name"]
            session["admin_role"] = admin["role"]

            add_access_log(
                user=admin["full_name"],
                role=admin["role"],
                action="Logged in to the E-Wellness system"
            )

            flash("Logged in successfully.", "success")
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."
        flash("Invalid username or password.", "error")

    return render_template(
        "auth/login.html",
        title="Admin Login",
        error=error
    )


@app.route("/signup", methods=["GET", "POST"])
def signup_page():
    if "admin_id" in session:
        return redirect(url_for("dashboard"))

    error = ""

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not username or not role or not password or not confirm_password:
            error = "Please complete all required fields."
            flash("Please complete all required fields.", "warning")
        elif get_admin_by_username(username):
            error = "Username already exists."
            flash("Username already exists.", "error")
        elif password != confirm_password:
            error = "Passwords do not match."
            flash("Passwords do not match.", "error")
        else:
            new_admin = {
                "id": get_next_admin_id(),
                "full_name": full_name,
                "username": username,
                "role": role,
                "password_hash": generate_password_hash(password)
            }

            add_admin_user(new_admin)

            session["admin_id"] = new_admin["id"]
            session["admin_name"] = new_admin["full_name"]
            session["admin_role"] = new_admin["role"]

            add_access_log(
                user=new_admin["full_name"],
                role=new_admin["role"],
                action="Created an admin account and logged in"
            )

            flash("Admin account created successfully.", "success")
            return redirect(url_for("dashboard"))

    return render_template(
        "auth/signup.html",
        title="Admin Signup",
        error=error
    )


@app.route("/logout")
@login_required
def logout_page():
    admin_name = get_current_admin_name()
    admin_role = get_current_admin_role()

    add_access_log(
        user=admin_name,
        role=admin_role,
        action="Logged out of the E-Wellness system"
    )

    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login_page"))


# --------------------------------------------------
# USER MANAGEMENT ROUTES
# --------------------------------------------------

@app.route("/users")
@system_admin_required
def users_page():
    return render_template(
        "admin/users.html",
        title="User Management",
        active_page="users",
        admin_users=get_admin_users()
    )


@app.route("/users/add", methods=["GET", "POST"])
@system_admin_required
def add_user_page():
    error = ""

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not full_name or not username or not role or not password or not confirm_password:
            error = "Please complete all required fields."
            flash("Please complete all required fields.", "warning")
        elif username_exists(username):
            error = "Username already exists."
            flash("Username already exists.", "error")
        elif password != confirm_password:
            error = "Passwords do not match."
            flash("Passwords do not match.", "error")
        else:
            new_admin = {
                "id": get_next_admin_id(),
                "full_name": full_name,
                "username": username,
                "role": role,
                "password_hash": generate_password_hash(password)
            }

            add_admin_user(new_admin)

            add_access_log(
                user=get_current_admin_name(),
                role=get_current_admin_role(),
                action=f'Created user account for {full_name} as {role}'
            )

            flash("User account added successfully.", "success")
            return redirect(url_for("users_page"))

    return render_template(
        "admin/user_form.html",
        title="Add User",
        active_page="users",
        mode="add",
        user=None,
        error=error
    )


@app.route("/users/edit/<int:admin_id>", methods=["GET", "POST"])
@system_admin_required
def edit_user_page(admin_id):
    admin = get_admin_by_id(admin_id)

    if admin is None:
        flash("User account not found.", "error")
        return redirect(url_for("users_page"))

    error = ""

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()
        role = request.form.get("role", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not full_name or not username or not role:
            error = "Please complete all required fields."
            flash("Please complete all required fields.", "warning")
        elif username_exists(username, current_admin_id=admin_id):
            error = "Username already exists."
            flash("Username already exists.", "error")
        elif password and password != confirm_password:
            error = "Passwords do not match."
            flash("Passwords do not match.", "error")
        elif session.get("admin_id") == admin_id and role != "System Admin":
            error = "You cannot change your own System Admin role."
            flash("You cannot change your own System Admin role.", "warning")
        else:
            old_name = admin["full_name"]
            old_role = admin["role"]

            update_data = {
                "full_name": full_name,
                "username": username,
                "role": role
            }

            if password:
                update_data["password_hash"] = generate_password_hash(password)

            update_admin_user(admin_id, update_data)

            if session.get("admin_id") == admin_id:
                session["admin_name"] = full_name
                session["admin_role"] = role

            add_access_log(
                user=get_current_admin_name(),
                role=get_current_admin_role(),
                action=f'Updated user account {old_name} from {old_role} to {role}'
            )

            flash("User account updated successfully.", "success")
            return redirect(url_for("users_page"))

    return render_template(
        "admin/user_form.html",
        title="Edit User",
        active_page="users",
        mode="edit",
        user=admin,
        error=error
    )


@app.route("/users/delete/<int:admin_id>", methods=["POST"])
@system_admin_required
def delete_user_page(admin_id):
    admin = get_admin_by_id(admin_id)

    if admin is None:
        flash("User account not found.", "error")
        return redirect(url_for("users_page"))

    if session.get("admin_id") == admin_id:
        flash("You cannot delete your own logged-in account.", "warning")
        return redirect(url_for("users_page"))

    admin_users_list = get_admin_users()
    system_admin_count = len([
        user for user in admin_users_list
        if user["role"] == "System Admin"
    ])

    if admin["role"] == "System Admin" and system_admin_count <= 1:
        flash("At least one System Admin account must remain.", "warning")
        return redirect(url_for("users_page"))

    deleted_name = admin["full_name"]
    deleted_role = admin["role"]

    delete_admin_user(admin_id)

    add_access_log(
        user=get_current_admin_name(),
        role=get_current_admin_role(),
        action=f'Deleted user account for {deleted_name} with role {deleted_role}'
    )

    flash("User account deleted successfully.", "success")
    return redirect(url_for("users_page"))


# --------------------------------------------------
# KIOSK ROUTES
# Patient-facing pages do not require admin login.
# --------------------------------------------------

@app.route("/kiosk")
def kiosk_welcome_page():
    return render_template(
        "kiosk/kiosk_welcome.html",
        title="Health Monitoring Kiosk"
    )


@app.route("/kiosk/checkin", methods=["GET", "POST"])
def kiosk_checkin_page():
    if request.method == "POST":
        session["kiosk_patient"] = {
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "birth_date": request.form.get("birth_date", "").strip(),
            "contact_no": request.form.get("contact_no", "").strip(),
            "barangay": request.form.get("barangay", "").strip()
        }

        session["kiosk_results"] = {}

        return redirect(url_for("kiosk_assessment_page"))

    return render_template(
        "kiosk/kiosk_checkin.html",
        title="Patient Check-in"
    )


@app.route("/kiosk/assessment")
def kiosk_assessment_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    return render_template(
        "kiosk/kiosk_assessment.html",
        title="Health Assessment",
        patient=kiosk_patient
    )


@app.route("/kiosk/measure/temperature")
def kiosk_temperature_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})
    saved_temperature = kiosk_results.get("temperature")

    return render_template(
        "kiosk/kiosk_temperature.html",
        title="Temperature Measurement",
        patient=kiosk_patient,
        saved_temperature=saved_temperature
    )


@app.route("/kiosk/measure/temperature/save", methods=["POST"])
def kiosk_temperature_save_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    temperature_value = request.form.get("temperature_value", "").strip()

    if not temperature_value:
        return redirect(url_for("kiosk_temperature_page"))

    try:
        temperature_value = float(temperature_value)
    except ValueError:
        return redirect(url_for("kiosk_temperature_page"))

    if temperature_value < 36.0:
        temperature_status = "LOW TEMPERATURE"
    elif temperature_value <= 37.5:
        temperature_status = "NORMAL TEMPERATURE"
    else:
        temperature_status = "HIGH TEMPERATURE"

    kiosk_results = session.get("kiosk_results", {})

    kiosk_results["temperature"] = {
        "value": temperature_value,
        "unit": "°C",
        "status": temperature_status
    }

    session["kiosk_results"] = kiosk_results
    session.modified = True

    return redirect(url_for("kiosk_assessment_page"))


@app.route("/kiosk/measure/blood-pressure")
def kiosk_blood_pressure_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})
    saved_blood_pressure = kiosk_results.get("blood_pressure")

    retry = request.args.get("retry") == "1"

    if retry:
        saved_blood_pressure = None

    return render_template(
        "kiosk/kiosk_blood_pressure.html",
        title="Blood Pressure Measurement",
        patient=kiosk_patient,
        saved_blood_pressure=saved_blood_pressure
    )


@app.route("/kiosk/measure/blood-pressure/save", methods=["POST"])
def kiosk_blood_pressure_save_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    systolic_value = request.form.get("systolic_value", "").strip()
    diastolic_value = request.form.get("diastolic_value", "").strip()
    pulse_value = request.form.get("pulse_value", "").strip()

    if not systolic_value or not diastolic_value or not pulse_value:
        return redirect(url_for("kiosk_blood_pressure_page"))

    try:
        systolic_value = int(systolic_value)
        diastolic_value = int(diastolic_value)
        pulse_value = int(pulse_value)
    except ValueError:
        return redirect(url_for("kiosk_blood_pressure_page"))

    if systolic_value < 90 or diastolic_value < 60:
        bp_status = "LOW BLOOD PRESSURE"
    elif systolic_value >= 140 or diastolic_value >= 90:
        bp_status = "HIGH BLOOD PRESSURE"
    else:
        bp_status = "NORMAL BLOOD PRESSURE"

    kiosk_results = session.get("kiosk_results", {})

    kiosk_results["blood_pressure"] = {
        "systolic": systolic_value,
        "diastolic": diastolic_value,
        "pulse": pulse_value,
        "unit": "mmHg",
        "status": bp_status
    }

    session["kiosk_results"] = kiosk_results
    session.modified = True

    return redirect(url_for("kiosk_assessment_page"))


@app.route("/kiosk/measure/height")
def kiosk_height_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})
    saved_height = kiosk_results.get("height")

    retry = request.args.get("retry") == "1"

    if retry:
        saved_height = None

    return render_template(
        "kiosk/kiosk_height.html",
        title="Height Measurement",
        patient=kiosk_patient,
        saved_height=saved_height
    )


@app.route("/kiosk/measure/height/save", methods=["POST"])
def kiosk_height_save_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    height_value = request.form.get("height_value", "").strip()

    if not height_value:
        return redirect(url_for("kiosk_height_page"))

    try:
        height_value = float(height_value)
    except ValueError:
        return redirect(url_for("kiosk_height_page"))

    if height_value < 120:
        height_status = "BELOW AVERAGE HEIGHT"
    elif height_value <= 190:
        height_status = "HEIGHT RECORDED"
    else:
        height_status = "ABOVE AVERAGE HEIGHT"

    kiosk_results = session.get("kiosk_results", {})

    kiosk_results["height"] = {
        "value": height_value,
        "unit": "cm",
        "status": height_status
    }

    session["kiosk_results"] = kiosk_results
    session.modified = True

    return redirect(url_for("kiosk_assessment_page"))


@app.route("/kiosk/measure/weight")
def kiosk_weight_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})
    saved_weight = kiosk_results.get("weight")

    retry = request.args.get("retry") == "1"

    if retry:
        saved_weight = None

    return render_template(
        "kiosk/kiosk_weight.html",
        title="Weight Measurement",
        patient=kiosk_patient,
        saved_weight=saved_weight
    )


@app.route("/kiosk/measure/weight/save", methods=["POST"])
def kiosk_weight_save_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    weight_value = request.form.get("weight_value", "").strip()

    if not weight_value:
        return redirect(url_for("kiosk_weight_page"))

    try:
        weight_value = float(weight_value)
    except ValueError:
        return redirect(url_for("kiosk_weight_page"))

    if weight_value <= 0:
        weight_status = "INVALID WEIGHT"
    else:
        weight_status = "WEIGHT RECORDED"

    kiosk_results = session.get("kiosk_results", {})

    kiosk_results["weight"] = {
        "value": weight_value,
        "unit": "kg",
        "status": weight_status
    }

    session["kiosk_results"] = kiosk_results
    session.modified = True

    return redirect(url_for("kiosk_assessment_page"))


@app.route("/kiosk/measure/bmi")
def kiosk_bmi_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})

    saved_height = kiosk_results.get("height")
    saved_weight = kiosk_results.get("weight")
    saved_bmi = kiosk_results.get("bmi")

    calculated_bmi = None
    bmi_category = None
    bmi_status = None

    if saved_height and saved_weight:
        height_value = float(saved_height["value"])
        weight_value = float(saved_weight["value"])

        calculated_bmi = calculate_bmi(height_value, weight_value)
        bmi_category = get_bmi_category(calculated_bmi)
        bmi_status = bmi_category.upper() + " BMI"

    return render_template(
        "kiosk/kiosk_bmi.html",
        title="BMI Calculation",
        patient=kiosk_patient,
        saved_height=saved_height,
        saved_weight=saved_weight,
        saved_bmi=saved_bmi,
        calculated_bmi=calculated_bmi,
        bmi_category=bmi_category,
        bmi_status=bmi_status
    )


@app.route("/kiosk/measure/bmi/save", methods=["POST"])
def kiosk_bmi_save_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})

    saved_height = kiosk_results.get("height")
    saved_weight = kiosk_results.get("weight")

    if not saved_height or not saved_weight:
        return redirect(url_for("kiosk_bmi_page"))

    height_value = float(saved_height["value"])
    weight_value = float(saved_weight["value"])

    bmi_value = calculate_bmi(height_value, weight_value)
    bmi_category = get_bmi_category(bmi_value)

    kiosk_results["bmi"] = {
        "value": bmi_value,
        "unit": "kg/m²",
        "category": bmi_category,
        "status": bmi_category.upper() + " BMI"
    }

    session["kiosk_results"] = kiosk_results
    session.modified = True

    return redirect(url_for("kiosk_assessment_page"))


@app.route("/kiosk/measure/spo2")
def kiosk_spo2_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})
    saved_spo2 = kiosk_results.get("oxygen_saturation")

    retry = request.args.get("retry") == "1"

    if retry:
        saved_spo2 = None

    return render_template(
        "kiosk/kiosk_spo2.html",
        title="Oxygen Saturation Measurement",
        patient=kiosk_patient,
        saved_spo2=saved_spo2
    )


@app.route("/kiosk/measure/spo2/save", methods=["POST"])
def kiosk_spo2_save_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    spo2_value = request.form.get("spo2_value", "").strip()

    if not spo2_value:
        return redirect(url_for("kiosk_spo2_page"))

    try:
        spo2_value = int(spo2_value)
    except ValueError:
        return redirect(url_for("kiosk_spo2_page"))

    if spo2_value < 95:
        spo2_status = "LOW OXYGEN SATURATION"
    elif spo2_value <= 100:
        spo2_status = "NORMAL OXYGEN SATURATION"
    else:
        spo2_status = "INVALID OXYGEN SATURATION"

    kiosk_results = session.get("kiosk_results", {})

    kiosk_results["oxygen_saturation"] = {
        "value": spo2_value,
        "unit": "%",
        "status": spo2_status
    }

    session["kiosk_results"] = kiosk_results
    session.modified = True

    return redirect(url_for("kiosk_assessment_page"))


@app.route("/kiosk/summary")
def kiosk_summary_page():
    kiosk_patient = session.get("kiosk_patient")

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    kiosk_results = session.get("kiosk_results", {})

    required_results = {
        "temperature": "Body Temperature",
        "blood_pressure": "Blood Pressure",
        "oxygen_saturation": "Oxygen Saturation",
        "height": "Height",
        "weight": "Weight",
        "bmi": "BMI"
    }

    missing_results = []

    for key, label in required_results.items():
        if key not in kiosk_results:
            missing_results.append({
                "key": key,
                "label": label
            })

    is_complete = len(missing_results) == 0

    overall_status = "Incomplete"

    if is_complete:
        abnormal_findings = []

        temperature = kiosk_results["temperature"]["value"]
        blood_pressure = kiosk_results["blood_pressure"]
        oxygen_saturation = kiosk_results["oxygen_saturation"]["value"]
        bmi_category = kiosk_results["bmi"]["category"]

        if temperature < 36.0:
            abnormal_findings.append("low body temperature")

        if temperature > 37.5:
            abnormal_findings.append("high body temperature")

        if blood_pressure["systolic"] >= 140 or blood_pressure["diastolic"] >= 90:
            abnormal_findings.append("high blood pressure")

        if blood_pressure["systolic"] < 90 or blood_pressure["diastolic"] < 60:
            abnormal_findings.append("low blood pressure")

        if oxygen_saturation < 95:
            abnormal_findings.append("low oxygen saturation")

        if bmi_category in ["Underweight", "Overweight", "Obese"]:
            abnormal_findings.append(bmi_category.lower() + " BMI")

        if abnormal_findings:
            overall_status = "Needs Attention"
        else:
            overall_status = "Normal"

    return render_template(
        "kiosk/kiosk_summary.html",
        title="Summary Results",
        patient=kiosk_patient,
        results=kiosk_results,
        missing_results=missing_results,
        is_complete=is_complete,
        overall_status=overall_status
    )


@app.route("/kiosk/summary/submit", methods=["POST"])
def kiosk_summary_submit_page():
    kiosk_patient = session.get("kiosk_patient")
    kiosk_results = session.get("kiosk_results", {})

    if not kiosk_patient:
        return redirect(url_for("kiosk_checkin_page"))

    required_keys = [
        "temperature",
        "blood_pressure",
        "oxygen_saturation",
        "height",
        "weight",
        "bmi"
    ]

    for key in required_keys:
        if key not in kiosk_results:
            return redirect(url_for("kiosk_summary_page"))

    new_patient = {
        "id": get_next_patient_id(),
        "first_name": kiosk_patient.get("first_name", "").strip(),
        "last_name": kiosk_patient.get("last_name", "").strip(),
        "gender": kiosk_patient.get("gender", "Not specified"),
        "birth_date": kiosk_patient.get("birth_date", "").strip(),
        "contact_no": kiosk_patient.get("contact_no", "").strip(),
        "barangay": kiosk_patient.get("barangay", "").strip()
    }

    add_patient(new_patient)

    temperature = float(kiosk_results["temperature"]["value"])
    blood_pressure = kiosk_results["blood_pressure"]
    heart_rate = int(blood_pressure["pulse"])
    oxygen_saturation = int(kiosk_results["oxygen_saturation"]["value"])
    systolic = int(blood_pressure["systolic"])
    diastolic = int(blood_pressure["diastolic"])
    height = float(kiosk_results["height"]["value"])
    weight = float(kiosk_results["weight"]["value"])

    new_record = create_health_record(
        patient_id=new_patient["id"],
        temperature=temperature,
        heart_rate=heart_rate,
        oxygen_saturation=oxygen_saturation,
        systolic=systolic,
        diastolic=diastolic,
        height=height,
        weight=weight
    )

    add_access_log(
        user="Kiosk Patient",
        role="Patient Kiosk",
        action=f'Submitted kiosk health assessment for {new_record["C"]} {new_record["D"]}'
    )

    session.pop("kiosk_patient", None)
    session.pop("kiosk_results", None)
    session.modified = True

    return redirect(url_for("kiosk_complete_page"))


@app.route("/kiosk/complete")
def kiosk_complete_page():
    return render_template(
        "kiosk/kiosk_complete.html",
        title="Assessment Complete"
    )


# --------------------------------------------------
# PAGE ROUTES
# --------------------------------------------------

@app.route("/")
@login_required
def dashboard():
    records_list = get_records()

    # Get all records in reverse order (newest first)
    latest_records = list(reversed(records_list))

    return render_template(
        "admin/dashboard.html",
        title="Dashboard",
        active_page="dashboard",
        stats=dashboard_stats(),
        latest_records=latest_records,
        bmi_trends=bmi_trends(),
        status_trends=status_trends(),
        bmi_chart_records=bmi_chart_records()
    )


@app.route("/patients")
@login_required
def patients_page():
    search = request.args.get("search", "").lower().strip()
    patients_list = get_patients()

    # Add age to each patient
    for patient in patients_list:
        patient["age"] = calculate_age(patient.get("birth_date", ""))

    if search:
        filtered_patients = [
            patient for patient in patients_list
            if search in f'{patient["first_name"]} {patient["last_name"]}'.lower()
            or search in patient["barangay"].lower()
            or search in patient["gender"].lower()
            or search in patient["contact_no"].lower()
        ]
    else:
        filtered_patients = patients_list

    return render_template(
        "admin/patients.html",
        title="Patient Management",
        active_page="patients",
        patients=filtered_patients,
        search=search
    )


@app.route("/add-patient", methods=["GET", "POST"])
@login_required
def add_patient_page():
    if request.method == "POST":
        # Calculate birth date from age
        age = int(request.form.get("age", 0))
        current_year = datetime.now().year
        birth_year = current_year - age
        birth_date = f"{birth_year}-01-01"  # Default to January 1st

        new_patient = {
            "id": get_next_patient_id(),
            "first_name": request.form.get("first_name", "").strip(),
            "last_name": request.form.get("last_name", "").strip(),
            "gender": request.form.get("gender", "").strip(),
            "birth_date": birth_date,
            "contact_no": "",
            "barangay": ""
        }

        add_patient(new_patient)

        # Parse blood pressure (format: "120/80")
        blood_pressure = request.form.get("blood_pressure", "").strip()
        try:
            bp_parts = blood_pressure.split("/")
            systolic = int(bp_parts[0]) if len(bp_parts) > 0 else 0
            diastolic = int(bp_parts[1]) if len(bp_parts) > 1 else 0
        except:
            systolic = 0
            diastolic = 0

        body_temp = float(request.form.get("body_temp"))
        heart_rate = int(request.form.get("heart_rate"))
        oxygen_saturation = int(request.form.get("oxygen_saturation"))
        height = float(request.form.get("height"))
        weight = float(request.form.get("weight"))
        bmi_input = request.form.get("bmi", "").strip()

        # Calculate BMI if not provided
        if bmi_input:
            bmi = float(bmi_input)
        else:
            bmi = calculate_bmi(height, weight)

        new_record = create_health_record(
            patient_id=new_patient["id"],
            temperature=body_temp,
            heart_rate=heart_rate,
            oxygen_saturation=oxygen_saturation,
            systolic=systolic,
            diastolic=diastolic,
            height=height,
            weight=weight
        )

        add_access_log(
            user=get_current_admin_name(),
            role=get_current_admin_role(),
            action=f'Added patient manually with initial health record for {new_patient["first_name"]} {new_patient["last_name"]}'
        )

        flash("Patient and initial health record saved successfully.", "success")
        return redirect(url_for("patients_page"))

    return render_template(
        "admin/add_patient.html",
        title="Add Patient Manually",
        active_page="patients"
    )


@app.route("/ehr-records")
@login_required
def ehr_records_page():
    return render_template(
        "admin/ehr_records.html",
        title="Electronic Health Records",
        active_page="ehr_records",
        patient_summaries=ehr_patient_summaries()
    )


@app.route("/ehr-records/patient/<int:patient_id>")
@login_required
def patient_record_history_page(patient_id):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        flash("Patient record not found.", "error")
        return redirect(url_for("ehr_records_page"))

    patient_records = list(reversed(get_records_for_patient(patient_id)))
    latest_record = patient_records[0] if patient_records else None

    add_access_log(
        user=get_current_admin_name(),
        role=get_current_admin_role(),
        action=f'Viewed health record history for {patient["first_name"]} {patient["last_name"]}'
    )

    return render_template(
        "admin/patient_record_history.html",
        title="Patient Health Records",
        active_page="ehr_records",
        patient=patient,
        records=patient_records,
        latest_record=latest_record
    )


@app.route("/download-patient-history/<int:patient_id>")
@login_required
def download_patient_history(patient_id):
    patient = get_patient_by_id(patient_id)

    if patient is None:
        flash("Patient record not found.", "error")
        return redirect(url_for("ehr_records_page"))

    patient_records = list(reversed(get_records_for_patient(patient_id)))

    patient_name = f'{patient["first_name"]} {patient["last_name"]}'
    generated_at = datetime.now().strftime("%Y-%m-%d %I:%M %p")

    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    story.append(Paragraph("E-Wellness Patient Health History", title_style))
    story.append(Spacer(1, 12))

    patient_info = f"""
    <b>Patient Name:</b> {patient_name}<br/>
    <b>Gender:</b> {patient["gender"]}<br/>
    <b>Birth Date:</b> {patient["birth_date"]}<br/>
    <b>Contact Number:</b> {patient["contact_no"]}<br/>
    <b>Barangay:</b> {patient["barangay"]}<br/>
    <b>Generated At:</b> {generated_at}
    """

    story.append(Paragraph(patient_info, normal_style))
    story.append(Spacer(1, 16))

    total_records = len(patient_records)
    latest_record = patient_records[0] if patient_records else None

    if latest_record:
        # Display status - if normal or needs attention with normal BMI, show "Normal"
        if latest_record["status"] == "Normal" or (latest_record["status"] == "Needs Attention" and latest_record["bmi_category"] == "Normal"):
            display_status = "Normal"
        else:
            display_status = latest_record["status"]

        summary_info = f"""
        <b>Total Records:</b> {total_records}<br/>
        <b>Latest BMI:</b> {latest_record["bmi"]} ({latest_record["bmi_category"]})<br/>
        <b>Latest Status:</b> {display_status}<br/>
        <b>Latest Record Date:</b> {latest_record["created_at"]}
        """
    else:
        summary_info = """
        <b>Total Records:</b> 0<br/>
        <b>Latest BMI:</b> No record yet<br/>
        <b>Latest Status:</b> No record yet<br/>
        <b>Latest Record Date:</b> No record yet
        """

    story.append(Paragraph("Patient Summary", heading_style))
    story.append(Paragraph(summary_info, normal_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("Health Record History", heading_style))
    story.append(Spacer(1, 10))

    if patient_records:
        table_data = [
            [
                "Date",
                "Vitals",
                "BMI",
                "Status",
                "Remarks"
            ]
        ]

        for record in patient_records:
            vitals = (
                f'Temp: {record["temperature"]} deg C<br/>'
                f'HR: {record["heart_rate"]} bpm<br/>'
                f'SpO2: {record["oxygen_saturation"]}%<br/>'
                f'BP: {record["blood_pressure"]}<br/>'
                f'Height: {record["height"]} cm<br/>'
                f'Weight: {record["weight"]} kg'
            )

            bmi = (
                f'{record["bmi"]}<br/>'
                f'{record["bmi_category"]}'
            )

            # Display status - if normal or needs attention with normal BMI, show "Normal"
            if record["status"] == "Normal" or (record["status"] == "Needs Attention" and record["bmi_category"] == "Normal"):
                display_status = "Normal"
            else:
                display_status = record["status"]

            table_data.append([
                Paragraph(str(record["created_at"]), normal_style),
                Paragraph(vitals, normal_style),
                Paragraph(bmi, normal_style),
                Paragraph(display_status, normal_style),
                Paragraph(str(record["remarks"]), normal_style)
            ])

        table = Table(
            table_data,
            colWidths=[
                1.25 * inch,
                1.55 * inch,
                0.85 * inch,
                1.05 * inch,
                1.55 * inch
            ],
            repeatRows=1
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f6bff")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 7.5),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dce8f7")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ffffff"))
        ]))

        story.append(table)
    else:
        story.append(Paragraph("No health records available for this patient.", normal_style))

    story.append(Spacer(1, 18))

    footer_text = (
        "Generated by E-Wellness Health Monitoring EHR System. "
        "This document is intended for healthcare monitoring and patient record review."
    )

    story.append(Paragraph(footer_text, normal_style))

    pdf.build(story)
    buffer.seek(0)

    add_access_log(
        user=get_current_admin_name(),
        role=get_current_admin_role(),
        action=f"Downloaded health history PDF for {patient_name}"
    )

    flash("Patient history PDF generated successfully.", "success")

    filename = f"{make_safe_filename(patient_name)}_health_history.pdf"

    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )


@app.route("/add-health-record", methods=["GET", "POST"])
@login_required
def add_health_record_page():
    selected_patient_id = request.args.get("patient_id", type=int)

    if request.method == "POST":
        patient_id = int(request.form.get("patient_id"))

        temperature = float(request.form.get("temperature"))
        heart_rate = int(request.form.get("heart_rate"))
        oxygen_saturation = int(request.form.get("oxygen_saturation"))
        systolic = int(request.form.get("systolic"))
        diastolic = int(request.form.get("diastolic"))
        height = float(request.form.get("height"))
        weight = float(request.form.get("weight"))

        new_record = create_health_record(
            patient_id=patient_id,
            temperature=temperature,
            heart_rate=heart_rate,
            oxygen_saturation=oxygen_saturation,
            systolic=systolic,
            diastolic=diastolic,
            height=height,
            weight=weight
        )

        add_access_log(
            user=get_current_admin_name(),
            role=get_current_admin_role(),
            action=f'Added follow-up health record for {new_record["C"]} {new_record["D"]}'
        )

        flash("Health record added successfully.", "success")
        return redirect(url_for("patient_record_history_page", patient_id=patient_id))

    if not selected_patient_id:
        flash("Please select a patient before adding a health record.", "warning")
        return redirect(url_for("patients_page"))

    selected_patient = get_patient_by_id(selected_patient_id)

    if not selected_patient:
        flash("Patient record not found.", "error")
        return redirect(url_for("patients_page"))

    return render_template(
        "admin/add_health_record.html",
        title="Add Health Record",
        active_page="ehr_records",
        selected_patient=selected_patient
    )


@app.route("/reports")
@login_required
def reports_page():
    records_list = get_records()
    return render_template(
        "admin/reports.html",
        title="Reports and Analytics",
        active_page="reports",
        stats=dashboard_stats(),
        bmi_trends=bmi_trends(),
        status_trends=status_trends(),
        bmi_chart_records=bmi_chart_records(),
        records=list(reversed(records_list))
    )


@app.route("/security")
@login_required
def security_page():
    return render_template(
        "admin/security.html",
        title="Security and Audit Logs",
        active_page="security",
        logs=get_access_logs()
    )


# --------------------------------------------------
# DATA IMPORT ROUTES
# --------------------------------------------------

@app.route("/import")
@login_required
def import_data_page():
    return render_template(
        "admin/import_data.html",
        title="Import Data",
        active_page="import"
    )


@app.route("/import/kiosk", methods=["POST"])
@login_required
def import_kiosk_data():
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("import_data_page"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("import_data_page"))

    try:
        if file.filename.endswith(".json"):
            imported_count = import_kiosk_json(file)
            flash(f"Successfully imported {imported_count} kiosk records.", "success")
        else:
            flash("Invalid file format. Please upload JSON.", "error")
            return redirect(url_for("import_data_page"))

        add_access_log(
            user=get_current_admin_name(),
            role=get_current_admin_role(),
            action=f"Imported {imported_count} kiosk records from {file.filename}"
        )

    except Exception as e:
        flash(f"Error importing kiosk data: {str(e)}", "error")
        return redirect(url_for("import_data_page"))

    return redirect(url_for("import_data_page"))


@app.route("/import/patients", methods=["POST"])
@login_required
def import_patients():
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("import_data_page"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("import_data_page"))

    try:
        if file.filename.endswith(".csv"):
            imported_count = import_patients_from_csv(file)
            flash(f"Successfully imported {imported_count} patients from CSV.", "success")
        elif file.filename.endswith(".json"):
            imported_count = import_patients_from_json(file)
            flash(f"Successfully imported {imported_count} patients from JSON.", "success")
        else:
            flash("Invalid file format. Please upload CSV or JSON.", "error")
            return redirect(url_for("import_data_page"))

        add_access_log(
            user=get_current_admin_name(),
            role=get_current_admin_role(),
            action=f"Imported {imported_count} patients from {file.filename}"
        )

    except Exception as e:
        flash(f"Error importing patients: {str(e)}", "error")
        return redirect(url_for("import_data_page"))

    return redirect(url_for("import_data_page"))


@app.route("/import/records", methods=["POST"])
@login_required
def import_records():
    if "file" not in request.files:
        flash("No file selected.", "error")
        return redirect(url_for("import_data_page"))

    file = request.files["file"]
    if file.filename == "":
        flash("No file selected.", "error")
        return redirect(url_for("import_data_page"))

    try:
        if file.filename.endswith(".csv"):
            imported_count = import_records_from_csv(file)
            flash(f"Successfully imported {imported_count} health records from CSV.", "success")
        elif file.filename.endswith(".json"):
            imported_count = import_records_from_json(file)
            flash(f"Successfully imported {imported_count} health records from JSON.", "success")
        else:
            flash("Invalid file format. Please upload CSV or JSON.", "error")
            return redirect(url_for("import_data_page"))

        add_access_log(
            user=get_current_admin_name(),
            role=get_current_admin_role(),
            action=f"Imported {imported_count} health records from {file.filename}"
        )

    except Exception as e:
        flash(f"Error importing health records: {str(e)}", "error")
        return redirect(url_for("import_data_page"))

    return redirect(url_for("import_data_page"))


def import_patients_from_csv(file):
    imported_count = 0
    patients_list = get_patients()
    existing_ids = {p["id"] for p in patients_list}
    max_id = max(existing_ids) if existing_ids else 0

    csv_reader = csv.DictReader(file.read().decode("utf-8").splitlines())
    for row in csv_reader:
        max_id += 1
        new_patient = {
            "id": max_id,
            "first_name": row.get("first_name", "").strip(),
            "last_name": row.get("last_name", "").strip(),
            "gender": row.get("gender", "Not specified").strip(),
            "birth_date": row.get("birth_date", "").strip(),
            "contact_no": row.get("contact_no", "").strip(),
            "barangay": row.get("barangay", "").strip()
        }
        add_patient(new_patient)
        imported_count += 1

    return imported_count


def import_patients_from_json(file):
    imported_count = 0
    data = json.load(file)
    patients_list = get_patients()
    existing_ids = {p["id"] for p in patients_list}
    max_id = max(existing_ids) if existing_ids else 0

    for patient_data in data:
        max_id += 1
        new_patient = {
            "id": max_id,
            "first_name": patient_data.get("first_name", "").strip(),
            "last_name": patient_data.get("last_name", "").strip(),
            "gender": patient_data.get("gender", "Not specified").strip(),
            "birth_date": patient_data.get("birth_date", "").strip(),
            "contact_no": patient_data.get("contact_no", "").strip(),
            "barangay": patient_data.get("barangay", "").strip()
        }
        add_patient(new_patient)
        imported_count += 1

    return imported_count


def import_records_from_csv(file):
    imported_count = 0
    records_list = get_records()
    existing_ids = {r["id"] for r in records_list}
    max_id = max(existing_ids) if existing_ids else 0

    csv_reader = csv.DictReader(file.read().decode("utf-8").splitlines())
    for row in csv_reader:
        max_id += 1
        patient_id = int(row.get("patient_id", 0))
        patient = get_patient_by_id(patient_id)

        if not patient:
            continue

        temperature = float(row.get("temperature", 0))
        heart_rate = int(row.get("heart_rate", 0))
        oxygen_saturation = int(row.get("oxygen_saturation", 0))
        systolic = int(row.get("systolic", 0))
        diastolic = int(row.get("diastolic", 0))
        height = float(row.get("height", 0))
        weight = float(row.get("weight", 0))

        new_record = create_health_record(
            patient_id=patient_id,
            temperature=temperature,
            heart_rate=heart_rate,
            oxygen_saturation=oxygen_saturation,
            systolic=systolic,
            diastolic=diastolic,
            height=height,
            weight=weight
        )
        imported_count += 1

    return imported_count


def import_records_from_json(file):
    imported_count = 0
    data = json.load(file)
    records_list = get_records()
    existing_ids = {r["id"] for r in records_list}
    max_id = max(existing_ids) if existing_ids else 0

    for record_data in data:
        max_id += 1
        patient_id = int(record_data.get("patient_id", 0))
        patient = get_patient_by_id(patient_id)

        if not patient:
            continue

        temperature = float(record_data.get("temperature", 0))
        heart_rate = int(record_data.get("heart_rate", 0))
        oxygen_saturation = int(record_data.get("oxygen_saturation", 0))
        systolic = int(record_data.get("systolic", 0))
        diastolic = int(record_data.get("diastolic", 0))
        height = float(record_data.get("height", 0))
        weight = float(record_data.get("weight", 0))

        new_record = create_health_record(
            patient_id=patient_id,
            temperature=temperature,
            heart_rate=heart_rate,
            oxygen_saturation=oxygen_saturation,
            systolic=systolic,
            diastolic=diastolic,
            height=height,
            weight=weight
        )
        imported_count += 1

    return imported_count


def import_kiosk_json(file):
    imported_count = 0
    data = json.load(file)

    # Handle both single record and array of records
    if isinstance(data, dict):
        data = [data]

    patients_list = get_patients()
    records_list = get_records()
    existing_patient_ids = {p["id"] for p in patients_list}
    max_patient_id = max(existing_patient_ids) if existing_patient_ids else 0
    existing_record_ids = {r["id"] for r in records_list}
    max_record_id = max(existing_record_ids) if existing_record_ids else 0

    for record in data:
        # Parse kiosk format with letter keys
        first_name = record.get("C", "").strip()
        last_name = record.get("D", "").strip()
        age_str = record.get("E", "0")
        gender = record.get("F", "").strip()
        blood_pressure = record.get("G", "").strip()
        heart_rate_str = record.get("H", "0")
        oxygen_saturation_str = record.get("I", "0")
        body_temp_str = record.get("J", "0")
        weight_str = record.get("K", "0")
        height_str = record.get("L", "0")
        bmi_str = record.get("M", "0")

        # Skip header rows (if values are field names)
        if age_str == "Age" or first_name == "FirstName":
            continue

        # Convert to appropriate types with error handling
        try:
            age = int(age_str)
        except:
            age = 0

        try:
            heart_rate = int(heart_rate_str)
        except:
            heart_rate = 0

        try:
            oxygen_saturation = int(oxygen_saturation_str)
        except:
            oxygen_saturation = 0

        try:
            body_temp = float(body_temp_str)
        except:
            body_temp = 0.0

        try:
            weight = float(weight_str)
        except:
            weight = 0.0

        try:
            height = float(height_str)
        except:
            height = 0.0

        try:
            bmi = float(bmi_str)
        except:
            bmi = 0.0

        # Check if patient already exists (by name)
        existing_patient = None
        for patient in patients_list:
            if patient["first_name"] == first_name and patient["last_name"] == last_name:
                existing_patient = patient
                break

        if not existing_patient:
            # Create new patient
            max_patient_id += 1
            # Calculate birth date from age
            current_year = datetime.now().year
            birth_year = current_year - age
            birth_date = f"{birth_year}-01-01"  # Default to January 1st

            new_patient = {
                "id": max_patient_id,
                "first_name": first_name,
                "last_name": last_name,
                "gender": gender,
                "birth_date": birth_date,
                "contact_no": "",
                "barangay": ""
            }
            add_patient(new_patient)
            patients_list.append(new_patient)
            patient_id = max_patient_id
        else:
            patient_id = existing_patient["id"]

        # Parse blood pressure (format: "120/80")
        try:
            bp_parts = blood_pressure.split("/")
            systolic = int(bp_parts[0]) if len(bp_parts) > 0 else 0
            diastolic = int(bp_parts[1]) if len(bp_parts) > 1 else 0
        except:
            systolic = 0
            diastolic = 0

        # Create health record
        max_record_id += 1
        new_record = create_health_record(
            patient_id=patient_id,
            temperature=body_temp,
            heart_rate=heart_rate,
            oxygen_saturation=oxygen_saturation,
            systolic=systolic,
            diastolic=diastolic,
            height=height,
            weight=weight
        )
        imported_count += 1

    return imported_count


# --------------------------------------------------
# SAMPLE API ROUTES FOR BACKEND PROGRAMMER
# --------------------------------------------------

@app.route("/api/dashboard-data")
@login_required
def api_dashboard_data():
    return jsonify({
        "stats": dashboard_stats(),
        "bmi_trends": bmi_trends(),
        "status_trends": status_trends(),
        "bmi_chart_records": bmi_chart_records()
    })


@app.route("/api/records")
@login_required
def api_records():
    return jsonify(get_records())


@app.route("/api/patients")
@login_required
def api_patients():
    return jsonify(get_patients())


if __name__ == "__main__":
    app.run(debug=True)