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

# --- INPUT FIELDS ---
name = st.text_input("Customer Name")
vehicle = st.text_input("Vehicle Name")

col1, col2 = st.columns(2)
with col1:
    price = st.number_input("Ex-Showroom Price", min_value=0)
    down_payment = st.number_input("Down Payment", min_value=0)
with col2:
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1)
    tenure = st.number_input("Tenure (Months)", min_value=1, step=1)

fc_charges = st.number_input("FC Charges", min_value=0)
additional_charges = st.number_input("Additional Charges", min_value=0)

# --- CALCULATIONS ---
loan_amount = price - down_payment
total_interest = (loan_amount * interest_rate * (tenure/12)) / 100
total_payable = loan_amount + total_interest + fc_charges + additional_charges
emi = total_payable / tenure

st.divider()
st.subheader(f"Loan Amount: ₹{loan_amount}")
st.subheader(f"Monthly EMI: ₹{round(emi, 2)}")
st.write(f"**Total Payable Amount:** ₹{round(total_payable, 2)}")

# --- PDF GENERATOR ---
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
    c.drawString(50, 640, f"Loan Amount: Rs. {loan_amount}")
    c.drawString(50, 620, f"Interest Rate: {interest_rate}% for {tenure} months")
    c.drawString(50, 600, f"FC Charges: Rs. {fc_charges}")
    c.drawString(50, 580, f"Additional Charges: Rs. {additional_charges}")
    
    c.setFont("Helvetica-Bold", 14)
    c.line(50, 560, 550, 560)
    c.drawString(50, 540, f"Monthly EMI: Rs. {round(emi, 2)}")
    c.drawString(50, 520, f"Total Amount Payable: Rs. {round(total_payable, 2)}")
    
    c.save()
    return file_name

if st.button("Generate PDF Quotation"):
    if name:
        pdf_file = export_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button("Click here to Download PDF", f, file_name=pdf_file)
    else:
        st.error("Please enter Customer Name")
