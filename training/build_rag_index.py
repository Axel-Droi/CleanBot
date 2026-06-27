#!/usr/bin/env python3
"""
Build the FAISS vector index from the CleanBot waste knowledge base.

Run once before deploying or after updating documents in src/knowledge/documents/.

Output:
  data/rag_index/index.faiss   — FAISS flat inner-product index
  data/rag_index/chunks.json   — text chunks + source metadata

Usage:
  python training/build_rag_index.py
  python training/build_rag_index.py --model all-MiniLM-L6-v2  # default
  python training/build_rag_index.py --model all-mpnet-base-v2  # higher quality, slower
"""
import argparse
import json
from pathlib import Path

import numpy as np

DOCS_DIR  = Path(__file__).resolve().parents[1] / "src" / "knowledge" / "documents"
INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "rag_index"


def load_chunks(docs_dir: Path) -> list[dict]:
    """
    Load all .md files and split into paragraph-level chunks.
    Each chunk carries its source filename for debugging.
    """
    chunks = []
    for doc_path in sorted(docs_dir.glob("*.md")):
        source = doc_path.stem
        text = doc_path.read_text(encoding="utf-8")

        # Split on double newlines, skip empty paragraphs and headings
        paragraphs = [p.strip() for p in text.split("\n\n")]
        for para in paragraphs:
            # skip section headings and very short lines
            if para.startswith("#") or len(para) < 40:
                continue
            chunks.append({"text": para, "source": source})

    return chunks


def build_index(chunks: list[dict], model_name: str) -> None:
    try:
        import faiss
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        raise ImportError(
            f"Missing dependency: {e}\n"
            "Install with: pip install faiss-cpu sentence-transformers"
        ) from e

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading embedding model: {model_name}")
    embedder = SentenceTransformer(model_name)

    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = embedder.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
        batch_size=32,
    ).astype(np.float32)

    dim = embeddings.shape[1]
    # IndexFlatIP = exact inner-product search (cosine similarity with normalized vectors)
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))
    (INDEX_DIR / "chunks.json").write_text(json.dumps(chunks, indent=2, ensure_ascii=False))

    print(f"\nIndex built: {len(chunks)} chunks, dim={dim}")
    print(f"Saved to: {INDEX_DIR}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="all-MiniLM-L6-v2",
                        help="Sentence-transformers model name")
    args = parser.parse_args()

    if not DOCS_DIR.exists():
        raise FileNotFoundError(f"Documents directory not found: {DOCS_DIR}")

    chunks = load_chunks(DOCS_DIR)
    print(f"Loaded {len(chunks)} chunks from {DOCS_DIR}")
    for doc in sorted(set(c["source"] for c in chunks)):
        n = sum(1 for c in chunks if c["source"] == doc)
        print(f"  {doc}: {n} chunks")

    build_index(chunks, args.model)


if __name__ == "__main__":
    main()
