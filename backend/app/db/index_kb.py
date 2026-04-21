from pathlib import Path

from app.config import settings
from app.db.mongo import get_db
from app.services.analyze_service import embed_text


def load_kb_files():
    kb_dir = Path(settings.RAG_KNOWLEDGE_DIR)
    docs = []

    for file_path in kb_dir.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8").strip()
        if not content:
            continue

        docs.append({
            "title": file_path.stem,
            "source": file_path.name,
            "content": content,
        })

    return docs


def main():
    db = get_db()
    docs = load_kb_files()

    if not docs:
        print("No knowledge-base files found.")
        return

    for doc in docs:
        existing = db.knowledge_base.find_one({"source": doc["source"]})
        if existing:
            print(f"Skipping existing doc: {doc['source']}")
            continue

        embedding = embed_text(doc["content"])
        if not embedding:
            print(f"Failed to embed: {doc['source']}")
            continue

        db.knowledge_base.insert_one({
            "title": doc["title"],
            "source": doc["source"],
            "content": doc["content"],
            "embedding": embedding,
        })

        print(f"Indexed: {doc['source']}")

    print("Knowledge base indexing complete.")


if __name__ == "__main__":
    main()