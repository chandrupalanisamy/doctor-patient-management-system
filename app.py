from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_file
import mysql.connector
import math
import os
import base64
from hashlib import sha256
from cryptography.fernet import Fernet
from fpdf import FPDF
import io

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Uploads folder ---
UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Database connection ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # put your MySQL password
    database="hospital_management"
)
cursor = db.cursor(dictionary=True)

# Haversine function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_fernet(nurse_key):
    derived_key = base64.urlsafe_b64encode(sha256(nurse_key.encode()).digest())
    return Fernet(derived_key)

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type = request.form["user_type"]
        username_email = request.form["username_email"]
        password = request.form["password"]
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        if user_type == "admin":
            cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username_email, password))
            user = cursor.fetchone()
            if user:
                if latitude and longitude:
                    cursor.execute("UPDATE admin SET latitude=%s, longitude=%s WHERE id=%s",
                                   (latitude, longitude, user["id"]))
                    db.commit()
                session["user_type"] = "admin"
                session["user_id"] = user["id"]
                return redirect("/admin_dashboard")

        elif user_type == "nurse":
            cursor.execute("SELECT * FROM nurse WHERE email=%s AND password=%s", (username_email, password))
            user = cursor.fetchone()
            if user:
                session["user_type"] = "nurse"
                session["user_id"] = user["id"]
                return redirect("/nurse_dashboard")

        elif user_type == "doctor":
            cursor.execute("SELECT * FROM doctor WHERE email=%s AND password=%s", (username_email, password))
            user = cursor.fetchone()
            if user:
                cursor.execute("SELECT latitude, longitude FROM admin ORDER BY id DESC LIMIT 1")
                admin_loc = cursor.fetchone()
                if not admin_loc or not admin_loc["latitude"] or not admin_loc["longitude"]:
                    flash("Admin location not set! Doctor login restricted.")
                    return redirect("/")
                if latitude and longitude:
                    distance = haversine(latitude, longitude, admin_loc["latitude"], admin_loc["longitude"])
                    if distance <= 5:
                        cursor.execute("UPDATE doctor SET latitude=%s, longitude=%s WHERE id=%s",
                                       (latitude, longitude, user["id"]))
                        db.commit()
                        session["user_type"] = "doctor"
                        session["user_id"] = user["id"]
                        return redirect("/doctor_dashboard")
                    else:
                        flash("You are not within the allowed login area!")
                        return redirect("/")
                else:
                    flash("Latitude and longitude required for doctor login!")
                    return redirect("/")

        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("user_type") != "admin":
        return redirect("/")
    return render_template("admin_dashboard.html")

@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if session.get("user_type") != "admin":
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        cursor.execute("INSERT INTO patient(name, age, gender, email, mobile) VALUES (%s,%s,%s,%s,%s)",
                       (name, age, gender, email, mobile))
        db.commit()
        flash("Patient added successfully!")
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    return render_template("add_patient.html", patients=patients)

@app.route("/add_nurse", methods=["GET", "POST"])
def add_nurse():
    if session.get("user_type") != "admin":
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        mobile = request.form["mobile"]
        key = request.form["key"]
        cursor.execute("INSERT INTO nurse(name,email,password,mobile,`key`) VALUES(%s,%s,%s,%s,%s)",
                       (name, email, password, mobile, key))
        db.commit()
        flash("Nurse added successfully!")
    cursor.execute("SELECT * FROM nurse")
    nurses = cursor.fetchall()
    return render_template("add_nurse.html", nurses=nurses)

@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():
    if session.get("user_type") != "admin":
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        mobile = request.form["mobile"]
        specialist = request.form["specialist"]
        cursor.execute("INSERT INTO doctor(name,email,password,mobile,specialist) VALUES(%s,%s,%s,%s,%s)",
                       (name, email, password, mobile, specialist))
        db.commit()
        flash("Doctor added successfully!")
    cursor.execute("SELECT * FROM doctor")
    doctors = cursor.fetchall()
    return render_template("add_doctor.html", doctors=doctors)

