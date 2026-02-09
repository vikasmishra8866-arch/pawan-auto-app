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
st.set_page_config(page_title="Pawan Auto Finance", page_icon="🏦", layout="wide")

# --- PREMIUM INTERFACE (CSS) ---
st.markdown("""
    <style>
    section[data-testid="stSidebar"] { width: 240px !important; }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .rgb-box {
        padding: 8px; background: white; border-radius: 10px;
        text-align: center; border: 3px solid;
        animation: rgb-anim 4s linear infinite; margin-bottom: 10px;
    }
    @keyframes rgb-anim {
        0% { border-color: #ff0000; }
        33% { border-color: #00ff00; }
        66% { border-color: #0000ff; }
        100% { border-color: #ff0000; }
    }
    h1 { color: #1e3d59 !important; text-align: center; margin-bottom: 0px; }
    .whatsapp-btn {
        position: fixed; bottom: 20px; right: 20px; background-color: #25d366;
        color: white !important; border-radius: 50px; padding: 12px 20px;
        font-weight: bold; text-decoration: none; z-index: 1000;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 10px;
    }
    </style>
    <a href="https://wa.me/919696159863" class="whatsapp-btn" target="_blank"><span>💬 WhatsApp</span></a>
    """, unsafe_allow_html=True)

# --- SIDEBAR ADDRESS & QR ---
with st.sidebar:
    st.markdown('<div class="rgb-box"><b style="font-size: 13px; color: #1e3d59;">SCAN FOR ADDRESS</b></div>', unsafe_allow_html=True)
    qr_side = qrcode.QRCode(version=1, box_size=4, border=1)
    qr_side.add_data("https://share.google/2Cs3iSUypf5Lf9PpS")
    qr_side.make(fit=True)
    buf_side = io.BytesIO()
    qr_side.make_image(fill_color="#1e3d59", back_color="white").save(buf_side, format='PNG')
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m: st.image(buf_side, use_container_width=True)
    st.markdown("""
        <div style="background:#1e3d59; color:white; padding:10px; border-radius:8px; font-size:10px; line-height:1.4;">
        <b>ADDRESS:</b><br>SHOP NO-6, ASHIRWAD TOWNSHIP-1, NEAR WELCOME PAN CENTRE, BAMROLI ROAD, PANDESARA, SURAT, GUJARAT-394210
        </div>""", unsafe_allow_html=True)

# --- MAIN UI ---
st.title("🏦 PAWAN AUTO FINANCE")
st.markdown(f"<div style='text-align:center;'><b>Managed by: Vikas Mishra</b></div>", unsafe_allow_html=True) 
st.write(f"<div style='text-align:center; font-size:12px;'>📅 {current_time}</div>", unsafe_allow_html=True)

st.markdown("---")
service_mode = st.radio("Select Quotation Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

# --- ORIGINAL LOGIC & INPUTS ---
if service_mode == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Enter Price...")
        down = st.number_input("Down Payment (Rs)", value=None, placeholder="Enter Down Payment...")
        file_charges = st.number_input("File Charges (Rs)", value=None, placeholder="Enter File Charges...")
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None, placeholder="Enter Other Charges...")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0) 
    
    loan_amt = (price or 0) - (down or 0) + (file_charges or 0) + (other_charges or 0)
    pdf_labels = [("Vehicle Price", price or 0), ("Down Payment", down or 0), ("File Charges", file_charges or 0), ("Other Charges", other_charges or 0)]
else: 
    with col1:
        l_amt = st.number_input("Loan Amount (Rs)", value=None, placeholder="Enter Loan Amt...")
        ins_ch = st.number_input("Insurance Charge (Rs)", value=None, placeholder="0.0")
        pass_ch = st.number_input("Passing Charge (Rs)", value=None, placeholder="0.0")
        trans_ch = st.number_input("Transfer Charge (Rs)", value=None, placeholder="0.0")
    with col2:
        hp_term = st.number_input("HP Terminate Charge (Rs)", value=None, placeholder="0.0")
        hp_add = st.number_input("HP Add Charge (Rs)", value=None, placeholder="0.0")
        oth_ch = st.number_input("Other Charge (Rs)", value=None, placeholder="0.0")
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0) 
    
    loan_amt = (l_amt or 0) + (ins_ch or 0) + (pass_ch or 0) + (trans_ch or 0) + (hp_term or 0) + (hp_add or 0) + (oth_ch or 0)
    pdf_labels = [("Loan Amount", l_amt or 0), ("Ins/Pass/Trans", (ins_ch or 0)+(pass_ch or 0)+(trans_ch or 0)), ("HP Term/Add", (hp_term or 0)+(hp_add or 0)), ("Other Charges", oth_ch or 0)]

