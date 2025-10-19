import streamlit as st
import os
import time
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Load environment variables
load_dotenv()

# Load Groq API Key
groq_api_key = os.getenv("GROQ_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Initialize LLM
llm = ChatGroq(groq_api_key=groq_api_key, model="llama-3.1-8b-instant")

# Prompt Template
prompt = ChatPromptTemplate.from_template(
    """
    Answer the question based on the context only.
    Please provide the most accurate response based on the question.
    <context> {context} <context>
    Question: {input}
    """
)

# Function to create vector embeddings
def create_vector_embeddings():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        st.session_state.loader = PyPDFDirectoryLoader("../PDFDocuments")  # Data Ingestion
        st.session_state.documents = st.session_state.loader.load()  # Document Loading
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(
            st.session_state.documents
        )  # Text Splitting
        st.session_state.vectors = FAISS.from_documents(
            st.session_state.final_documents, st.session_state.embeddings
        )  # Vector Embeddings

# Streamlit UI
st.title("📘 PDF RAG Chatbot using LangChain + Groq")

user_prompt = st.text_input("Enter your question here:")

if st.button("Document Embedding"):
    create_vector_embeddings()
    st.success("✅ Document Embedding Created Successfully!")

# Query section
if user_prompt:
    if "vectors" not in st.session_state:
        st.warning("Please create document embeddings first!")
    else:
        document_chain = create_stuff_documents_chain(llm, prompt)
        retriever = st.session_state.vectors.as_retriever()
        retrieval_chain = create_retrieval_chain(retriever, document_chain)

        start = time.process_time()
        response = retrieval_chain.invoke({"input": user_prompt})
        st.write("Response Time:", time.process_time() - start)

        # Debug: Show response keys
        st.write("**Debug - Response keys:**", list(response.keys()))
        
        # Display response
        st.write("### Response:")
        st.write(response.get("answer", response.get("output", "No output found.")))

        # Display relevant context documents
        with st.expander("See Relevant Documents"):
            context_docs = response.get("context", [])
            for i, doc in enumerate(context_docs):
                st.write(f"**Document {i+1}:**")
                st.write(doc.page_content)
                st.write("---------------")
