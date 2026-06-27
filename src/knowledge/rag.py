"""
WasteRAG — offline retrieval-augmented knowledge for CleanBot.

Flow:
  1. YOLO detects a waste item → Detection(class_name, confidence, bbox)
  2. WasteRAG.enrich(detection) → disposal action, bin type, hazard level, passage
  3. Navigation/dashboard layer uses enrichment for routing and logging

The index is built once by training/build_rag_index.py and then loaded at
runtime. All inference runs locally — no network required on Jetson Nano.

Optional: set ANTHROPIC_API_KEY in environment to enable natural language
responses via the Claude API (used by the dashboard, not the robot).
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


INDEX_DIR = Path(__file__).resolve().parents[3] / "data" / "rag_index"

# Action labels embedded in knowledge documents
_ACTION_RE = re.compile(
    r"CleanBot action:\s*(collect_recyclable|collect_compost|collect_landfill"
    r"|collect_hazardous|flag_for_pickup)",
    re.IGNORECASE,
)
_BIN_RE = re.compile(r"Bin:\s*(blue|green|black|red)", re.IGNORECASE)
_PRIORITY_RE = re.compile(r"Priority:\s*(high|medium|low|critical)", re.IGNORECASE)
_HAZARD_RE = re.compile(r"Hazard(?:[^:]*)?:\s*(low|medium|high|critical)", re.IGNORECASE)


@dataclass
class Enrichment:
    class_name: str
    action: str          # collect_recyclable | collect_compost | collect_landfill | collect_hazardous | flag_for_pickup
    bin_color: str       # blue | green | black | red | unknown
    priority: str        # high | medium | low | critical
    hazard: str          # low | medium | high | critical
    passage: str         # top retrieved passage (human-readable context)
    score: float         # retrieval similarity score 0–1


class WasteRAG:
    def __init__(
        self,
        index_dir: Path | str = INDEX_DIR,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        import faiss
        from sentence_transformers import SentenceTransformer

        index_dir = Path(index_dir)
        index_path = index_dir / "index.faiss"
        chunks_path = index_dir / "chunks.json"

        if not index_path.exists():
            raise FileNotFoundError(
                f"RAG index not found at {index_path}\n"
                "Run: python training/build_rag_index.py"
            )

        self.embedder = SentenceTransformer(model_name)
        self.index = faiss.read_index(str(index_path))
        self.chunks: list[dict] = json.loads(chunks_path.read_text())

    def query(self, text: str, top_k: int = 3) -> list[dict]:
        """Return top_k most relevant chunks for the query text."""
        vec = self.embedder.encode([text], normalize_embeddings=True).astype(np.float32)
        scores, ids = self.index.search(vec, top_k)
        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            chunk = dict(self.chunks[idx])
            chunk["score"] = float(score)
            results.append(chunk)
        return results

    def enrich(self, class_name: str, confidence: float = 1.0, context: str = "") -> Enrichment:
        """
        Enrich a detected waste class with disposal guidance.

        Args:
            class_name: one of plastic | metal | paper | bio_waste
            confidence: detector confidence (0–1)
            context: optional extra context (e.g. "near storm drain", "appears to be a syringe")
        """
        query = f"{class_name} waste disposal handling bin action {context}".strip()
        results = self.query(query, top_k=5)

        # Aggregate actions across top passages — majority vote
        actions, bins, priorities, hazards = [], [], [], []
        for r in results:
            text = r["text"]
            m = _ACTION_RE.search(text)
            if m:
                actions.append(m.group(1).lower())
            m = _BIN_RE.search(text)
            if m:
                bins.append(m.group(1).lower())
            m = _PRIORITY_RE.search(text)
            if m:
                priorities.append(m.group(1).lower())
            m = _HAZARD_RE.search(text)
            if m:
                hazards.append(m.group(1).lower())

        def majority(lst: list[str], default: str) -> str:
            if not lst:
                return default
            return max(set(lst), key=lst.count)

        top_passage = results[0]["text"] if results else ""
        top_score = results[0]["score"] if results else 0.0

        # If confidence is below 0.5, override to flag_for_pickup
        if confidence < 0.5:
            return Enrichment(
                class_name=class_name,
                action="flag_for_pickup",
                bin_color="unknown",
                priority="low",
                hazard="low",
                passage="Detection confidence below threshold — flagging for human review.",
                score=top_score,
            )

        return Enrichment(
            class_name=class_name,
            action=majority(actions, "collect_landfill"),
            bin_color=majority(bins, "black"),
            priority=majority(priorities, "medium"),
            hazard=majority(hazards, "low"),
            passage=top_passage,
            score=top_score,
        )

    def answer(self, question: str, use_claude: bool = True) -> str:
        """
        Answer a natural language question about waste disposal.
        Used by the dashboard. Falls back to raw passage if no API key.
        """
        passages = self.query(question, top_k=4)
        context = "\n\n".join(f"[{i+1}] {p['text']}" for i, p in enumerate(passages))

        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key or not use_claude:
            # Return the top passage directly
            return passages[0]["text"] if passages else "No relevant information found."

        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            system=(
                "You are CleanBot's waste disposal advisor. "
                "Answer the user's question using only the provided context. "
                "Be concise and specific. If the context does not cover the question, say so."
            ),
            messages=[{
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}",
            }],
        )
        return response.content[0].text
