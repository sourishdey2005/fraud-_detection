import streamlit as st
import pandas as pd
import re
import google.generativeai as genai
import easyocr
from PIL import Image
import io

# Set up Gemini API key
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# Initialize session state for transactions if not already present
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'aadhar_verified' not in st.session_state:
    st.session_state.aadhar_verified = False

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

def add_sample_data():
    new_id = f'TXN{len(st.session_state.transactions) + 1}'
    upi_id = st.text_input("Enter UPI ID for transaction:", key=f'upi_input_{new_id}')
    if st.button("Submit UPI", key=f'submit_{new_id}'):
        if is_valid_upi(upi_id):
            st.session_state.transactions.append({'id': new_id, 'status': 'Pending', 'upi': upi_id})
            st.rerun()
        else:
            st.error("Invalid UPI ID. Please enter a valid UPI ID based in India.")

def validate_transaction(index):
    st.session_state.transactions[index]['status'] = 'Validated'
    st.rerun()

# Aadhar Verification Prototype
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

# Bank Details Linking with QR Code Scanner
def scan_qr_code():
    uploaded_qr = st.file_uploader("Upload QR Code Image for Bank Linking", type=["jpg", "jpeg", "png"], key="qr")
    if uploaded_qr:
        reader = easyocr.Reader(['en'])
        result = reader.readtext(io.BytesIO(uploaded_qr.getvalue()), detail=0)
        
        for text in result:
            if "upi" in text.lower():
                st.success(f"✅ Bank Details Linked: {text}")
                return
        st.error("❌ Invalid QR Code. Please upload a valid UPI-linked QR Code.")

# Streamlit UI
st.set_page_config(page_title="Decentralized Fraud Detection System", layout="wide")
st.title("🚀 Decentralized Fraud Detection Dashboard")

# Styling
st.markdown("""
    <style>
        .css-18e3th9 {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
    </style>
""", unsafe_allow_html=True)

# Aadhar Verification
st.subheader("🆔 Aadhar Verification")
verify_aadhar()

# Bank Linking with QR Scanner
st.subheader("🏦 Bank Linking via QR Code")
scan_qr_code()

# Display transactions as a table
st.subheader("📋 Transaction Reports")
if st.session_state.transactions:
    df = pd.DataFrame(st.session_state.transactions)
    st.dataframe(df, width=700)
    
    for i, row in df.iterrows():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
        col1.write(f"**{row['id']}**")
        col2.write(f"🚦 {row['status']}")
        col3.write(f"💰 {row['upi']}")
        if col4.button("✅ Validate", key=f'btn_{i}'):
            validate_transaction(i)
else:
    st.info("No transactions available. Add a new transaction with a valid UPI ID.")

# Add sample data button
st.markdown("### 📌 Actions")
add_sample_data()
