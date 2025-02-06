import streamlit as st
import pandas as pd
import re
import google.generativeai as genai
import easyocr
from PIL import Image
import io
import time
import random

# Set Streamlit page config (must be first Streamlit command)
st.set_page_config(page_title="Decentralized Fraud Detection System", layout="wide")

# Set up Gemini API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Initialize session state for transactions if not already present
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'aadhar_verified' not in st.session_state:
    st.session_state.aadhar_verified = False
if 'fraud_alerts' not in st.session_state:
    st.session_state.fraud_alerts = []
if 'pan_verified' not in st.session_state:
    st.session_state.pan_verified = False
if 'bank_verified' not in st.session_state:
    st.session_state.bank_verified = False
if 'credit_score' not in st.session_state:
    st.session_state.credit_score = random.randint(300, 900)
if 'otp_verified' not in st.session_state:
    st.session_state.otp_verified = False
if 'gst_verified' not in st.session_state:
    st.session_state.gst_verified = False

# List of valid UPI handles in India
valid_upi_handles = {
    "@sbi", "@imobile", "@pockets", "@ezeepay", "@eazypay", "@icici", "@okicici",
    "@hdfcbank", "@payzapp", "@okhdfcbank", "@rajgovhdfcbank", "@mahb", "@kotak",
    "@kaypay", "@kmb", "@kmbl", "@yesbank", "@yesbankltd", "@ubi", "@united",
    "@utbi", "@idbi", "@idbibank", "@hsbc", "@pnb", "@centralbank", "@cbin",
    "@cboi", "@cnrb", "@barodampay"
}

def is_valid_upi(upi_id):
    return any(upi_id.endswith(handle) for handle in valid_upi_handles)

def verify_aadhar():
    uploaded_file = st.file_uploader("Upload Aadhar Card Image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        reader = easyocr.Reader(['en'])
        result = reader.readtext(io.BytesIO(uploaded_file.getvalue()), detail=0)
        
        for text in result:
            if re.match(r'\d{4} \d{4} \d{4}', text):
                st.success("✅ Aadhar Verified Successfully!")
                st.session_state.aadhar_verified = True
                return
        st.error("❌ Invalid Aadhar Card. Please upload a valid document.")

def add_sample_data():
    new_id = f'TXN{len(st.session_state.transactions) + 1}'
    upi_id = st.text_input("Enter UPI ID for transaction:", key=f'upi_input_{new_id}')
    amount = st.number_input("Enter Amount:", min_value=1, step=1, key=f'amount_{new_id}')
    location = st.text_input("Enter Transaction Location:", key=f'location_{new_id}')
    if st.button("Submit UPI", key=f'submit_{new_id}'):
        if is_valid_upi(upi_id):
            st.session_state.transactions.append({'id': new_id, 'status': 'Pending', 'upi': upi_id, 'amount': amount, 'location': location})
            st.rerun()
        else:
            st.error("Invalid UPI ID. Please enter a valid UPI ID based in India.")

def validate_transaction(index):
    st.session_state.transactions[index]['status'] = 'Validated'
    st.rerun()

def monitor_fraud():
    for txn in st.session_state.transactions:
        if txn['amount'] > 50000:
            alert = f"🚨 Fraud Alert: Transaction {txn['id']} with amount {txn['amount']} looks suspicious!"
            if alert not in st.session_state.fraud_alerts:
                st.session_state.fraud_alerts.append(alert)
        if txn['location'].lower() not in ['mumbai', 'delhi', 'bangalore']:
            alert = f"⚠️ Unusual Location: Transaction {txn['id']} from {txn['location']}!"
            if alert not in st.session_state.fraud_alerts:
                st.session_state.fraud_alerts.append(alert)

st.sidebar.subheader("🚨 Fraud Alerts")
for alert in st.session_state.fraud_alerts:
    st.sidebar.write(alert)

# PAN Verification Prototype
def verify_pan():
    pan_number = st.text_input("Enter PAN Number:")
    if st.button("Verify PAN"):
        if re.match(r'[A-Z]{5}[0-9]{4}[A-Z]', pan_number):
            st.success("✅ PAN Verified Successfully!")
            st.session_state.pan_verified = True
        else:
            st.error("❌ Invalid PAN Number. Please enter a valid PAN.")

# GSTIN Verification
def verify_gstin():
    gst_number = st.text_input("Enter GSTIN:")
    if st.button("Verify GSTIN"):
        if re.match(r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[Z]{1}[A-Z0-9]{1}', gst_number):
            st.success("✅ GSTIN Verified Successfully!")
            st.session_state.gst_verified = True
        else:
            st.error("❌ Invalid GSTIN. Please enter a valid GSTIN.")

# Streamlit UI
st.title("🚀 Decentralized Fraud Detection Dashboard")

# Aadhar Verification
st.subheader("🆔 Aadhar Verification")
verify_aadhar()

# PAN Verification
st.subheader("📜 PAN Verification")
verify_pan()

# GSTIN Verification
st.subheader("🛒 GSTIN Verification")
verify_gstin()

# Display transactions as a table
st.subheader("📋 Transaction Reports")
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    st.dataframe(df, width=700)
    for i, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 2, 2, 2, 2])
        col1.write(f"**{row['id']}**")
        col2.write(f"🚦 {row['status']}")
        col3.write(f"💰 {row['upi']}")
        col4.write(f"💲 {row['amount']}")
        col5.write(f"📍 {row['location']}")
        if col6.button("✅ Validate", key=f'btn_{i}'):
            validate_transaction(i)
else:
    st.info("No transactions available. Add a new transaction with a valid UPI ID.")

# Add sample data button
st.markdown("### 📌 Actions")
add_sample_data()

# Monitor fraud detection
monitor_fraud()