@app.route("/allot_patient", methods=["GET", "POST"])
def allot_patient():
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM doctor")
    doctors = cursor.fetchall()
    if request.method == "POST":
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']
        cursor.execute("INSERT INTO allot_patient (patient_id, doctor_id) VALUES (%s,%s)", (patient_id, doctor_id))
        db.commit()
        flash("Patient allotted successfully!")
        return redirect("/allot_patient")
    cursor.execute("""
        SELECT ap.id, p.name AS patient_name, d.name AS doctor_name, d.specialist
        FROM allot_patient ap
        JOIN patient p ON ap.patient_id = p.id
        JOIN doctor d ON ap.doctor_id = d.id
        ORDER BY ap.id DESC
    """)
    allotments = cursor.fetchall()
    return render_template("allot_patient.html", patients=patients, doctors=doctors, allotments=allotments)

@app.route("/nurse_dashboard")
def nurse_dashboard():
    if session.get("user_type") != "nurse":
        return redirect("/")
    return render_template("nurse_dashboard.html")

# --- FEATURE 1: Add Report with optional file upload & encryption ---
@app.route("/add_report", methods=["GET", "POST"])
def add_report():
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        temperature = request.form["temperature"]
        pulse_rate = request.form["pulse_rate"]
        spo2 = request.form["spo2"]
        height_cm = request.form["height_cm"]
        weight_kg = request.form["weight_kg"]
        cursor.execute("""INSERT INTO report(patient_id, temperature, pulse_rate, spo2, height_cm, weight_kg)
                          VALUES (%s,%s,%s,%s,%s,%s)""",
                       (patient_id, temperature, pulse_rate, spo2, height_cm, weight_kg))
        db.commit()
        report_id = cursor.lastrowid

        # Handle optional file upload with encryption
        uploaded_file = request.files.get("report_file")
        if uploaded_file and uploaded_file.filename:
            nurse_id = session.get("user_id")
            cursor.execute("SELECT `key` FROM nurse WHERE id=%s", (nurse_id,))
            nurse = cursor.fetchone()
            if nurse and nurse["key"]:
                fernet = get_fernet(nurse["key"])
                file_bytes = uploaded_file.read()
                enc_bytes = fernet.encrypt(file_bytes)
                original_filename = uploaded_file.filename
                enc_filename = f"report_{report_id}_{original_filename}.enc"
                enc_file_path = os.path.join(UPLOAD_FOLDER, enc_filename)
                with open(enc_file_path, 'wb') as f:
                    f.write(enc_bytes)

                # Encrypt the vitals too and store combined row
                enc_temperature = fernet.encrypt(temperature.encode()).decode()
                enc_pulse_rate = fernet.encrypt(pulse_rate.encode()).decode()
                enc_spo2 = fernet.encrypt(spo2.encode()).decode()
                enc_height_cm = fernet.encrypt(height_cm.encode()).decode()
                enc_weight_kg = fernet.encrypt(weight_kg.encode()).decode()

                cursor.execute("""
                    INSERT INTO report_enc (report_id, nurse_id, enc_temperature, enc_pulse_rate,
                        enc_spo2, enc_height_cm, enc_weight_kg, enc_file_path, original_filename)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (report_id, nurse_id, enc_temperature, enc_pulse_rate,
                      enc_spo2, enc_height_cm, enc_weight_kg,
                      enc_file_path, original_filename))
                db.commit()
                flash("Report and encrypted file saved successfully!")
            else:
                flash("Report added but file not encrypted — nurse key missing.")
        else:
            flash("Report added successfully!")

    cursor.execute("""SELECT r.id, p.name as patient_name, r.temperature, r.pulse_rate, r.spo2, r.height_cm, r.weight_kg
                      FROM report r JOIN patient p ON r.patient_id=p.id""")
    reports = cursor.fetchall()
    return render_template("add_report.html", patients=patients, reports=reports)

# ---------------- ENCRYPT REPORT (existing) ----------------
@app.route('/encrypt_report/<int:report_id>', methods=['POST'])
def encrypt_report(report_id):
    if session.get("user_type") != "nurse":
        flash("You must log in as a nurse first.")
        return redirect("/login")
    nurse_id = session.get("user_id")
    cursor.execute("SELECT `key` FROM nurse WHERE id=%s", (nurse_id,))
    nurse = cursor.fetchone()
    if not nurse or not nurse["key"]:
        flash("Encryption key not found for this nurse!")
        return redirect("/add_report")
    fernet = get_fernet(nurse["key"])
    cursor.execute("SELECT * FROM report WHERE id=%s", (report_id,))
    report = cursor.fetchone()
    if not report:
        flash("Report not found!")
        return redirect("/add_report")
    enc_temperature = fernet.encrypt(report["temperature"].encode()).decode()
    enc_pulse_rate = fernet.encrypt(report["pulse_rate"].encode()).decode()
    enc_spo2 = fernet.encrypt(report["spo2"].encode()).decode()
    enc_height_cm = fernet.encrypt(report["height_cm"].encode()).decode()
    enc_weight_kg = fernet.encrypt(report["weight_kg"].encode()).decode()
    cursor.execute("""
        INSERT INTO report_enc (report_id, nurse_id, enc_temperature, enc_pulse_rate, enc_spo2, enc_height_cm, enc_weight_kg)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (report_id, nurse_id, enc_temperature, enc_pulse_rate, enc_spo2, enc_height_cm, enc_weight_kg))
    db.commit()
    flash("Report encrypted and stored successfully!")
    return redirect("/add_report")

