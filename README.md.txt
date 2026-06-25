# PDF RAG Chatbot using ChromaDB and Groq LLM

## Live Demo

[Try the App Here](https://pdf-rag-chatbot-2izdqetqvpmm5spepoc4qs.streamlit.app/)

A cloud-deployed Retrieval-Augmented Generation (RAG) chatbot that allows users to upload PDF documents and ask questions based on the document content.

---

## Features

* Upload PDF files
* Extract text from PDFs
* Split text into semantic chunks
* Generate vector embeddings
* Store embeddings in ChromaDB
* Retrieve relevant chunks using similarity search
* Generate context-aware answers using Groq LLM
* Interactive chat interface using Streamlit

---

## Tech Stack

* Python
* Streamlit
* ChromaDB
* Sentence Transformers
* Groq API (Llama 3.3 70B)
* PyPDF

---

## Project Workflow

1. User uploads a PDF
2. PDF text is extracted
3. Text is divided into chunks
4. Embeddings are generated for each chunk
5. Embeddings are stored in ChromaDB
6. User asks a question
7. Question embedding is generated
8. Top relevant chunks are retrieved
9. LLM generates an answer using retrieved context

---

## Architecture

```bash
PDF Upload
    │
    ▼
PDF Parser (PyPDF)
    │
    ▼
Text Chunking
    │
    ▼
Embedding Model
(Sentence Transformers)
    │
    ▼
ChromaDB Vector Store
    │
    ▼
Similarity Search
    │
    ▼
Groq LLM
(Llama 3.3 70B)
    │
    ▼
Final Response
```


## Project Structure

```bash
pdf-rag-chatbot/
│
├── app.py
├── requirements.txt
├── README.md
└── utils/
    ├── chunker.py
    ├── embedder.py
    ├── llm.py
    ├── pdf_reader.py
    └── vector_store.py
```

---

## Setup & Installation

Clone the repository:

```bash
git clone https://github.com/TheHarshUp/pdf-rag-chatbot.git
cd pdf-rag-chatbot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create environment variables:

```env
GROQ_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

---

## Challenges Solved

* Managing Streamlit session state for persistent chat history
* Handling vector database reset when users upload new PDFs
* Deploying a complete RAG pipeline on Streamlit Cloud
* Migrating from local Ollama inference to cloud-based Groq API

---

## Future Improvements

* Multi-PDF support
* Better UI/UX
* Source citations for answers
* Chat history export
* Conversation memory

---

## Demo Screenshot

*(Will be added after UI improvements)*
