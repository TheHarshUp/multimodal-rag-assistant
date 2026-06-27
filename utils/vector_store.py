import chromadb
import uuid

client = None
collection = None

def get_collection():
    global client, collection

    if collection is None:
        client = chromadb.PersistentClient(path="chroma_db")
        collection = client.get_or_create_collection(
            name="pdf_chunks"
        )

    return collection


def store_embeddings(chunks, embeddings, pdf_name):
    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [{"source": pdf_name} for _ in chunks]

    collection.add(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )


def search(query_embedding, top_k=3):
    collection = get_collection()

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
            if hasattr(query_embedding, "tolist")
            else list(query_embedding)
        ],
        n_results=top_k
    )

    return (
        results["documents"][0],
        results["metadatas"][0]
    )