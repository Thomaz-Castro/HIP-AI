from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from db import db
from models import User, Patient, Doctor, Report
from utils import hash_password, verify_password, generate_pdf
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hypertension.db'
app.config['SECRET_KEY'] = 'secret123'
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password=hash_password("admin123"), role="admin")
        db.session.add(admin)
        db.session.commit()

@app.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        elif current_user.role == "doctor":
            return redirect(url_for("doctor_dashboard"))
        elif current_user.role == "patient":
            return redirect(url_for("patient_dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and verify_password(password, user.password):
            login_user(user)
            return redirect(url_for("index"))
        flash("Credenciais inválidas")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("index"))
    users = User.query.all()
    return render_template("admin.html", users=users)

@app.route("/doctor")
@login_required
def doctor_dashboard():
    if current_user.role != "doctor":
        return redirect(url_for("index"))
    patients = Patient.query.all()
    return render_template("doctor.html", patients=patients)

@app.route("/doctor/report/<int:patient_id>", methods=["GET", "POST"])
@login_required
def create_report(patient_id):
    if current_user.role != "doctor":
        return redirect(url_for("index"))
    if request.method == "POST":
        content = request.form["content"]
        patient = Patient.query.get(patient_id)
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        report = Report(patient_id=patient.id, doctor_id=doctor.id, content=content)
        db.session.add(report)
        db.session.commit()
        flash("Relatório criado com sucesso!")
        return redirect(url_for("doctor_dashboard"))
    return render_template("report.html", patient_id=patient_id)

@app.route("/report/<int:report_id>/pdf")
@login_required
def download_report(report_id):
    report = Report.query.get(report_id)
    filename = f"report_{report_id}.pdf"
    generate_pdf(report.content, filename)
    return send_file(filename, as_attachment=True)

@app.route("/patient")
@login_required
def patient_dashboard():
    if current_user.role != "patient":
        return redirect(url_for("index"))
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    reports = Report.query.filter_by(patient_id=patient.id).all()
    return render_template("patient.html", reports=reports)

if __name__ == "__main__":
    app.run(debug=True)
