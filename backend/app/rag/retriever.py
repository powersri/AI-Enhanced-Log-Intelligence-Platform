import math
from pathlib import Path

from app.config import settings
from app.rag.embedder import embed_text


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def load_knowledge_documents() -> list[dict]:
    kb_path = Path(settings.RAG_KNOWLEDGE_DIR)
    docs = []

    for file_path in kb_path.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")
        docs.append({
            "source": file_path.name,
            "text": text,
        })

    return docs


def retrieve_relevant_docs(query_text: str, top_k: int = 3) -> list[dict]:
    query_embedding = embed_text(query_text)
    docs = load_knowledge_documents()

    scored_docs = []
    for doc in docs:
        doc_embedding = embed_text(doc["text"])
        score = cosine_similarity(query_embedding, doc_embedding)
        scored_docs.append({
            "source": doc["source"],
            "text": doc["text"],
            "score": score,
        })

    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    return scored_docs[:top_k]