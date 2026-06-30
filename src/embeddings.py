import math
import requests

OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"


def embed(text: str) -> list:
    response = requests.post(OLLAMA_EMBED_URL, json={
        "model": EMBED_MODEL,
        "input": text,
    })
    response.raise_for_status()
    return response.json()["embeddings"][0]


def cosine_similarity(a: list, b: list) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)