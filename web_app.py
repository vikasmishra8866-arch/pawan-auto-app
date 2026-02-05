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
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, step=0.1, value=18.0)
    fc_charges = st.number_input("FC Charges", min_value=0)

additional_charges = st.number_input("Additional Charges", min_value=0)

# --- CALCULATIONS ---
loan_amount = price - down_payment

def calculate_emi(months):
    total_int = (loan_amount * interest_rate * (months/12)) / 100
    total_pay = loan_amount + total_int + fc_charges + additional_charges
    return round(total_pay / months, 2), round(total_pay, 2)

tenures = [12, 18, 24, 36]
results = {t: calculate_emi(t) for t in tenures}

st.divider()
st.subheader(f"Loan Amount: ₹{loan_amount}")

# Display EMIs in a table
st.write("### EMI Options")
st.table({
    "Tenure (Months)": [f"{t} Months" for t in tenures],
    "Monthly EMI": [f"₹{results[t][0]}" for t in tenures],
    "Total Payable": [f"₹{results[t][1]}" for t in tenures]
})

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
    c.drawString(50, 640, f"Net Loan Amount: Rs. {loan_amount}")
    c.drawString(50, 620, f"Interest Rate: {interest_rate}%")
    c.drawString(50, 600, f"FC + Addl Charges: Rs. {fc_charges + additional_charges}")
    
    c.setFont("Helvetica-Bold", 14)
    c.line(50, 580, 550, 580)
    c.drawString(50, 560, "EMI PLANS:")
    
    y = 530
    c.setFont("Helvetica", 12)
    for t in tenures:
        emi_val, total_val = results[t]
        c.drawString(50, y, f"{t} Months: EMI = Rs. {emi_val} | Total = Rs. {total_val}")
        y -= 25
    
    c.save()
    return file_name

if st.button("Generate PDF Quotation"):
    if name:
        pdf_file = export_pdf()
        with open(pdf_file, "rb") as f:
            st.download_button("Click here to Download PDF", f, file_name=pdf_file)
    else:
        st.error("Please enter Customer Name")