# --- FEATURE 2: View Encrypted Reports (nurse) with file info ---
@app.route("/view_report_enc_table")
def view_report_enc_table():
    if session.get("user_type") != "nurse":
        flash("You must log in as a nurse first.")
        return redirect("/")
    nurse_id = session.get("user_id")
    cursor.execute("""
        SELECT re.id, p.name as patient_name, re.enc_temperature, re.enc_pulse_rate,
               re.enc_spo2, re.enc_height_cm, re.enc_weight_kg,
               re.enc_file_path, re.original_filename
        FROM report_enc re
        JOIN report r ON re.report_id = r.id
        JOIN patient p ON r.patient_id = p.id
        WHERE re.nurse_id=%s
        ORDER BY re.id DESC
    """, (nurse_id,))
    enc_reports = cursor.fetchall()
    return render_template("view_report_enc_table.html", reports=enc_reports)

# --- NURSE: Decrypt vitals for display (uses nurse's own key, no prompt) ---
@app.route("/nurse/decrypt_vitals/<int:report_enc_id>")
def nurse_decrypt_vitals(report_enc_id):
    if session.get("user_type") != "nurse":
        return jsonify({"status": "error", "msg": "Unauthorized"}), 403
    nurse_id = session.get("user_id")
    cursor.execute("SELECT `key` FROM nurse WHERE id=%s", (nurse_id,))
    nurse = cursor.fetchone()
    if not nurse or not nurse["key"]:
        return jsonify({"status": "error", "msg": "Nurse key not found"})
    cursor.execute("SELECT * FROM report_enc WHERE id=%s AND nurse_id=%s", (report_enc_id, nurse_id))
    row = cursor.fetchone()
    if not row:
        return jsonify({"status": "error", "msg": "Report not found or not yours"})
    fernet = get_fernet(nurse["key"])
    decrypted = {
        "temperature": fernet.decrypt(row["enc_temperature"].encode()).decode(),
        "pulse_rate":  fernet.decrypt(row["enc_pulse_rate"].encode()).decode(),
        "spo2":        fernet.decrypt(row["enc_spo2"].encode()).decode(),
        "height_cm":   fernet.decrypt(row["enc_height_cm"].encode()).decode(),
        "weight_kg":   fernet.decrypt(row["enc_weight_kg"].encode()).decode(),
    }
    return jsonify({"status": "success", "report": decrypted})

# --- FEATURE 2: Download raw .enc file ---
@app.route("/nurse/download_enc_file/<int:report_enc_id>")
def nurse_download_enc_file(report_enc_id):
    if session.get("user_type") != "nurse":
        return redirect("/")
    cursor.execute("SELECT enc_file_path, original_filename FROM report_enc WHERE id=%s", (report_enc_id,))
    row = cursor.fetchone()
    if not row or not row["enc_file_path"]:
        flash("No encrypted file found.")
        return redirect("/view_report_enc_table")
    enc_filename = os.path.basename(row["enc_file_path"]) 
    return send_file(row["enc_file_path"], as_attachment=True, download_name=enc_filename)

