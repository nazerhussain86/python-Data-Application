import streamlit as st
from pdf2docx import Converter
import os
from io import BytesIO

st.set_page_config(page_title="PDF to Word to Excel", layout="centered")

# Header
st.markdown("""
    <h1 style='text-align: center;'>📄 PDF ➜ Word ➜ Excel (Preserve Layout)</h1>
    <p style='text-align: center; font-size: 18px;'>Upload a PDF with tables or layout. We'll convert it to Word (.docx) with layout preserved. You can open this Word file in Excel.</p>
""", unsafe_allow_html=True)

# Upload and convert layout
with st.container():
    st.markdown("---")
    col1, col2 = st.columns([4, 1])

    with col1:
        uploaded_pdf = st.file_uploader("**Step 1:** Upload your PDF", type=["pdf"], label_visibility="collapsed")
        st.caption("Max size: 200MB • Format: PDF")

    with col2:
        st.write("")  # spacing
        convert_clicked = st.button("📤 Convert", use_container_width=True)

# Conversion logic
if uploaded_pdf and convert_clicked:
    with st.spinner("🔄 Converting PDF to Word..."):
        try:
            # Save uploaded PDF
            pdf_path = f"/tmp/{uploaded_pdf.name}"
            with open(pdf_path, "wb") as f:
                f.write(uploaded_pdf.read())

            # Set output path
            word_filename = f"{os.path.splitext(uploaded_pdf.name)[0]}_layout.docx"
            word_path = f"/tmp/{word_filename}"

            # Convert PDF to Word
            converter = Converter(pdf_path)
            converter.convert(word_path, start=0, end=None)
            converter.close()

            # Load Word file as BytesIO
            output = BytesIO()
            with open(word_path, "rb") as f:
                output.write(f.read())
            output.seek(0)

            st.success("✅ PDF converted to Word with layout preserved!")
            st.download_button(
                label="📥 Download Word File (Open in Excel)",
                data=output,
                file_name=word_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

            st.info("💡 Open the downloaded .docx file in Excel to maintain layout and extract tables.")

        except Exception as e:
            st.error(f"❌ Error during conversion: {e}")

elif not uploaded_pdf and convert_clicked:
    st.warning("⚠️ Please upload a PDF file before converting.")
