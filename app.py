import streamlit as st
import difflib
import tempfile
import os

st.set_page_config(page_title="Document Comparison Tool", layout="wide")

st.title("📄 Document Comparison Tool")

# Upload files
file1 = st.file_uploader("Upload File 1", type=["txt"])
file2 = st.file_uploader("Upload File 2", type=["txt"])

def generate_diff_html(text1, text2):
    """Generate HTML diff highlighting changes from text1 to text2"""
    text1_lines = text1.splitlines()
    text2_lines = text2.splitlines()
    
    differ = difflib.HtmlDiff(wrapcolumn=80)
    html_diff = differ.make_file(text1_lines, text2_lines, 
                                 fromdesc='Original File', 
                                 todesc='Modified File',
                                 context=True, numlines=3)
    
    return html_diff

if file1 and file2:
    text1 = file1.read().decode("utf-8")
    text2 = file2.read().decode("utf-8")

    st.subheader("🔍 Differences Highlighted (Red = Removed from File 1)")
    
    # Generate diff HTML
    diff_html = generate_diff_html(text1, text2)

    # Save to temp HTML file
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html") as f:
        html_path = f.name
        f.write(diff_html)

    # Display in iframe
    st.components.v1.html(
        f"""
        <iframe src="file://{html_path}" width="100%" height="600px" style="border:none;"></iframe>
        """,
        height=620,
        scrolling=True
    )

    # Clean up on rerun
    if os.path.exists(html_path):
        os.remove(html_path)
else:
    st.info("Please upload both files to begin comparison.")