# --- FEATURE 2: Decrypt file and send as download ---
@app.route("/nurse/decrypt_file/<int:report_enc_id>")
def nurse_decrypt_file(report_enc_id):
    if session.get("user_type") != "nurse":
        return redirect("/")
    nurse_id = session.get("user_id")
    cursor.execute("SELECT `key` FROM nurse WHERE id=%s", (nurse_id,))
    nurse = cursor.fetchone()
    if not nurse or not nurse["key"]:
        flash("Nurse key not found.")
        return redirect("/view_report_enc_table")
    cursor.execute("SELECT enc_file_path, original_filename, nurse_id FROM report_enc WHERE id=%s", (report_enc_id,))
    row = cursor.fetchone()
    if not row or not row["enc_file_path"]:
        flash("No encrypted file found.")
        return redirect("/view_report_enc_table")
    if row["nurse_id"] != nurse_id:
        flash("Unauthorized.")
        return redirect("/view_report_enc_table")
    fernet = get_fernet(nurse["key"])
    with open(row["enc_file_path"], 'rb') as f:
        enc_bytes = f.read()
    dec_bytes = fernet.decrypt(enc_bytes)
    return send_file(io.BytesIO(dec_bytes), as_attachment=True, download_name=row["original_filename"])

# --- Doctor Dashboard ---
@app.route("/doctor_dashboard")
def doctor_dashboard():
    if session.get("user_type") != "doctor":
        return redirect("/")
    return render_template("doctor_dashboard.html")

@app.route("/doctor/view_allotted_patients")
def doctor_view_allotted_patients():
    if session.get("user_type") != "doctor":
        return redirect("/")
    doctor_id = session.get("user_id")
    cursor.execute("""
        SELECT p.id, p.name, p.age, p.gender, p.email, p.mobile
        FROM allot_patient ap
        JOIN patient p ON ap.patient_id = p.id
        WHERE ap.doctor_id = %s
        ORDER BY ap.id DESC
    """, (doctor_id,))
    patients = cursor.fetchall()
    return render_template("doctor_allotted_patients.html", patients=patients)

# --- FEATURE 3 & 4: View Encrypted Reports (doctor) ---
@app.route("/doctor/view_encrypted_reports")
def doctor_view_encrypted_reports():
    if session.get("user_type") != "doctor":
        return redirect("/")
    doctor_id = session.get("user_id")
    cursor.execute("""
        SELECT re.id as report_enc_id, r.id as report_id, p.name as patient_name,
               re.enc_temperature, re.enc_pulse_rate, re.enc_spo2, re.enc_height_cm, re.enc_weight_kg,
               n.key as nurse_key, re.enc_file_path, re.original_filename
        FROM report_enc re
        JOIN report r ON re.report_id = r.id
        JOIN patient p ON r.patient_id = p.id
        JOIN nurse n ON re.nurse_id = n.id
        WHERE re.id IN (
            SELECT re2.id
            FROM report_enc re2
            JOIN report r2 ON re2.report_id = r2.id
            JOIN allot_patient ap ON r2.patient_id = ap.patient_id
            WHERE ap.doctor_id = %s
        )
        ORDER BY re.id DESC
    """, (doctor_id,))
    reports = cursor.fetchall()
    return render_template("doctor_view_reports.html", reports=reports)

# --- Decrypt report vitals (existing, unchanged) ---
@app.route("/doctor/decrypt_report", methods=["POST"])
def doctor_decrypt_report():
    if session.get("user_type") != "doctor":
        return jsonify({"status": "error", "msg": "Unauthorized"}), 403
    data = request.get_json()
    report_enc_id = data.get("report_enc_id")
    entered_key = data.get("key")
    cursor.execute("""
        SELECT re.*, n.key as nurse_key
        FROM report_enc re
        JOIN nurse n ON re.nurse_id = n.id
        WHERE re.id=%s
    """, (report_enc_id,))
    report_enc = cursor.fetchone()
    if not report_enc:
        return jsonify({"status": "error", "msg": "Report not found"})
    if entered_key != report_enc["nurse_key"]:
        return jsonify({"status": "error", "msg": "Invalid key"})
    fernet = get_fernet(report_enc["nurse_key"])
    decrypted_report = {
        "temperature": fernet.decrypt(report_enc["enc_temperature"].encode()).decode(),
        "pulse_rate": fernet.decrypt(report_enc["enc_pulse_rate"].encode()).decode(),
        "spo2": fernet.decrypt(report_enc["enc_spo2"].encode()).decode(),
        "height_cm": fernet.decrypt(report_enc["enc_height_cm"].encode()).decode(),
        "weight_kg": fernet.decrypt(report_enc["enc_weight_kg"].encode()).decode(),
        "has_file": bool(report_enc.get("enc_file_path"))
    }
    return jsonify({"status": "success", "report": decrypted_report})

