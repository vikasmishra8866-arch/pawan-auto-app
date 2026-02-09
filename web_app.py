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

# --- NEW PREMIUM INTERFACE (CSS) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* RGB Border Animation for Sidebar QR */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    .rgb-box {
        padding: 15px;
        background: white;
        border-radius: 15px;
        text-align: center;
        border: 4px solid;
        animation: rgb-anim 4s linear infinite;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    @keyframes rgb-anim {
        0% { border-color: #ff0000; }
        33% { border-color: #00ff00; }
        66% { border-color: #0000ff; }
        100% { border-color: #ff0000; }
    }

    /* Title Styling */
    h1 {
        color: #1e3d59 !important;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }

    /* WhatsApp Button */
    .whatsapp-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #25d366;
        color: white !important;
        border-radius: 50px;
        padding: 15px 25px;
        font-weight: bold;
        text-decoration: none;
        z-index: 1000;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 10px;
    }
    </style>
    
    <a href="https://wa.me/919696159863" class="whatsapp-btn" target="_blank">
        <span>💬 WhatsApp Support</span>
    </a>
    """, unsafe_allow_html=True)

# --- SIDEBAR ADDRESS & QR (Adding to empty space) ---
with st.sidebar:
    st.markdown('<div class="rgb-box">', unsafe_allow_html=True)
    st.markdown("<b style='color:#1e3d59;'>📍 SCAN FOR SHOP ADDRESS</b>", unsafe_allow_html=True)
    
    # QR Code Generation for Sidebar
    shop_link = "https://share.google/2Cs3iSUypf5Lf9PpS"
    qr_side = qrcode.QRCode(version=1, box_size=10, border=1)
    qr_side.add_data(shop_link)
    qr_side.make(fit=True)
    qr_side_img = qr_side.make_image(fill_color="#1e3d59", back_color="white")
    buf_side = io.BytesIO()
    qr_side_img.save(buf_side, format='PNG')
    
    st.image(buf_side, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="background:#1e3d59; color:white; padding:12px; border-radius:10px; font-size:12px;">
        <b>SHOP ADDRESS:</b><br>
        SHOP NO-6, ASHIRWAD TOWNSHIP-1, NEAR WELCOME PAN CENTRE, 
        120 FT BAMROLI ROAD, PANDESARA, SURAT, GUJARAT-394210
        </div>
    """, unsafe_allow_html=True)

# --- UI DESIGN (ORIGINAL) ---
st.title("🏦 PAWAN AUTO FINANCE")
st.markdown(f"<div style='text-align:center;'><b>Managed by: Vikas Mishra</b></div>", unsafe_allow_html=True) 
st.write(f"📅 {current_time}")

# --- NEW OPTION SELECTION (ORIGINAL) ---
st.markdown("---")
service_mode = st.radio("Select Quotation Type", ["Vehicle Purchase", "Loan on Vehicle"], horizontal=True)

# [START OF ORIGINAL INPUTS]
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")
veh_name = st.text_input("Vehicle Name", placeholder="e.g. PIAGGIO / APE")

col1, col2 = st.columns(2)

if service_mode == "Vehicle Purchase":
    with col1:
        price = st.number_input("Vehicle Price (Rs)", value=None, placeholder="Enter Price...")
        down = st.number_input("Down Payment (Rs)", value=None, placeholder="Enter Down Payment...")
        file_charges = st.number_input("File Charges (Rs)", value=None, placeholder="Enter File Charges...")
    with col2:
        other_charges = st.number_input("Other Charges (Rs)", value=None, placeholder="Enter Other Charges...")
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

    loan_amt = (l_amt if l_amt else 0) + (ins_ch if ins_ch else 0) + (pass_ch if pass_ch else 0) + \
               (trans_ch if trans_ch else 0) + (hp_term if hp_term else 0) + \
               (hp_add if hp_add else 0) + (oth_ch if oth_ch else 0)
    
    pdf_labels = [
        ("Loan Amount", l_amt if l_amt else 0), 
        ("Ins/Pass/Trans", (ins_ch if ins_ch else 0)+(pass_ch if pass_ch else 0)+(trans_ch if trans_ch else 0)), 
        ("HP Term/Add", (hp_term if hp_term else 0)+(hp_add if hp_add else 0)), 
        ("Other Charges", oth_ch if oth_ch else 0)
    ]

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
else:
    st.info("Fill the amounts to see live EMI preview.")

# --- PDF GENERATION (ORIGINAL LOGIC) ---
if st.button("Generate Premium PDF Quotation"):
    if not cust_name or not veh_name or loan_amt == 0:
        st.error("Please fill all necessary details!")
    else:
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
        
        c.setFillColor(colors.black); c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 720, f"CUSTOMER NAME: {cust_name.upper()}")
        c.drawString(50, 700, f"VEHICLE MODEL: {veh_name.upper()}")
        c.drawRightString(540, 720, f"DATE: {current_time}")
        c.line(50, 690, 540, 690)

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
            
        qr_y = 110 
        qr_reader = ImageReader(qr_img_buffer)
        c.drawImage(qr_reader, 50, qr_y, width=65, height=65)
        c.setFont("Helvetica-Bold", 7); c.drawString(50, qr_y - 8, "SCAN FOR ADDRESS")

        c.line(50, 100, 540, 100)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(50, 85, f"* This is a computer-generated quotation based on {int_type.lower()}.")
        c.setFont("Helvetica-Bold", 12); c.drawRightString(540, 85, "Authorized Signature")
        c.drawRightString(540, 65, "AGARWAL ENTERPRISE")

        c.save()
        st.success(f"Quotation Generated Successfully!")
        st.download_button("📥 Download Premium Quotation", buffer.getvalue(), f"Quotation_{cust_name}.pdf", "application/pdf")
