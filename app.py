import streamlit as st
import fitz  # PyMuPDF
import difflib
import tempfile
import os
import base64

st.set_page_config(page_title="PDF Comparison Tool", layout="wide")
st.title("📄 PDF Comparison Tool")

# --- Helper Functions ---

def extract_text_from_pdf(uploaded_file):
    """Extract text from PDF using PyMuPDF"""
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def generate_diff_html(text1, text2):
    """Generate HTML diff with highlighting"""
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
    """Embed PDF in HTML iframe using base64"""
    base64_pdf = base64.b64encode(file.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" style="border:none;"></iframe>'
    return pdf_display

# --- Upload PDFs ---
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload PDF File 1 (Original)", type="pdf", key="file1")
    if file1:
        st.markdown("#### 📄 Original PDF Preview")
        st.markdown(display_pdf(file1), unsafe_allow_html=True)

with col2:
    file2 = st.file_uploader("Upload PDF File 2 (Modified)", type="pdf", key="file2")
    if file2:
        st.markdown("#### 📝 Modified PDF Preview")
        st.markdown(display_pdf(file2), unsafe_allow_html=True)

# --- Compare Button ---
if file1 and file2:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
    compare = st.button("🔍 Compare PDFs")
    st.markdown("</div>", unsafe_allow_html=True)

    if compare:
        with st.spinner("Comparing documents..."):
            # Rewind file pointers after preview display
            file1.seek(0)
            file2.seek(0)

            text1 = extract_text_from_pdf(file1)
            text2 = extract_text_from_pdf(file2)
            diff_html = generate_diff_html(text1, text2)

            # Save comparison HTML
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
                html_path = f.name
                f.write(diff_html)

        st.markdown("### 🔄 Differences Highlighted (Red = Removed | Green = Added)")
        st.components.v1.html(
            f"""<iframe src="file://{html_path}" width="100%" height="600px" style="border:none;"></iframe>""",
            height=620,
            scrolling=True
        )

else:
    st.info("Upload both PDF files to enable comparison.")
