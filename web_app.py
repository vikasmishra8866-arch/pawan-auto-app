import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import datetime
import io
import pytz 

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

# Page Setup
st.set_page_config(page_title="Pawan Auto Finance", page_icon="🏦")

# --- UI DESIGN ---
st.title("🏦 PAWAN AUTO FINANCE")
st.markdown(f"**Managed by: Vikas Mishra**") 
st.write(f"📅 {current_time}")

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
    # --- INTEREST TYPE SELECTION ---
    int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
    roi = st.number_input(f"{int_type} (%)", value=18.0)

# Calculations
p_val = price if price is not None else 0
d_val = down if down is not None else 0
f_val = file_charges if file_charges is not None else 0
o_val = other_charges if other_charges is not None else 0
loan_amt = (p_val - d_val) + f_val + o_val

if st.button("Generate Premium PDF Quotation"):
    if not cust_name or not veh_name or price is None:
        st.error("Please fill all details!")
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # --- WATERMARK (Light Grey Background Text) ---
        c.saveState()
        c.setFont("Helvetica-Bold", 50)
        c.setStrokeColor(colors.lightgrey)
        c.setFillColor(colors.lightgrey, alpha=0.15) # Halka dikhne ke liye alpha kam rakha hai
        c.translate(300, 450) # Page ke center mein
        c.rotate(45) # Tircha (diagonal) dikhne ke liye
        c.drawCentredString(0, 0, "PAWAN AUTO FINANCE")
        c.restoreState()
        
        # --- HEADER (Blue Theme) ---
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(0, 750, 600, 100, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(300, 795, "PAWAN AUTO FINANCE")
        
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(300, 775, "Fastest Loan Approval & Trusted Service")
        
        # --- DETAILS SECTION ---
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, f"CUSTOMER NAME: {cust_name.upper()}")
        c.drawString(50, 700, f"VEHICLE MODEL: {veh_name.upper()}")
        c.drawRightString(540, 720, f"DATE: {current_time}")
        c.line(50, 690, 540, 690)

        y = 660
        data = [
            ("Vehicle Price", f"Rs. {p_val:,.2f}"),
            ("Down Payment", f"Rs. {d_val:,.2f}"),
            ("File Charges", f"Rs. {f_val:,.2f}"),
            ("Other Charges", f"Rs. {o_val:,.2f}"),
            ("Net Loan Amount", f"Rs. {loan_amt:,.2f}"),
            ("Interest Rate", f"{roi}% ({int_type})")
        ]
        
        for label, val in data:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, label)
            c.setFont("Helvetica", 12)
            c.drawRightString(520, y, val)
            y -= 25
        
        c.line(50, y+10, 540, y+10)

        # --- EMI TABLE ---
        y -= 30
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(50, y-10, 490, 30, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(300, y, "EMI REPAYMENT OPTIONS")
        
        c.setFillColor(colors.black)
        y -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(80, y, "TENURE")
        c.drawRightString(500, y, "MONTHLY EMI (RS)")
        c.line(50, y-5, 540, y-5)
        
        y -= 25
        for m in [12, 18, 24, 36]:
            if int_type == "Flat Rate":
                emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else:
                # Reducing Balance Formula
                r = roi / (12 * 100)
                emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
                
            c.setFont("Helvetica", 12)
            c.drawString(80, y, f"{m} Months Plan")
            c.drawRightString(500, y, f"{emi:,.2f}")
            y -= 25
            
        # --- FOOTER ---
        c.line(50, 100, 540, 100)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 85, f"* This is a computer-generated quotation based on {int_type.lower()}.")
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(540, 85, "Authorized Signature")
        # --- UPDATED FIRM NAME ---
        c.drawRightString(540, 65, "AGARWAL ENTERPRISE")

        c.save()
        st.success(f"Professional PDF Generated for {cust_name}!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
