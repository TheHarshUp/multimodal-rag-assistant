from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:1234/v1",
    api_key="lm-studio"
)


def ask_llm(question, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
Answer using only the provided context.

Give concise and clear answers.
If answer is not present, say "I don't know".

Context:
{context}

Question:
{question}

Answer:
"""

    response = client.chat.completions.create(
        model="meta-llama-3-8b-instruct",
        messages=[{
            "role": "user",
            "content": prompt
        }],
        temperature=0.2
    )

    return response.choices[0].message.content