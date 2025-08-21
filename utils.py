from passlib.hash import bcrypt
from fpdf import FPDF

def hash_password(password):
    return bcrypt.hash(password)

def verify_password(password, hashed):
    return bcrypt.verify(password, hashed)

def generate_pdf(report_text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, report_text)
    pdf.output(filename)
