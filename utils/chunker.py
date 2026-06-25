def chunk_text(text):
    text = text.replace("\n", " ")
    words = text.split()

    chunk_size = 150
    overlap = 30

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append(chunk)

    return chunks
