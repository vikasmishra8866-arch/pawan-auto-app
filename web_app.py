import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import datetime
import io

# Page Setup
st.set_page_config(page_title="Pawan Finance", page_icon="🏦")

st.title("🏦 PAWAN AUTO FINANCE")
st.subheader("Welcome, Vikas Mishra") 

# Input Section
cust_name = st.text_input("Customer Name", placeholder="e.g. VIKAS MISHRA")

col1, col2 = st.columns(2)
with col1:
    price = st.number_input("Vehicle Price (Rs)", value=0)
    down = st.number_input("Down Payment (Rs)", value=0)
    file_charges = st.number_input("File Charges (Rs)", value=0) # Alag Box 1
with col2:
    other_charges = st.number_input("Other Charges (Rs)", value=0) # Alag Box 2
    roi = st.number_input("Flat Interest Rate (%)", value=18.0)

# Total Loan Calculation
loan_amt = (price - down) + file_charges + other_charges

if st.button("Calculate & Create PDF"):
    if not cust_name:
        st.error("Please enter Customer Name!")
    elif price <= 0:
        st.error("Please enter Vehicle Price!")
    else:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(300, 800, "PAWAN AUTO FINANCE")
        c.setFont("Helvetica", 12)
        c.drawCentredString(300, 775, "Managed by: Vikas Mishra")
        c.line(50, 765, 550, 765)
        
        dt = datetime.datetime.now().strftime("%d-%m-%Y %I:%M %p")
        c.setFont("Helvetica", 11)
        c.drawString(70, 740, f"Customer: {cust_name}")
        c.drawRightString(530, 740, f"Date: {dt}")
        
        y = 690
        basics = [
            ("Vehicle Price", f"Rs. {price:,.2f}"),
            ("Down Payment", f"Rs. {down:,.2f}"),
            ("File Charges", f"Rs. {file_charges:,.2f}"),
            ("Other Charges", f"Rs. {other_charges:,.2f}"),
            ("Net Loan Amount", f"Rs. {loan_amt:,.2f}"),
            ("Interest Rate", f"{roi}% (Flat)")
        ]
        
        for label, val in basics:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(100, y, f"{label}:")
            c.setFont("Helvetica", 12)
            c.drawRightString(450, y, val)
            y -= 30

        y -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(300, y, "EMI REPAYMENT OPTIONS")
        y -= 10; c.line(100, y, 500, y)
        
        for m in [12, 18, 24, 36]:
            y -= 30
            emi = (loan_amt + (loan_amt * roi * (m/12) / 100)) / m
            c.setFont("Helvetica", 12)
            c.drawString(150, y, f"{m} Months Tenure")
            c.drawRightString(450, y, f"Rs. {emi:,.2f}")
            
        c.save()
        st.success("PDF taiyaar hai!")
        st.download_button(label="📥 Download Quotation PDF", data=buffer.getvalue(), file_name=f"Quotation_{cust_name}.pdf", mime="application/pdf")
