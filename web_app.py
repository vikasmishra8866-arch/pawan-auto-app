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

# Page Setup - Screen size compact karne ke liye width adjust ki hai
st.set_page_config(page_title="Pawan Auto Finance", page_icon="🏦", layout="wide")

# --- PREMIUM INTERFACE (CSS) ---
st.markdown("""
    <style>
    /* Screen Zoom kam karne ke liye sidebar aur padding adjust */
    section[data-testid="stSidebar"] { width: 220px !important; }
    .main .block-container { padding-top: 2rem; padding-bottom: 1rem; }
    
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    /* RGB Border Animation */
    .rgb-box {
        padding: 8px;
        background: white;
        border-radius: 10px;
        text-align: center;
        border: 3px solid;
        animation: rgb-anim 4s linear infinite;
        margin-bottom: 10px;
    }
    @keyframes rgb-anim {
        0% { border-color: #ff0000; }
        33% { border-color: #00ff00; }
        66% { border-color: #0000ff; }
        100% { border-color: #ff0000; }
    }

    h1 { color: #1e3d59 !important; font-family: 'Helvetica Neue', sans-serif; font-weight: 800; text-align: center; margin-bottom: 0px; }

    .whatsapp-btn {
        position: fixed; bottom: 20px; right: 20px; background-color: #25d366;
        color: white !important; border-radius: 50px; padding: 12px 20px;
        font-weight: bold; text-decoration: none; z-index: 1000;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2); display: flex; align-items: center; gap: 10px;
    }
    </style>
    
    <a href="https://wa.me/919696159863" class="whatsapp-btn" target="_blank">
        <span>💬 WhatsApp</span>
    </a>
    """, unsafe_allow_html=True)

# --- SIDEBAR: VERY SMALL QR & FULL ADDRESS ---
with st.sidebar:
    st.markdown('<div class="rgb-box"><b style="font-size: 12px; color: #1e3d59;">SCAN FOR ADDRESS</b></div>', unsafe_allow_html=True)
    
    shop_link = "https://share.google/2Cs3iSUypf5Lf9PpS"
    qr_side = qrcode.QRCode(version=1, box_size=4, border=1) 
    qr_side.add_data(shop_link)
    qr_side.make(fit=True)
    qr_side_img = qr_side.make_image(fill_color="#1e3d59", back_color="white")
    buf_side = io.BytesIO()
    qr_side_img.save(buf_side, format='PNG')
    
    col_l, col_m, col_r = st.columns([1, 3, 1])
    with col_m:
        st.image(buf_side, use_container_width=True)
    
    st.markdown("""
        <div style="background:#1e3d59; color:white; padding:10px; border-radius:8px; font-size:10px; text-align:left; line-height:1.4;">
        <b>ADDRESS:</b><br>
        SHOP NO-6, ASHIRWAD TOWNSHIP-1,<br>
        NEAR WELCOME PAN CENTRE,<br>
        BAMROLI ROAD, PANDESARA,<br>
        SURAT, GUJARAT - 394210
        </div>
    """, unsafe_allow_html=True)

# --- MAIN UI ---
st.title("🏦 PAWAN AUTO FINANCE")
st.markdown(f"<div style='text-align:center; font-size:14px;'><b>Managed by: Vikas Mishra</b></div>", unsafe_allow_html=True) 

# --- INPUT SECTION (ORIGINAL) ---
st.markdown("---")
service_mode = st.radio("Select Quotation Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

if service_mode == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None)
        down = st.number_input("Down Payment (Rs)", value=None)
        file_charges = st.number_input("File Charges (Rs)", value=None)
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None)
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0) 
    
    p_val = price if price is not None else 0
    d_val = down if down is not None else 0
    f_val = file_charges if file_charges is not None else 0
    o_val = other_charges if other_charges is not None else 0
    loan_amt = (p_val - d_val) + f_val + o_val
    pdf_labels = [("Vehicle Price", p_val), ("Down Payment", d_val), ("File Charges", f_val), ("Other Charges", o_val)]