# --- FEATURE 3: Doctor download decrypted file (via key in URL) ---
@app.route("/doctor/download_file_direct/<int:report_enc_id>")
def doctor_download_file_direct(report_enc_id):
    if session.get("user_type") != "doctor":
        return redirect("/")
    entered_key = request.args.get("key", "")
    cursor.execute("""
        SELECT re.enc_file_path, re.original_filename, n.key as nurse_key
        FROM report_enc re
        JOIN nurse n ON re.nurse_id = n.id
        WHERE re.id=%s
    """, (report_enc_id,))
    row = cursor.fetchone()
    if not row or not row["enc_file_path"]:
        return "No file found", 404
    if entered_key != row["nurse_key"]:
        return "Invalid key", 403
    fernet = get_fernet(row["nurse_key"])
    with open(row["enc_file_path"], 'rb') as f:
        enc_bytes = f.read()
    dec_bytes = fernet.decrypt(enc_bytes)
    return send_file(io.BytesIO(dec_bytes), as_attachment=True, download_name=row["original_filename"])

# --- FEATURE 4: Doctor download full PDF report ---
@app.route("/doctor/download_full_report/<int:report_enc_id>")
def doctor_download_full_report(report_enc_id):
    if session.get("user_type") != "doctor":
        return redirect("/")
    entered_key = request.args.get("key", "")
    cursor.execute("""
        SELECT re.*, n.key as nurse_key,
               p.name as patient_name, p.age, p.gender, p.email as patient_email, p.mobile as patient_mobile
        FROM report_enc re
        JOIN nurse n ON re.nurse_id = n.id
        JOIN report r ON re.report_id = r.id
        JOIN patient p ON r.patient_id = p.id
        WHERE re.id=%s
    """, (report_enc_id,))
    row = cursor.fetchone()
    if not row:
        return "Report not found", 404
    if entered_key != row["nurse_key"]:
        return "Invalid key", 403

    fernet = get_fernet(row["nurse_key"])
    temperature = fernet.decrypt(row["enc_temperature"].encode()).decode()
    pulse_rate = fernet.decrypt(row["enc_pulse_rate"].encode()).decode()
    spo2 = fernet.decrypt(row["enc_spo2"].encode()).decode()
    height_cm = fernet.decrypt(row["enc_height_cm"].encode()).decode()
    weight_kg = fernet.decrypt(row["enc_weight_kg"].encode()).decode()

    # Generate PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_fill_color(20, 21, 22)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 14, "City Hospital - Patient Medical Report", new_x="LMARGIN", new_y="NEXT", fill=True, align="C")
    pdf.ln(4)

    # Patient Details
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 21, 22)
    pdf.cell(0, 10, "Patient Details", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(50, 50, 50)
    details = [
        ("Name", row["patient_name"]),
        ("Age", str(row["age"])),
        ("Gender", row["gender"]),
        ("Email", row["patient_email"]),
        ("Mobile", row["patient_mobile"]),
    ]
    for label, value in details:
        pdf.cell(50, 8, f"{label}:", new_x="RIGHT", new_y="TOP")
        pdf.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Vital Signs
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 21, 22)
    pdf.cell(0, 10, "Vital Signs", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(17, 18, 19)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 9, "Measurement", border=1, fill=True, new_x="RIGHT", new_y="TOP")
    pdf.cell(0, 9, "Value", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(30, 30, 30)
    vitals = [
        ("Temperature (deg C)", temperature),
        ("Pulse Rate (bpm)", pulse_rate),
        ("SPO2 (%)", spo2),
        ("Height (cm)", height_cm),
        ("Weight (kg)", weight_kg),
    ]
    fill = False
    for label, value in vitals:
        pdf.set_fill_color(242, 242, 242) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(80, 8, label, border=1, fill=True, new_x="RIGHT", new_y="TOP")
        pdf.cell(0, 8, value, border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        fill = not fill
    pdf.ln(6)

    # Attached file note
    if row.get("enc_file_path") and row.get("original_filename"):
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 8, f"Attached File: {row['original_filename']}", new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = pdf.output()
    safe_name = row["patient_name"].replace(" ", "_")
    filename = f"patient_report_{safe_name}_{report_enc_id}.pdf"
    return send_file(io.BytesIO(bytes(pdf_bytes)), as_attachment=True, download_name=filename, mimetype="application/pdf")

if __name__ == "__main__":
    app.run(debug=True)
