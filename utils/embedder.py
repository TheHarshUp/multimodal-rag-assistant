from sentence_transformers import SentenceTransformer

model = None

def generate_embeddings(text):
    global model

    if model is None:
        model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2",
            device="cpu"
        )

    return model.encode(text, convert_to_numpy=True)