# --- LIVE EMI PREVIEW ---
st.markdown("---")
st.subheader(f"📊 Live EMI Preview")
if loan_amt > 0:
    all_tenures = [5, 10, 12, 15, 18, 24, 30, 36]
    for i in range(0, len(all_tenures), 4):
        cols = st.columns(4)
        for m, col in zip(all_tenures[i:i+4], cols):
            if int_type == "Flat Rate": emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else: r = roi / (12 * 100); emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            col.metric(f"{m} Mo", f"₹{emi:,.0f}/m")
else: st.info("Enter values to see EMI preview.")

# --- PDF GENERATION (FIXED QR OVERLAP) ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or loan_amt == 0: st.error("Please fill details!")
    else:
        qr_buf = io.BytesIO()
        qrcode.make("https://share.google/2Cs3iSUypf5Lf9PpS").save(qr_buf, format='PNG')
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Header
        c.setFillColor(colors.HexColor("#1e3d59")); c.rect(0, 740, 600, 110, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 28); c.drawCentredString(300, 805, "PAWAN AUTO FINANCE")
        c.setFont("Helvetica-Bold", 16); c.drawCentredString(300, 785, "AGARWAL ENTERPRISE")
        c.setFont("Helvetica-Oblique", 9)
        c.drawCentredString(300, 770, "SHOP NO-6, ASHIRWAD TOWNSHIP-1, NEAR WELCOME PAN CENTRE, BAMROLI ROAD, PANDESARA, SURAT")
        
        # Details
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 715, f"CUSTOMER NAME: {cust_name.upper()}")
        c.drawString(50, 695, f"VEHICLE MODEL: {veh_name.upper()}")
        c.drawRightString(540, 715, f"DATE: {current_time}"); c.line(50, 685, 540, 685)
        
        y = 655
        for label, val in pdf_labels:
            c.setFont("Helvetica-Bold", 12); c.drawString(70, y, label); c.drawRightString(520, y, f"Rs. {val:,.2f}"); y -= 25
        
        c.setFont("Helvetica-Bold", 12); c.drawString(70, y, "Net Loan Amount"); c.drawRightString(520, y, f"Rs. {loan_amt:,.2f}")
        y -= 25
        c.drawString(70, y, "Interest Rate"); c.drawRightString(520, y, f"{roi}% ({int_type})")
        c.line(50, y-10, 540, y-10)

        # Repayment Table
        y -= 50; c.setFillColor(colors.HexColor("#1e3d59")); c.rect(50, y-10, 490, 30, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 14); c.drawCentredString(300, y, "REPAYMENT SCHEDULE")
        c.setFillColor(colors.black); y -= 40
        c.setFont("Helvetica-Bold", 11); c.drawString(60, y, "TENURE"); c.drawCentredString(260, y, "MONTHLY EMI (RS)"); c.drawRightString(530, y, "TOTAL PAYABLE (RS)")
        c.line(50, y-5, 540, y-5); y -= 25
        
        for m in [5, 10, 12, 15, 18, 24, 30, 36]:
            if int_type == "Flat Rate": emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else: r = roi / (12 * 100); emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            c.setFont("Helvetica", 11); c.drawString(60, y, f"{m} Months Plan"); c.drawCentredString(260, y, f"{emi:,.2f}"); c.drawRightString(530, y, f"{emi*m:,.2f}"); y -= 22
            
        # --- FOOTER SECTION (Sahi coordinates ke saath) ---
        qr_y_pos = 45 # QR thoda niche
        c.drawImage(ImageReader(qr_buf), 50, qr_y_pos, width=60, height=60)
        
        c.setFont("Helvetica-Bold", 7)
        c.drawString(50, qr_y_pos - 8, "SCAN FOR ADDRESS") 

        # Horizontal line (QR ke upar nahi aayegi)
        c.line(50, 115, 540, 115) 
        
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 122, f"* This is a computer-generated quotation based on {int_type.lower()}.") 
        
        # Signature logic
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(540, 85, "Authorized Signature")
        c.drawRightString(540, 65, "AGARWAL ENTERPRISE")

        c.save(); st.success("Quotation Ready!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
