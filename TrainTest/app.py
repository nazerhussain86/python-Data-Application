from langchain_community.llms import CTransformers
from langchain.agents import Tool
from langchain.agents import AgentType, initialize_agent
from langchain.chains import RetrievalQA
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import tempfile
import os
import streamlit as st
import sys
from langchain.callbacks.tracers import ConsoleCallbackHandler

# Load the model
def load_llm():
    try:
        llm = CTransformers(
            model="TheBloke/Llama-2-7B-Chat-GGML",
            model_type="llama",
            max_new_tokens=512,
            temperature=0.7
        )
        return llm
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        return None

# Load and process PDF files
def process_pdf(pdf_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        # Create embeddings and store in FAISS
        embeddings = HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        db = FAISS.from_documents(texts, embeddings)

        return db
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
        return None

# Initialize the QA system
def initialize_qa_system(db):
    try:
        llm = load_llm()
        if llm is None:
            return None
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever()
        )
        return qa
    except Exception as e:
        st.error(f"Error initializing QA system: {e}")
        return None

# Function to compare new file with trained model
def compare_with_trained_model(trained_db, new_db, threshold=0.8):
    try:
        # Retrieve the most similar documents from the trained index
        similar_docs = trained_db.similarity_search_with_score(new_db.docstore._dict.values(), k=1)

        # Check if the most similar document is above the threshold
        if similar_docs and similar_docs[0][1] > threshold:
            return False  # Not a new file
        else:
            return True  # New file
    except Exception as e:
        st.error(f"Error comparing files: {e}")
        return None

# Streamlit app
def main():
    st.title("PDF File Comparison System")

    # Create tabs
    tab1, tab2 = st.tabs(["Train Model", "Check File"])

    with tab1:
        st.header("Upload PDFs for Training")
        uploaded_files_train = st.file_uploader("Choose PDF files for training", type="pdf", accept_multiple_files=True, key="train_uploader")

        if st.button("Train", key="train_button"):
            if uploaded_files_train:
                # Process the uploaded files and create a FAISS index
                db_list = []
                for uploaded_file in uploaded_files_train:
                    db = process_pdf(uploaded_file)
                    if db is not None:
                        db_list.append(db)

                # Merge the FAISS indexes
                if db_list:
                    merged_db = db_list[0]
                    for db in db_list[1:]:
                        merged_db.merge_from(db)

                    st.session_state['trained_db'] = merged_db
                    st.write("Model trained and ready for comparison.")
                else:
                    st.write("No files uploaded for training.")
            else:
                st.write("No files uploaded for training.")

    with tab2:
        st.header("Upload PDF for Checking")
        uploaded_file_check = st.file_uploader("Choose a PDF file to check", type="pdf", key="check_uploader")

        if st.button("Check", key="check_button"):
            if uploaded_file_check is not None and 'trained_db' in st.session_state:
                # Process the uploaded file for checking
                check_db = process_pdf(uploaded_file_check)
                if check_db is not None:
                    # Compare the new file with the trained model
                    is_new_file = compare_with_trained_model(st.session_state['trained_db'], check_db)

                    if is_new_file is not None:
                        if is_new_file:
                            st.write("This PDF is a new file.")
                        else:
                            st.write("This PDF is the same as the previously trained files.")
            else:
                st.write("Please upload a PDF file to check and ensure the model is trained.")

if __name__ == "__main__":
    main()
