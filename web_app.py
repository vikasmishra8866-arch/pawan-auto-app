import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader # QR Fix ke liye
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
st.subheader("Vehicle Purchase EMI Quotation")
st.markdown(f"**Managed by: Vikas Mishra**") 
st.write(f"📅 {current_time}")

# --- SERVICE SELECTION ---
st.markdown("---")
service_type = st.radio("Select Service Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

# Input Section
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

label_1, val_1 = "", 0
label_2, val_2 = "", 0
label_3, val_3 = "", 0
label_4, val_4 = "", 0

if service_type == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Type Price...")
        down = st.number_input("Down Payment (Rs)", value=None, placeholder="Type Down Payment...")
        file_charges = st.number_input("File Charges (Rs)", value=None, placeholder="Type File Charges...")
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None, placeholder="Type Other Charges...")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    p_val = price if price is not None else 0
    d_val = down if down is not None else 0
    f_val = file_charges if file_charges is not None else 0
    o_val = other_charges if other_charges is not None else 0
    loan_amt = (p_val - d_val) + f_val + o_val
    
    label_1, val_1 = "Vehicle Price", p_val
    label_2, val_2 = "Down Payment", d_val
    label_3, val_3 = "File Charges", f_val
    label_4, val_4 = "Other Charges", o_val

else: # LOAN ON VEHICLE
    with col1:
        l_amt_input = st.number_input("Loan Amount (Rs)", value=None, placeholder="Enter Loan Amount...")
        ins_charges = st.number_input("Insurance Charges (Rs)", value=None, placeholder="Enter Insurance Charges...")
        pass_charges = st.number_input("Passing Charges (Rs)", value=None, placeholder="Enter Passing Charges...")
    with col2:
        other_charges_loan = st.number_input("Other Charges (Rs)", value=None, placeholder="Enter Other Charges...")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    l_val = l_amt_input if l_amt_input is not None else 0
    i_val = ins_charges if ins_charges is not None else 0
    ps_val = pass_charges if pass_charges is not None else 0
    ol_val = other_charges_loan if other_charges_loan is not None else 0
    loan_amt = l_val + i_val + ps_val + ol_val
    
    label_1, val_1 = "Loan Amount", l_val
    label_2, val_2 = "Insurance Charges", i_val
    label_3, val_3 = "Passing Charges", ps_val
    label_4, val_4 = "Other Charges", ol_val

# --- LIVE PREVIEW ---
st.markdown("---")
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
            col.metric(f"{m} Mo", f"₹{emi_val:,.0f}")
            col.caption(f"Tot: ₹{total_payable:,.0f}")

# --- PDF GENERATION ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or not veh_name:
        st.error("Please fill all details!")
    else:
        # --- QR CODE GENERATION (Optimized for GitHub) ---
        qr_data = f"Pawan Auto Finance\nCust: {cust_name}\nLoan: Rs.{loan_amt:,.0f}\nVehicle: {veh_name}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        qr_img_buffer = io.BytesIO()
        qr_img.save(qr_img_buffer, format='PNG')
        qr_img_buffer.seek(0)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Watermark & Header
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
        
        # Details
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, f"CUSTOMER NAME: {cust_name.upper()}")
        c.drawString(50, 700, f"VEHICLE MODEL: {veh_name.upper()}")
        c.drawRightString(540, 720, f"DATE: {current_time}")

        # --- DRAW QR CODE (Using ImageReader for No Errors) ---
        qr_reader = ImageReader(qr_img_buffer)
        c.drawImage(qr_reader, 460, 600, width=80, height=80)

        y = 660
        data = [(label_1, f"Rs. {val_1:,.2f}"), (label_2, f"Rs. {val_2:,.2f}"), (label_3, f"Rs. {val_3:,.2f}"), (label_4, f"Rs. {val_4:,.2f}"), ("Net Loan Amount", f"Rs. {loan_amt:,.2f}"), ("Interest Rate", f"{roi}% ({int_type})")]
        
        for label, val in data:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(70, y, label)
            c.setFont("Helvetica", 12)
            c.drawRightString(450, y, val)
            y -= 25
        
        # Table Schedule
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

        c.save()
        st.success("PDF with QR Code Generated!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
