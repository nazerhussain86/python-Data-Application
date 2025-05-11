import streamlit as st
import pdfplumber
import pandas as pd
import os
from io import BytesIO

st.set_page_config(page_title="PDF to Excel Table Extractor", layout="centered")
st.title("📄 PDF to Excel Table Extractor")

# Layout for file upload and convert button side by side
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"], key="pdf_upload")

with col2:
    convert_clicked = st.button("📤 Convert to Excel")

if uploaded_pdf and convert_clicked:
    with st.spinner("Extracting tables..."):
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
            st.error(f"Error extracting tables: {e}")
elif not uploaded_pdf and convert_clicked:
    st.warning("⚠️ Please upload a PDF file before converting.")

