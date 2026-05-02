"""Embeddings service using fastembed (ONNX, no torch).
Lazy-load model on first use. Provides utility functions for jobs  profiles.
"""
from __future__ import annotations

import logging
import math
import threading
from typing import List, Optional, Sequence

import numpy as np

logger = logging.getLogger("talentiv.embed")

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model = None
_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                try:
                    from fastembed import TextEmbedding
                    logger.info("Loading embedding model %s...", _MODEL_NAME)
                    _model = TextEmbedding(_MODEL_NAME)
                    logger.info("Embedding model loaded.")
                except Exception as e:
                    logger.exception("Failed to load embedding model: %s", e)
                    raise
    return _model


def embed_texts(texts: Sequence[str]) -> List[List[float]]:
    if not texts:
        return []
    model = _get_model()
    vectors = list(model.embed(list(texts)))
    return [v.tolist() if hasattr(v, "tolist") else list(v) for v in vectors]


def embed_text(text: str) -> List[float]:
    vecs = embed_texts([text])
    return vecs[0] if vecs else []


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    av = np.asarray(a, dtype=np.float32)
    bv = np.asarray(b, dtype=np.float32)
    na = float(np.linalg.norm(av))
    nb = float(np.linalg.norm(bv))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(av, bv) / (na * nb))


def job_text(job: dict) -> str:
    """Concat relevant job fields into a single semantic text."""
    parts = [
        job.get("title") or "",
        job.get("description") or "",
        job.get("requirements") or "",
        " ".join(job.get("skills") or []),
        job.get("location") or "",
        job.get("experience_level") or "",
    ]
    return " | ".join(p for p in parts if p).strip()[:4000]


def profile_text(profile: dict) -> str:
    """Concat relevant profile fields into a single semantic text."""
    exp_blob = " ".join(
        f"{(e or {}).get('title','')} {(e or {}).get('company','')} {(e or {}).get('description','')}"
        for e in (profile.get("experience") or [])
    )
    parts = [
        profile.get("headline") or "",
        profile.get("summary") or "",
        " ".join(profile.get("skills") or []),
        exp_blob,
        profile.get("location") or "",
    ]
    return " | ".join(p for p in parts if p).strip()[:4000]


def query_text(q: Optional[str], location: Optional[str] = None) -> str:
    parts = [q or "", location or ""]
    return " | ".join(p for p in parts if p).strip()
