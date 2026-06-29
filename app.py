import os
import streamlit as st
import pandas as pd
from utils.pdf_reader import read_pdf
from utils.table_parser import extract_tables
from utils.chunker import chunk_text
from utils.embedder import generate_embeddings
from utils.vector_store import store_embeddings, search
from utils.llm import ask_llm
from utils.image_extractor import extract_images
from utils.vision_llm import ask_vision
import re

os.makedirs("uploads", exist_ok=True)

st.set_page_config(page_title="Multimodal RAG Assistant", page_icon="🤖", layout="wide")

st.markdown("""
# 🤖 Multimodal RAG Assistant
Ask questions across multiple PDFs with source citations
""")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "processed_pdfs" not in st.session_state:
    st.session_state.processed_pdfs = set()
if "pdf_texts" not in st.session_state:
    st.session_state.pdf_texts = {}

if "tables" not in st.session_state:
    st.session_state.tables = {}

if "images" not in st.session_state:
    st.session_state.images = {}

with st.sidebar:
    st.header("📂 Documents")

    uploaded_files = st.file_uploader(
        "Upload PDFs", type=["pdf"], accept_multiple_files=True
    )

    if uploaded_files:
        st.markdown("### Uploaded Files")
        for file in uploaded_files:
            status = (
                "✅ Indexed"
                if file.name in st.session_state.processed_pdfs
                else "⏳ Processing"
            )
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
            st.session_state.pdf_texts[uploaded_file.name] = text
            image_paths = extract_images(file_path)
            st.session_state.images[uploaded_file.name] = image_paths
            st.write(f"Extracted {len(image_paths)} images")

            tables = []
            if uploaded_file.size < 2_000_000:
                tables = extract_tables(file_path)
                st.session_state.tables[uploaded_file.name] = tables
            else:
                st.warning("Large PDF detected — skipping table extraction")

            table_text = ""

            for table_data in tables:
                page = table_data["page"]
                table = table_data["table"]

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

        if "image" in message:
            st.image(message["image"], width=400)

        st.markdown(message["content"])

        if message["content"] == "📊 Here are the extracted tables:":
            for pdf_name, pdf_tables in st.session_state.tables.items():
                st.subheader(f"📄 {pdf_name}")

                for i, table_data in enumerate(pdf_tables):
                    page = table_data["page"]
                    table = table_data["table"]

                    st.markdown(f"### Table {i + 1} (Page {page})")

                    if len(table) > 1:
                        headers = table[0]
                        rows = table[1:]

                        df = pd.DataFrame(rows, columns=headers)
                        st.dataframe(df, width="stretch")

# -------- QUESTION --------
question = st.chat_input("Ask anything about your documents...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    if "table" in question.lower():
        st.session_state.messages.append(
            {"role": "assistant", "content": "📊 Here are the extracted tables:"}
        )

        st.rerun()
    question_lower = question.lower()

    if (
        "image" in question_lower
        or "graph" in question_lower
        or "chart" in question_lower
        or "figure" in question_lower
    ):
        found = False

        for pdf_name, imgs in st.session_state.images.items():
            if len(imgs) > 0:
                selected_image = imgs[0]

                match = re.search(r'page\s*(\d+)', question_lower)

                if match:
                    requested_page = match.group(1)

                    for img in imgs:
                        if f"page_{requested_page}_" in img:
                            selected_image = img
                            break
                answer = ask_vision(selected_image, question)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🖼 Vision Analysis ({pdf_name}):\n\n{answer}",
                    "image": selected_image
                })

                found = True
                break

        if not found:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "No extracted images found."
            })

        st.rerun()
    question_lower = question.lower()

    if (
        "explain this pdf" in question_lower
        or "summarize this pdf" in question_lower
    ):
        for pdf_name, pdf_text in st.session_state.pdf_texts.items():

            summary_context = pdf_text[:20000]

            summary_question = """
    Summarize this PDF in simple language.

    Include:
    1. What this document is about
    2. Main topics
    3. Important findings / key points
    """

            summary = ask_llm(summary_question, [summary_context])

            st.session_state.messages.append({
                "role": "assistant",
                "content": f"📄 PDF Summary ({pdf_name}):\n\n{summary}"
            })

            st.rerun()
            st.stop()
    with st.spinner("Thinking..."):
        question_embedding = generate_embeddings(question)
        active_sources = list(st.session_state.processed_pdfs)

        results, metadata = search(
            question_embedding,
            active_sources,
            top_k=3
        )
        answer = ask_llm(question, results)

        sources = list(
            set(
                meta["source"]
                for meta in metadata
                if meta is not None and "source" in meta
            )
        )

        formatted_answer = f"""
{answer}

---
📄 Sources: {", ".join(sources)}
"""

        st.session_state.messages.append(
            {"role": "assistant", "content": formatted_answer}
        )

    st.rerun()
