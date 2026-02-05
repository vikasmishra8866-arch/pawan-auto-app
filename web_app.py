import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors # Colors ke liye
import datetime
import io
import pytz 

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

# Page Setup
st.set_page_config(page_title="Pawan Finance Premium", page_icon="🏦")

st.title("🏦 PAWAN AUTO FINANCE")
st.subheader("Professional Quotation Generator") 

# Input Section
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)
with col1:
    price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Type Price...")
    down = st.number_input("Down Payment (Rs)", value=None, placeholder="Type Down Payment...")
    file_charges = st.number_input("File Charges (Rs)", value=None, placeholder="Type File Charges...")
with col2:
    other_charges = st.number_input("Other Charges (Rs)", value=None, placeholder="Type Other Charges...")
    roi = st.number_input("Flat Interest Rate (%)", value=18.0)

# Calculations
p_val = price if price is not None else 0
d_val = down if down is not None else 0
f_val = file_charges if file_charges is not None else 0
o_val = other_charges if other_charges is not None else 0
loan_amt = (p_val - d_val) + f_val + o_val

if st.button("Generate Professional PDF"):
    if not cust_name or not veh_name or price is None:
        st.error("Please fill all details!")
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # --- HEADER DESIGN ---
        c.setFillColor(colors.HexColor("#1e3d59")) # Dark Blue Theme
        c.rect(0, 750, 600, 100, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(300, 790, "PAWAN AUTO FINANCE")
        c.setFont("Helvetica", 12)
        c.drawCentredString(300, 770, "Reliable Finance for Your Dream Vehicle")
        
        # --- CUSTOMER & DATE DETAILS ---
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, f"Customer Name: {cust_name.upper()}")
        c.drawString(50, 700, f"Vehicle Model: {veh_name.upper()}")
        c.drawRightString(540, 720, f"Date: {current_time}")
        c.line(50, 690, 540, 690)

        # --- FINANCIAL DETAILS ---
        y = 660
        data = [
            ("Ex-Showroom Price", f"Rs. {p_val:,.2f}"),
            ("Down Payment", f"Rs. {d_val:,.2f}"),
            ("File Charges", f"Rs. {f_val:,.2f}"),
            ("Other Charges", f"Rs. {o_val:,.2f}"),
            ("Net Loan Amount", f"Rs. {loan_amt:,.2f}"),
            ("Interest Rate", f"{roi}% (Flat)")
        ]
        
        for label, val in data:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, label)
            c.setFont("Helvetica", 12)
            c.drawRightString(520, y, val)
            y -= 25
        
        c.line(50, y+10, 540, y+10)

        # --- EMI TABLE DESIGN ---
        y -= 30
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(50, y-10, 490, 30, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(300, y, "EMI REPAYMENT OPTIONS")
        
        c.setFillColor(colors.black)
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y, "Tenure (Months)")
        c.drawRightString(500, y, "Monthly EMI (Rs)")
        c.line(50, y-5, 540, y-5)
        
        y -= 25
        for m in [12, 18, 24, 36]:
            emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            c.setFont("Helvetica", 12)
            c.drawString(80, y, f"{m} Months Plan")
            c.drawRightString(500, y, f"{emi:,.2f}")
            y -= 25
            
        # --- FOOTER ---
        c.line(50, 100, 540, 100)
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(50, 80, "* This is a computer-generated quotation.")
        c.drawRightString(540, 80, "Authorized Signatory")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(540, 65, "Vikas Mishra")

        c.save()
        st.success("Professional PDF Generated!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
