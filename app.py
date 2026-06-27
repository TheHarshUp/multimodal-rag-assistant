import os
import streamlit as st

from utils.pdf_reader import read_pdf
from utils.table_parser import extract_tables
from utils.chunker import chunk_text
from utils.embedder import generate_embeddings
from utils.vector_store import store_embeddings, search
from utils.llm import ask_llm

os.makedirs("uploads", exist_ok=True)

st.set_page_config(
    page_title="Multimodal RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
# 🤖 Multimodal RAG Assistant
Ask questions across multiple PDFs with source citations
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_pdfs" not in st.session_state:
    st.session_state.processed_pdfs = set()

with st.sidebar:
    st.header("📂 Documents")

    uploaded_files = st.file_uploader(
        "Upload PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown("### Uploaded Files")
        for file in uploaded_files:
            status = "✅ Indexed" if file.name in st.session_state.processed_pdfs else "⏳ Processing"
            st.write(f"{status} — {file.name}")

    if st.button("🗑 Clear Chat"):
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

# -------- PDF PROCESSING --------
if uploaded_files:
    for uploaded_file in uploaded_files:

        if uploaded_file.name not in st.session_state.processed_pdfs:
            file_path = f"uploads/{uploaded_file.name}"

            with open(file_path, "wb") as f:
                f.write(uploaded_file.read())

            text = read_pdf(file_path)
            tables = []

            tables = []

            if uploaded_file.size < 2_000_000:
                tables = extract_tables(file_path)
            else:
                st.warning("Large PDF detected — skipping table extraction")

            table_text = ""

            for table_data in tables:
                page = table_data["page"]
                table = table_data["table"]

                table_text += f"\nTable from Page {page}:\n"

                for row in table:
                    cleaned_row = [
                        str(cell) if cell else ""
                        for cell in row
                    ]
                    table_text += " | ".join(cleaned_row) + "\n"

            combined_text = f"{text}\n{table_text}"

            chunks = chunk_text(combined_text)
            embeddings = generate_embeddings(chunks)

            store_embeddings(chunks, embeddings, uploaded_file.name)

            st.session_state.processed_pdfs.add(uploaded_file.name)
            st.rerun()

# -------- CHAT HISTORY --------
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "🧑"

    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# -------- QUESTION --------
question = st.chat_input("Ask anything about your documents...")

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.spinner("Thinking..."):
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