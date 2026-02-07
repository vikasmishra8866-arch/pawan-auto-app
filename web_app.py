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
st.subheader("Vehicle Purchase EMI Quotation") # Naya Title jo aapne bola
st.markdown(f"**Managed by: Vikas Mishra**") 
st.write(f"📅 {current_time}")

# --- NEW OPTION: PURCHASE OR LOAN ---
st.markdown("---")
service_type = st.radio("Select Service Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

# Input Section
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

if service_type == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Type Price...")
        down = st.number_input("Down Payment (Rs)", value=None, placeholder="Type Down Payment...")
        file_charges = st.number_input("File Charges (Rs)", value=None, placeholder="Type File Charges...")
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None, placeholder="Type Other Charges...")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    # Calculation for Purchase
    p_val = price if price is not None else 0
    d_val = down if down is not None else 0
    f_val = file_charges if file_charges is not None else 0
    o_val = other_charges if other_charges is not None else 0
    loan_amt = (p_val - d_val) + f_val + o_val

else: # LOAN ON VEHICLE OPTION
    with col1:
        l_amt_input = st.number_input("Loan Amount (Rs)", value=None, placeholder="Enter Loan Amount...")
        ins_charges = st.number_input("Insurance Charges (Rs)", value=None, placeholder="Enter Insurance Charges...")
        pass_charges = st.number_input("Passing Charges (Rs)", value=None, placeholder="Enter Passing Charges...")
    with col2:
        other_charges_loan = st.number_input("Other Charges (Rs)", value=None, placeholder="Enter Other Charges...")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    # Calculation for Loan
    l_val = l_amt_input if l_amt_input is not None else 0
    i_val = ins_charges if ins_charges is not None else 0
    ps_val = pass_charges if pass_charges is not None else 0
    ol_val = other_charges_loan if other_charges_loan is not None else 0
    loan_amt = l_val + i_val + ps_val + ol_val
    # PDF ke liye purane variables map karna taaki PDF change na ho
    p_val = loan_amt # PDF mein Price ki jagah Net Amount dikhega
    d_val = 0
    f_val = i_val + ps_val # Combined as file/processing
    o_val = ol_val

# --- LIVE EMI PREVIEW SECTION (SAME AS BEFORE) ---
st.markdown("---")
st.subheader("📊 Live EMI Preview (EMI & Total Payable)")
if (service_type == "Vehicle Purchase" and price is not None) or (service_type == "Loan on Vehicle" and l_amt_input is not None):
    all_tenures = [5, 10, 12, 15, 18, 24, 30, 36]
    for i in range(0, len(all_tenures), 4):
        cols = st.columns(4)
        for m, col in zip(all_tenures[i:i+4], cols):
            if int_type == "Flat Rate":
                emi_val = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else:
                r = roi / (12 * 100)
                emi_val = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            total_payable = emi_val * m
            col.metric(f"{m} Months", f"₹{emi_val:,.0f}/m")
            col.caption(f"Total: ₹{total_payable:,.0f}")
else:
    st.info("Enter Amounts to see live EMI.")

# --- PDF GENERATION (NO COORDINATE CHANGE) ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or not veh_name:
        st.error("Please fill all details!")
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Watermark, Header, Details coordinates same as before
        c.saveState()
        c.setFont("Helvetica-Bold", 50)
        c.setStrokeColor(colors.lightgrey)
        c.setFillColor(colors.lightgrey, alpha=0.15) 
        c.translate(300, 450)
        c.rotate(45)
        c.drawCentredString(0, 0, "PAWAN AUTO FINANCE")
        c.restoreState()
        
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(0, 750, 600, 100, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(300, 795, "PAWAN AUTO FINANCE")
        c.setFont("Helvetica-Oblique", 12)
        c.drawCentredString(300, 775, "Fastest Loan Approval & Trusted Service")
        
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, f"CUSTOMER NAME: {cust_name.upper()}")
        c.drawString(50, 700, f"VEHICLE MODEL: {veh_name.upper()}")
        c.drawRightString(540, 720, f"DATE: {current_time}")
        c.line(50, 690, 540, 690)

        y = 660
        data = [
            ("Vehicle Value/Loan", f"Rs. {p_val:,.2f}"),
            ("Initial Payment", f"Rs. {d_val:,.2f}"),
            ("Processing/Insurance", f"Rs. {f_val:,.2f}"),
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
        y -= 30
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(50, y-10, 490, 30, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(300, y, "REPAYMENT SCHEDULE")
        
        c.setFillColor(colors.black)
        y -= 40
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, "TENURE")
        c.drawCentredString(260, y, "MONTHLY EMI (RS)")
        c.drawRightString(530, y, "TOTAL PAYABLE (RS)")
        c.line(50, y-5, 540, y-5)
        
        y -= 25
        for m in [5, 10, 12, 15, 18, 24, 30, 36]:
            if int_type == "Flat Rate":
                emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else:
                r = roi / (12 * 100)
                emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            total_pay = emi * m
            c.setFont("Helvetica", 11)
            c.drawString(60, y, f"{m} Months Plan")
            c.drawCentredString(260, y, f"{emi:,.2f}")
            c.drawRightString(530, y, f"{total_pay:,.2f}")
            y -= 22
            
        c.line(50, 100, 540, 100)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 85, f"* This is a computer-generated quotation based on {int_type.lower()}.")
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(540, 85, "Authorized Signature")
        c.drawRightString(540, 65, "AGARWAL ENTERPRISE")

        c.save()
        st.success(f"Quotation Generated for {cust_name}!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
