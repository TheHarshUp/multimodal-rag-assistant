import chromadb

chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="pdf_chunks")


def store_embeddings(chunks, embeddings, pdf_name):
    import uuid

    chunk_ids = [str(uuid.uuid4()) for _ in chunks]

    metadatas = [{"source": pdf_name} for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=chunk_ids,
        metadatas=metadatas
    )


def search(query_embedding, top_k):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return (
        results["documents"][0],
        results["metadatas"][0]
    )

