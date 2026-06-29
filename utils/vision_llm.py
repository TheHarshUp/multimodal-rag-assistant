import requests
import base64


def ask_vision(image_path, prompt):
    with open(image_path, "rb") as f:
        image_base64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {
        "model": "qwen2-vl-2b-instruct",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2,
        "max_tokens": 500
    }

    response = requests.post(
        "http://127.0.0.1:1234/v1/chat/completions",
        json=payload
    )
    result = response.json()
    return result["choices"][0]["message"]["content"]