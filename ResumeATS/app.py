import streamlit as st
import pdfplumber
import pandas as pd
import numpy as np
import spacy
from sentence_transformers import SentenceTransformer, util

# Load spaCy model for keyword extraction
nlp = spacy.load("en_core_web_sm")

# Load Sentence Transformer model from Hugging Face
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')
model = load_model()

def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_keywords(text, top_n=10):
    doc = nlp(text)
    keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'PROPN']]
    freq = pd.Series(keywords).value_counts()
    return freq.head(top_n).index.tolist()

def compute_similarity(resume_text, jd_text):
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(resume_emb, jd_emb)
    return float(similarity[0][0])

st.set_page_config(page_title="ATS Resume Matcher", layout="wide")
st.title("AI-Powered ATS Resume Matcher (Hugging Face Model)")

st.markdown("""
Upload one or more PDF resumes and enter a job description. The app will rank resumes based on their semantic similarity to the job description using state-of-the-art NLP models.
""")

jd_text = st.text_area("Paste the Job Description Here", height=200)
uploaded_files = st.file_uploader("Upload Resume PDFs", type=["pdf"], accept_multiple_files=True)

if 'results_df' not in st.session_state:
    st.session_state['results_df'] = None

if st.button("Rank Resumes"):
    if not jd_text:
        st.warning("Please enter a job description.")
        st.session_state['results_df'] = None
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
        st.session_state['results_df'] = None
    else:
        results = []
        jd_keywords = extract_keywords(jd_text)
        for file in uploaded_files:
            resume_text = extract_text_from_pdf(file)
            similarity = compute_similarity(resume_text, jd_text)
            resume_keywords = extract_keywords(resume_text)
            missing_keywords = set(jd_keywords) - set(resume_keywords)
            results.append({
                "Resume Name": file.name,
                "Similarity Score": round(similarity * 100, 2),
                "Missing Keywords": ", ".join(missing_keywords)
            })
        results_df = pd.DataFrame(results).sort_values(by="Similarity Score", ascending=False)
        st.session_state['results_df'] = results_df.reset_index(drop=True)
        st.success("Ranking complete!")

if st.session_state['results_df'] is not None:
    st.subheader("Ranking Results")
    st.dataframe(st.session_state['results_df'])
    st.bar_chart(st.session_state['results_df'].set_index("Resume Name")["Similarity Score"])
else:
    st.info("Please upload at least one resume and enter a job description to start.")

