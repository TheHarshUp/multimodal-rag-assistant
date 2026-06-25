import streamlit as st

from utils.embedder import generate_embeddings
from utils.vector_store import search, store_embeddings
from utils.llm import ask_llm
from utils.pdf_reader import read_pdf
from utils.chunker import chunk_text

import os
os.makedirs("uploads", exist_ok=True)

st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
section[data-testid="stSidebar"] {
    width: 280px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
# 🤖 Multimodal RAG Assistant
Ask questions across multiple PDFs with source citations
""")

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("📂 Documents")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if "processed_pdfs" in st.session_state:
        for pdf in st.session_state.processed_pdfs:
            st.write(f"✅ {pdf}")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.markdown("""
<style>
    section[data-testid="stSidebar"] {
        width: 280px !important;
    }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.info("""
### 👋 Welcome
Upload PDFs and ask:
- Explain concepts
- Summarize chapters
- Compare documents
- Find tables / graphs
""")

if "processed_pdfs" not in st.session_state:
    st.session_state.processed_pdfs = set()

if uploaded_files:
    processed_any = False

    for uploaded_file in uploaded_files:

        if uploaded_file.name not in st.session_state.processed_pdfs:
            processed_any = True

            file_path = f"uploads/{uploaded_file.name}"

            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            with st.spinner(f"Processing {uploaded_file.name}..."):

                text = read_pdf(file_path)
                chunks = chunk_text(text)
                embeddings = generate_embeddings(chunks)

                store_embeddings(chunks, embeddings, uploaded_file.name)

            st.session_state.processed_pdfs.add(uploaded_file.name)

    if processed_any:
        st.toast("All PDFs indexed successfully! 🎉")


for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "🧑"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

question = st.chat_input("Ask anything about your documents...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    question_embedding = generate_embeddings(question)

    results, metadata = search(question_embedding, top_k=3)

    answer = ask_llm(question, results)

    sources = list(set(
        meta["source"]
        for meta in metadata
        if meta is not None and "source" in meta
    ))

    formatted_answer = f"""
{answer}

---
📄 Sources: {", ".join(sources)}
"""

    st.session_state.messages.append({
        "role": "assistant",
        "content": formatted_answer
    })

    st.rerun()
