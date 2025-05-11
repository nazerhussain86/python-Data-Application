import streamlit as st
import fitz  # PyMuPDF
import difflib
import tempfile
import os
import base64
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO

st.set_page_config(page_title="PDF Comparison Tool with OCR", layout="wide")
st.title("📄 PDF Comparison Tool with OCR Support")

# --- Helper Functions ---

def extract_text_from_pdf(pdf_file):
    """Try text extraction from standard PDFs, fallback to OCR if empty"""
    pdf_file.seek(0)
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    if not text.strip():
        pdf_file.seek(0)
        text = extract_text_using_ocr(pdf_file)
    return text

def extract_text_using_ocr(pdf_file):
    """Extract text from scanned PDFs using OCR"""
    images = convert_from_bytes(pdf_file.read())
    ocr_text = ""
    for img in images:
        ocr_text += pytesseract.image_to_string(img)
    return ocr_text

def generate_diff_html(text1, text2):
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()
    differ = difflib.HtmlDiff(wrapcolumn=80)
    return differ.make_file(
        text1_lines, text2_lines,
        fromdesc="Original PDF",
        todesc="Modified PDF",
        context=True,
        numlines=3
    )

def display_pdf(file):
    """Embed PDF in iframe using base64 encoding (safe for Chrome)"""
    file.seek(0)
    file_data = file.read()
    base64_pdf = base64.b64encode(file_data).decode("utf-8")
    return f'''
        <iframe
            src="data:application/pdf;base64,{base64_pdf}"
            width="100%"
            height="600px"
            style="border: 1px solid #ccc; border-radius: 10px;"
        ></iframe>
    '''


def download_button_html(file_path, label):
    """Generate download link for HTML file"""
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    b64 = base64.b64encode(html_content.encode()).decode()
    return f'<a href="data:text/html;base64,{b64}" download="comparison_result.html">{label}</a>'

# --- Upload PDFs ---
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload PDF File 1 (Original)", type="pdf", key="file1")
    #if file1:
        #st.markdown("#### 📄 Original PDF Preview")
        #st.markdown(display_pdf(file1), unsafe_allow_html=True)

with col2:
    file2 = st.file_uploader("Upload PDF File 2 (Modified)", type="pdf", key="file2")
    #if file2:
        #st.markdown("#### 📝 Modified PDF Preview")
        #st.markdown(display_pdf(file2), unsafe_allow_html=True)


# --- Compare Button ---
if file1 and file2:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    compare = st.button("🔍 Compare PDFs")
    st.markdown("</div>", unsafe_allow_html=True)

    if compare:
        with st.spinner("Performing comparison (including OCR if needed)..."):
            file1.seek(0)
            file2.seek(0)
            text1 = extract_text_from_pdf(file1)
            file1.seek(0)
            file2.seek(0)
            text2 = extract_text_from_pdf(file2)
            diff_html = generate_diff_html(text1, text2)

            # Save to HTML file
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
                html_path = f.name
                f.write(diff_html)

        st.markdown("### 🔄 Differences Highlighted")
        with open(html_path, "r", encoding="utf-8") as f:
            diff_html_content = f.read()
        st.components.v1.html(diff_html_content, height=600, scrolling=True)

        st.markdown("### ⬇️ Download Result")
        st.markdown(download_button_html(html_path, "📥 Download HTML Comparison"), unsafe_allow_html=True)

else:
    st.info("Upload both PDFs to enable comparison.")
