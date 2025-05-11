import streamlit as st
import pdfplumber
import pandas as pd
import os
from io import BytesIO

# Page setup
st.set_page_config(page_title="PDF to Excel Table Extractor", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .upload-section {
        border: 2px dashed #dee2e6;
        border-radius: 12px;
        padding: 30px;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 10px;
        background-color: #ff4b4b;
        color: white;
        height: 3em;
        font-weight: 600;
        transition: 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #d73838;
        transform: scale(1.03);
    }
    .stDownloadButton>button {
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <h1 style='text-align: center;'>📄 PDF to Excel Table Extractor</h1>
    <p style='text-align: center; font-size: 18px;'>Upload a PDF file containing tables and convert them into Excel format.</p>
""", unsafe_allow_html=True)

# Upload and convert section
with st.container():
    st.markdown("### Step 1: Upload PDF File")
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader(" ", type=["pdf"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("### Step 2: Convert to Excel")
    convert_clicked = st.button("📤 Convert to Excel", use_container_width=True)

# Conversion logic
if uploaded_pdf and convert_clicked:
    with st.spinner("🔄 Extracting tables from PDF..."):
        try:
            original_name = os.path.splitext(uploaded_pdf.name)[0]
            output_excel_name = f"{original_name}_excel.xlsx"

            with pdfplumber.open(uploaded_pdf) as pdf:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for page_num, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        if not tables:
                            continue
                        for table_num, table in enumerate(tables):
                            df = pd.DataFrame(table[1:], columns=table[0])
                            sheet_name = f"Page{page_num+1}_Table{table_num+1}"
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                output.seek(0)

            st.success("✅ Tables extracted and saved to Excel!")
            st.download_button(
                label="📥 Download Excel File",
                data=output,
                file_name=output_excel_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        except Exception as e:
            st.error(f"❌ Error extracting tables: {e}")
elif not uploaded_pdf and convert_clicked:
    st.warning("⚠️ Please upload a PDF file before converting.")
