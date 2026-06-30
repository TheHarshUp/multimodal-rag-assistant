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
from utils.vision_llm import ask_vision, classify_image
import re
from utils.ocr import extract_text_with_ocr

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

    # ADD HERE
    st.markdown("---")

    total_pdfs = len(st.session_state.processed_pdfs)
    total_images = sum(len(imgs) for imgs in st.session_state.images.values())
    total_tables = sum(len(tbls) for tbls in st.session_state.tables.values())

    st.markdown("### 📊 Project Stats")
    st.write(f"PDFs Loaded: {total_pdfs}")
    st.write(f"Images: {total_images}")
    st.write(f"Tables: {total_tables}")
    st.write("Text LLM: Llama 3")
    st.write("Vision: Qwen2.5 VL")

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

            try:
                text = read_pdf(file_path)

                ocr_pages = extract_text_with_ocr(file_path)

                ocr_text = ""
                for page_data in ocr_pages:
                    page_num = page_data["page"]
                    page_text = page_data["text"]

                    if len(page_text.strip()) > 20:
                        ocr_text += f"\n[PAGE {page_num}]\n{page_text}\n"

                text = ocr_text if len(text.strip()) < 50 else text + "\n" + ocr_text

            except Exception as e:
                st.error(f"PDF processing failed: {e}")
                continue

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
            image_data = message["image"]

            if isinstance(image_data, dict):
                st.image(image_data["path"], width=400)
            else:
                st.image(image_data, width=400)

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
        is_graph_query = any(
            word in question_lower
            for word in [
                "graph",
                "chart",
                "plot",
                "figure",
                "diagram",
                "visualization"
            ]
        )

        found = False

        for pdf_name, imgs in st.session_state.images.items():
            if len(imgs) > 0:
                selected_image = None

                if is_graph_query:
                    for img in imgs:

                        img_type = classify_image(img["path"])

                        if img_type == "graph":
                            selected_image = img
                            break
                else:
                    selected_image = imgs[0]
                if selected_image is None:
                    continue

                match = re.search(r"page\s*(\d+)", question_lower)

                if match:
                    requested_page = int(match.group(1))

                    for img in imgs:
                        if img["page"] == requested_page:
                            selected_image = img
                            break
                
                if selected_image is None:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "No graph found."
                    })
                    st.rerun()
                vision_prompt = f"""
                Analyze this image extracted from a PDF.

                User question:
                {question}

                If this is a graph:
                - Explain x-axis
                - Explain y-axis
                - Mention important trends
                - Mention key values
                """

                try:
                    answer = ask_vision(selected_image["path"], vision_prompt)
                except Exception as e:
                    answer = f"Vision model error: {e}"

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"🖼 Vision Analysis ({pdf_name}):\n\n{answer}",
                        "image": selected_image,
                    }
                )

                found = True
                break

        if not found:
            msg = "No graph found." if is_graph_query else "No extracted images found."

            st.session_state.messages.append(
                {"role": "assistant", "content": msg}
            )

        st.rerun()
    question_lower = question.lower()

    if "explain this pdf" in question_lower or "summarize this pdf" in question_lower:
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

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"📄 PDF Summary ({pdf_name}):\n\n{summary}",
                }
            )

            st.rerun()
            st.stop()
    match = re.search(r"page\s*(\d+)", question.lower())
    if match:
        requested_page = int(match.group(1))

        for pdf_name, pdf_text in st.session_state.pdf_texts.items():
            page_marker = f"[PAGE {requested_page}]"
            start = pdf_text.find(page_marker)

            if start != -1:
                matches = list(re.finditer(r"\[PAGE \d+\]", pdf_text))

                next_start = -1
                for m in matches:
                    if m.start() > start:
                        next_start = m.start()
                        break

                if next_start == -1:
                    page_text = pdf_text[start:]
                else:
                    page_text = pdf_text[start:next_start]

                if "summarize" in question.lower():
                    prompt = f"""
            ONLY use this page.

            Summarize this page in simple language.

            {page_text}
            """
                else:
                    prompt = f"""
            ONLY answer using this page.

            Page:
            {page_text}

            Question:
            {question}
            """

                answer = ask_llm(prompt, [page_text])

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                st.rerun()
                st.stop()
        
    with st.spinner("Thinking..."):
        try:
            question_embedding = generate_embeddings(question)
            active_sources = list(st.session_state.processed_pdfs)

            results, metadata = search(question_embedding, active_sources, top_k=3)
            answer = ask_llm(question, results)

        except Exception as e:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": f"LLM error: {e}"
                }
            )
            st.rerun()

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
