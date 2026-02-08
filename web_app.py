import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
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
st.markdown(f"**Managed by: Vikas Mishra**") 
st.write(f"📅 {current_time}")

# --- NEW OPTION SELECTION ---
st.markdown("---")
service_mode = st.radio("Select Quotation Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

# Input Section
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

# Logic for inputs based on selection
if service_mode == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Type Price...")
        down = st.number_input("Down Payment (Rs)", value=None, placeholder="Type Down Payment...")
        file_charges = st.number_input("File Charges (Rs)", value=None, placeholder="Type File Charges...")
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None, placeholder="Type Other Charges...")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    # Calculations
    p_val = price if price is not None else 0
    d_val = down if down is not None else 0
    f_val = file_charges if file_charges is not None else 0
    o_val = other_charges if other_charges is not None else 0
    loan_amt = (p_val - d_val) + f_val + o_val
    pdf_labels = [("Vehicle Price", p_val), ("Down Payment", d_val), ("File Charges", f_val), ("Other Charges", o_val)]

else: # LOAN ON VEHICLE (Naya Option)
    with col1:
        l_amt = st.number_input("Loan Amount (Rs)", value=None, placeholder="Enter Loan Amt...")
        ins_ch = st.number_input("Insurance Charge (Rs)", value=0.0)
        pass_ch = st.number_input("Passing Charge (Rs)", value=0.0)
        trans_ch = st.number_input("Transfer Charge (Rs)", value=0.0)
    with col2:
        hp_term = st.number_input("HP Terminate Charge (Rs)", value=0.0)
        hp_add = st.number_input("HP Add Charge (Rs)", value=0.0)
        oth_ch = st.number_input("Other Charge (Rs)", value=0.0)
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0)
    
    loan_amt = (l_amt if l_amt else 0) + ins_ch + pass_ch + trans_ch + hp_term + hp_add + oth_ch
    pdf_labels = [("Loan Amount", l_amt if l_amt else 0), ("Ins/Pass/Trans", ins_ch+pass_ch+trans_ch), ("HP Term/Add", hp_term+hp_add), ("Other Charges", oth_ch)]

# --- LIVE EMI PREVIEW ---
st.markdown("---")
st.subheader(f"📊 Live EMI Preview ({service_mode})")
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
            total_payable = emi_val * m
            col.metric(f"{m} Months", f"₹{emi_val:,.0f}/m")
            col.caption(f"Total: ₹{total_payable:,.0f}")

# --- PDF GENERATION ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or not veh_name or loan_amt == 0:
        st.error("Please fill all necessary details!")
    else:
        # QR Code Setup
        map_link = "https://share.google/2Cs3iSUypf5Lf9PpS"
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(map_link)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="#1e3d59", back_color="white")
        qr_img_buffer = io.BytesIO()
        qr_img.save(qr_img_buffer, format='PNG')
        qr_img_buffer.seek(0)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Header & Watermark (Symmetry kept)
        c.saveState()
        c.setFont("Helvetica-Bold", 50)
        c.setStrokeColor(colors.lightgrey); c.setFillColor(colors.lightgrey, alpha=0.15) 
        c.translate(300, 450); c.rotate(45); c.drawCentredString(0, 0, "PAWAN AUTO FINANCE")
        c.restoreState()
        
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(0, 750, 600, 100, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 30)
        c.drawCentredString(300, 795, "PAWAN AUTO FINANCE")
        c.setFont("Helvetica-Oblique", 12); c.drawCentredString(300, 775, "Fastest Loan Approval & Trusted Service")
        
        # Details
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, f"CUSTOMER NAME: {cust_name.upper()}")
        c.drawString(50, 700, f"VEHICLE MODEL: {veh_name.upper()}")
        c.drawRightString(540, 720, f"DATE: {current_time}")
        c.line(50, 690, 540, 690)

        # Main Data Table
        y = 660
        for label, val in pdf_labels:
            c.setFont("Helvetica-Bold", 12); c.drawString(70, y, label)
            c.setFont("Helvetica", 12); c.drawRightString(520, y, f"Rs. {val:,.2f}")
            y -= 25
        
        c.setFont("Helvetica-Bold", 12); c.drawString(70, y, "Net Loan Amount")
        c.drawRightString(520, y, f"Rs. {loan_amt:,.2f}")
        y -= 25
        c.drawString(70, y, "Interest Rate"); c.drawRightString(520, y, f"{roi}% ({int_type})")
        
        c.line(50, y-10, 540, y-10)

        # EMI Table
        y -= 50
        c.setFillColor(colors.HexColor("#1e3d59")); c.rect(50, y-10, 490, 30, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 14); c.drawCentredString(300, y, "REPAYMENT SCHEDULE")
        
        c.setFillColor(colors.black); y -= 40
        c.setFont("Helvetica-Bold", 11); c.drawString(60, y, "TENURE"); c.drawCentredString(260, y, "MONTHLY EMI (RS)"); c.drawRightString(530, y, "TOTAL PAYABLE (RS)")
        c.line(50, y-5, 540, y-5)
        
        y -= 25
        for m in [5, 10, 12, 15, 18, 24, 30, 36]:
            if int_type == "Flat Rate":
                emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else:
                r = roi / (12 * 100); emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            total_pay = emi * m
            c.setFont("Helvetica", 11); c.drawString(60, y, f"{m} Months Plan"); c.drawCentredString(260, y, f"{emi:,.2f}"); c.drawRightString(530, y, f"{total_pay:,.2f}")
            y -= 22
            
        # --- FOOTER WITH QR CODE SHIFTED DOWN ---
        qr_y = 110 # Positioned above the generated text
        qr_reader = ImageReader(qr_img_buffer)
        c.drawImage(qr_reader, 50, qr_y, width=65, height=65)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(50, qr_y - 8, "SCAN FOR ADDRESS")

        c.line(50, 100, 540, 100)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 85, f"* This is a computer-generated quotation based on {int_type.lower()}.")
        c.setFont("Helvetica-Bold", 12); c.drawRightString(540, 85, "Authorized Signature")
        c.drawRightString(540, 65, "AGARWAL ENTERPRISE")

        c.save()
        st.success(f"Quotation Generated Successfully!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