else: 
    with col1:
        l_amt = st.number_input("Loan Amount (Rs)", value=None)
        ins_ch = st.number_input("Insurance Charge (Rs)", value=0.0)
        pass_ch = st.number_input("Passing Charge (Rs)", value=0.0)
    with col2:
        oth_ch = st.number_input("Other Charge (Rs)", value=0.0)
        int_type = st.radio("Interest Type", ["Flat Rate", "Reducing Balance"], horizontal=True)
        roi = st.number_input(f"{int_type} (%)", value=18.0) 
    loan_amt = (l_amt if l_amt else 0) + ins_ch + pass_ch + oth_ch
    pdf_labels = [("Loan Amount", l_amt if l_amt else 0), ("Insurance", ins_ch), ("Passing", pass_ch), ("Other", oth_ch)]

# --- LIVE EMI PREVIEW ---
st.subheader(f"📊 Live EMI Preview")
if loan_amt > 0:
    all_tenures = [12, 18, 24, 36] # Reduced number for better screen fit
    cols = st.columns(4)
    for m, col in zip(all_tenures, cols):
        if int_type == "Flat Rate":
            emi_val = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
        else:
            r = roi / (12 * 100); emi_val = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
        col.metric(f"{m} Mo", f"₹{emi_val:,.0f}")
else:
    st.info("Enter values to see EMI.")

# --- PDF GENERATION (UPDATED HEADER) ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or loan_amt == 0:
        st.error("Please fill details!")
    else:
        qr_img_buffer = io.BytesIO()
        qrcode.make("https://share.google/2Cs3iSUypf5Lf9PpS").save(qr_img_buffer, format='PNG')
        qr_img_buffer.seek(0)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Header Section
        c.setFillColor(colors.HexColor("#1e3d59"))
        c.rect(0, 740, 600, 110, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(300, 805, "PAWAN AUTO FINANCE")
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(300, 785, "AGARWAL ENTERPRISE")
        
        c.setFont("Helvetica-Oblique", 9) # Mudey hue text (Italic)
        shop_adr = "SHOP NO-6, ASHIRWAD TOWNSHIP-1, NEAR WELCOME PAN CENTRE, BAMROLI ROAD, PANDESARA, SURAT"
        c.drawCentredString(300, 770, shop_adr)

        # Content Logic (Original)
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 710, f"CUSTOMER: {cust_name.upper()} | VEHICLE: {veh_name.upper()}")
        c.drawRightString(540, 710, f"DATE: {current_time}")
        c.line(50, 700, 540, 700)
        
        y = 670
        for label, val in pdf_labels:
            c.setFont("Helvetica-Bold", 11); c.drawString(70, y, label)
            c.setFont("Helvetica", 11); c.drawRightString(520, y, f"Rs. {val:,.2f}")
            y -= 25
        
        c.line(50, y, 540, y); y -= 30
        c.setFont("Helvetica-Bold", 14); c.drawString(70, y, "Net Loan Amount"); c.drawRightString(520, y, f"Rs. {loan_amt:,.2f}")
        y -= 50
        
        # Table Header
        c.setFillColor(colors.HexColor("#1e3d59")); c.rect(50, y-10, 490, 30, fill=1)
        c.setFillColor(colors.white); c.setFont("Helvetica-Bold", 12); c.drawCentredString(300, y, "REPAYMENT SCHEDULE")
        y -= 40; c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 10); c.drawString(60, y, "TENURE"); c.drawCentredString(260, y, "MONTHLY EMI"); c.drawRightString(530, y, "TOTAL")
        
        y -= 20
        for m in [12, 18, 24, 30, 36]:
            if int_type == "Flat Rate": emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            else: r = roi / (12 * 100); emi = (loan_amt * r * (1 + r)**m) / ((1 + r)**m - 1)
            c.setFont("Helvetica", 10); c.drawString(60, y, f"{m} Months"); c.drawCentredString(260, y, f"{emi:,.2f}"); c.drawRightString(530, y, f"{emi*m:,.2f}")
            y -= 20

        # Footer
        c.drawImage(ImageReader(qr_img_buffer), 50, 50, width=60, height=60)
        c.setFont("Helvetica-Bold", 12); c.drawRightString(540, 70, "Authorized Signature")
        c.drawRightString(540, 55, "AGARWAL ENTERPRISE")
        
        c.save()
        st.success("Quotation Ready!")
        st.download_button("📥 Download PDF", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
