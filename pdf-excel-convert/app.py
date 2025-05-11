import streamlit as st
from pdf2docx import Converter
import os
from io import BytesIO
import pandas as pd
from docx import Document

st.set_page_config(page_title="PDF to Excel", layout="centered")

# Header
st.markdown("""
    <h1 style='text-align: center;'>📄 PDF ➜ Excel (Preserve Layout)</h1>
    <p style='text-align: center; font-size: 18px;'>Upload a PDF with tables or layout. We'll convert it directly to Excel (.xlsx) with layout preserved.</p>
""", unsafe_allow_html=True)

# Upload PDF
with st.container():
    st.markdown("---")
    col1, col2 = st.columns([4, 1])

    with col1:
        uploaded_pdf = st.file_uploader("**Step 1:** Upload your PDF", type=["pdf"], label_visibility="collapsed")
        st.caption("Max size: 200MB • Format: PDF")

    with col2:
        st.write("")  # spacing
        convert_clicked = st.button("📤 Convert to Excel", use_container_width=True)

# Conversion logic
if uploaded_pdf and convert_clicked:
    with st.spinner("🔄 Converting PDF to Excel..."):
        try:
            # Save uploaded PDF
            pdf_path = f"/tmp/{uploaded_pdf.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.read())

            # Convert PDF to Word first using pdf2docx
            word_filename = f"{os.path.splitext(uploaded_pdf.name)[0]}_layout.docx"
            word_path = f"/tmp/{word_filename}"

            converter = Converter(pdf_path)
            converter.convert(word_path, start=0, end=None)
            converter.close()

            # Load Word file to extract tables
            doc = Document(word_path)
            tables_data = []
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells]
                    tables_data.append(row_data)

            # If tables are found, create an Excel file
            if tables_data:
                df = pd.DataFrame(tables_data)
                excel_filename = f"{os.path.splitext(uploaded_pdf.name)[0]}_layout.xlsx"
                excel_buffer = BytesIO()
                df.to_excel(excel_buffer, index=False, header=False)
                excel_buffer.seek(0)

                # Provide the download button for Excel file
                st.success("✅ PDF converted to Excel successfully!")
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_buffer,
                    file_name=excel_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            else:
                st.warning("⚠️ No tables found in the PDF.")

        except Exception as e:
            st.error(f"❌ Error during conversion: {e}")

elif not uploaded_pdf and convert_clicked:
    st.warning("⚠️ Please upload a PDF file before converting.")
