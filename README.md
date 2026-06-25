# Multimodal PDF RAG Assistant (Local LLM)

A Retrieval-Augmented Generation (RAG) application that allows users to upload multiple PDF documents and ask questions using a locally hosted Large Language Model (LLM).

This project uses vector embeddings and semantic search to retrieve relevant information from PDFs, then generates context-aware answers using a self-hosted Llama 3 model via LM Studio.

---

## Live Features

* Upload multiple PDF documents simultaneously
* Extract text from PDFs
* Split documents into chunks for retrieval
* Generate semantic embeddings
* Store embeddings in ChromaDB
* Retrieve top relevant chunks using similarity search
* Generate context-aware answers using a local LLM
* Display source citations for each answer
* Interactive chat UI built with Streamlit
* No cloud API dependency (fully local inference)

---

## Tech Stack

* Python
* Streamlit
* ChromaDB
* Sentence Transformers
* LM Studio
* Meta Llama 3 8B Instruct (GGUF)
* PyPDF

---

## Project Workflow

1. User uploads one or more PDF files
2. PDF text is extracted
3. Text is split into chunks
4. Embeddings are generated for each chunk
5. Embeddings are stored in ChromaDB
6. User asks a question
7. Question embedding is generated
8. Similar chunks are retrieved
9. Local LLM generates answer using retrieved context
10. Source PDF citations are displayed

---

## Architecture

```bash
User Uploads PDFs
       |
       v
+------------------+
|   PDF Reader     |
+------------------+
       |
       v
+------------------+
|    Chunking      |
+------------------+
       |
       v
+------------------+
| Embedding Model  |
| MiniLM-L6-v2     |
+------------------+
       |
       v
+------------------+
|   ChromaDB       |
| Vector Database  |
+------------------+
       |
       v
+------------------+
| Similarity Search|
+------------------+
       |
       v
+------------------+
| LM Studio Server |
| Llama 3 8B LLM   |
+------------------+
       |
       v
Answer + Source Citation
```

---

## Project Structure

```bash
rag-project/
│
├── app.py
├── requirements.txt
├── README.md
├── uploads/
├── chroma_db/
│
└── utils/
    ├── chunker.py
    ├── embedder.py
    ├── llm.py
    ├── pdf_reader.py
    └── vector_store.py
```

---

## Installation

Clone repository:

```bash
git clone https://github.com/TheHarshUp/pdf-rag-chatbot.git
cd pdf-rag-chatbot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run LM Studio local server and load model:

* Open LM Studio
* Download Llama 3 8B Instruct GGUF
* Start Local Server on port 1234

Run application:

```bash
streamlit run app.py
```

---

## Key Improvements (V2)

### Multi-PDF Retrieval

Users can upload multiple PDFs and query across all documents.

### Source Citations

Every answer shows which document the information came from.

### Local LLM Hosting

Replaced Groq cloud inference with LM Studio local inference.

Benefits:

* No token cost
* Better privacy
* Offline capability
* Demonstrates self-hosted AI deployment

---

## Challenges Solved

* Managing Streamlit session state
* Resetting vector database for new uploads
* Multi-document retrieval
* Source tracking for answers
* Migrating from Groq API to LM Studio local server

---

## Future Improvements (V3)

* OCR support for scanned PDFs
* Table extraction from PDFs
* Graph and image understanding
* Better semantic chunking
* Hybrid search (keyword + vector search)
* Chat history export

---

## Demo Screenshot

Will be added after final UI improvements.
