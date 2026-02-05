import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime
import pytz 

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

st.set_page_config(page_title="PAWAN AUTO FINANCE", layout="centered")

st.title("🚗 PAWAN AUTO FINANCE")
st.write(f"**Date & Time:** {current_time}")

name = st.text_input("Customer Name")
vehicle = st.text_input("Vehicle Name")
price = st.number_input("Ex-Showroom Price", min_value=0)
down_payment = st.number_input("Down Payment", min_value=0)

loan_amount = price - down_payment
st.subheader(f"Loan Amount: ₹{loan_amount}")

def export_pdf():
    file_name = f"Quotation_{name}.pdf"
    c = canvas.Canvas(file_name, pagesize=A4)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, 800, "PAWAN AUTO FINANCE")
    c.setFont("Helvetica", 12)
    c.drawString(50, 750, f"Date & Time: {current_time}")
    c.drawString(50, 730, f"Customer: {name}")
    c.drawString(50, 710, f"Vehicle: {vehicle}")
    c.line(50, 700, 550, 700)
    c.drawString(50, 680, f"Ex-Showroom Price: Rs. {price}")
    c.drawString(50, 660, f"Down Payment: Rs. {down_payment}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 630, f"Net Loan Amount: Rs. {loan_amount}")
    c.save()
    return file_name

if st.button("Generate PDF Quotation"):
    if name:
        pdf_file = export_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button("Click here to Download PDF", f, file_name=pdf_file)
    else:
        st.error("Please enter Customer Name")
