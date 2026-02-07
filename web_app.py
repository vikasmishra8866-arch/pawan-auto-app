import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import datetime
import io
import pytz 
import qrcode

# --- INDIAN TIME SETTING ---
IST = pytz.timezone('Asia/Kolkata')
current_time = datetime.datetime.now(IST).strftime("%d-%m-%Y %I:%M %p")

# Page Setup
st.set_page_config(page_title="Pawan Auto Finance", page_icon="🏦")

# --- UI DESIGN ---
st.title("🏦 PAWAN AUTO FINANCE")
st.subheader("Vehicle Purchase & Loan Quotation")
st.markdown(f"**Managed by: Vikas Mishra**") 
st.write(f"📅 {current_time}")

# --- SERVICE SELECTION ---
st.markdown("---")
service_type = st.radio("Select Service Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

# Input Section
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

# PDF Variables
pdf_data = []

if service_type == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None)
        down = st.number_input("Down Payment (Rs)", value=None)
        file_charges = st.number_input("File Charges (Rs)", value=None)
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None)
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    loan_amt = ((price or 0) - (down or 0)) + (file_charges or 0) + (other_charges or 0)
    pdf_data = [("Vehicle Price", price or 0), ("Down Payment", down or 0), ("File Charges", file_charges or 0), ("Other Charges", other_charges or 0)]

else: # LOAN ON VEHICLE (Extra Boxes Added)
    with col1:
        l_amt = st.number_input("Loan Amount (Rs)", value=None)
        ins_ch = st.number_input("Insurance Charges (Rs)", value=None)
        pass_ch = st.number_input("Passing Charges (Rs)", value=None)
        trans_ch = st.number_input("Transfer Charges (Rs)", value=None) # NEW
    with col2:
        hp_term = st.number_input("HP Terminate (Rs)", value=None) # NEW
        hp_add = st.number_input("HP Add (Rs)", value=None) # NEW
        oth_ch_loan = st.number_input("Other Charges (Rs)", value=None)
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    loan_amt = (l_amt or 0) + (ins_ch or 0) + (pass_ch or 0) + (trans_ch or 0) + (hp_term or 0) + (hp_add or 0) + (oth_ch_loan or 0)
    pdf_data = [("Loan Amount", l_amt or 0), ("Insurance Charges", ins_ch or 0), ("Passing Charges", pass_ch or 0), 
                ("Transfer Charges", trans_ch or 0), ("HP Terminate", hp_term or 0), ("HP Add", hp_add or 0), ("Other Charges", oth_ch_loan or 0)]

# --- LIVE PREVIEW ---
st.markdown("---")
st.subheader(f"📊 Live Preview: {service_type}")
if loan_amt > 0:
    all_tenures = [5, 10, 12, 15, 18, 24, 30, 36]
    for i in range(0, len(all_tenures), 4):
        cols = st.columns(4)
        for m, col in zip(all_tenures[i:i+4], cols):
            if int_type == "Flat Rate":
                emi_val = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else:
                r = roi / (12 * 100)
                emi_val = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            col.metric(f"{m} Mo", f"₹{emi_val:,.0f}")
            col.caption(f"Total: ₹{emi_val*m:,.0f}")

# --- PDF GENERATION ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or loan_amt == 0:
        st.error("Details bhariye!")
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # QR Code Generation
        qr = qrcode.QRCode(box_size=2)
        qr.add_data("https://share.google/2Cs3iSUypf5Lf9PpS")
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white")
        qr_buffer = io.BytesIO()
        img_qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        
        # Header (Agarwal Enterprise Added)
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(0, 750, 600, 100, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 26)
        c.drawCentredString(300, 810, "PAWAN AUTO FINANCE")
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(300, 790, "AGARWAL ENTERPRISE")
        c.setFont("Helvetica-Oblique", 11)
        c.drawCentredString(300, 770, f"Vehicle Loan Quotation" if service_type == "Loan on Vehicle" else "Vehicle Purchase Quotation")

        # Table & Data
        y = 660
        for label, val in pdf_data:
            c.setFont("Helvetica-Bold", 11)
            c.drawString(70, y, label.upper())
            c.drawRightString(520, y, f"Rs. {val:,.2f}")
            y -= 22
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, y-10, "NET LOAN AMOUNT")
        c.drawRightString(520, y-10, f"Rs. {loan_amt:,.2f}")
        
        # EMI Table (Coordinates same as before)
        y -= 50
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(50, y-10, 490, 25, fill=1)
        c.setFillColor(colors.white)
        c.drawCentredString(300, y, "REPAYMENT SCHEDULE")
        
        c.setFillColor(colors.black)
        y -= 35
        for m in [5, 10, 12, 15, 18, 24, 30, 36]:
            if int_type == "Flat Rate":
                emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else:
                r = roi / (12 * 100)
                emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            c.setFont("Helvetica", 10)
            c.drawString(80, y, f"{m} Months Plan")
            c.drawRightString(500, y, f"{emi:,.2f}")
            y -= 18

        # Footer with QR Code
        c.line(50, 110, 540, 110)
        c.drawImage(io.BytesIO(qr_buffer.getvalue()), 50, 45, width=60, height=60)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(120, 70, f"* Computer-generated quotation based on {int_type.lower()}.")
        c.drawString(120, 60, "Scan QR for Shop Address")
        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(540, 70, "Authorized Signature")
        c.drawRightString(540, 55, "AGARWAL ENTERPRISE")

        c.save()
        st.download_button("📥 Download Final Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf")
