"""
MongoDB Atlas Vector Search Engine Simulator & Integration Adapter.
Provides high-performance cosine similarity k-NN vector matching against regulatory compliance mandates.
"""

import math
import hashlib
from typing import List, Dict, Any, Tuple


def generate_semantic_embedding(text: str, dimensions: int = 64) -> List[float]:
    """
    Generates a deterministic, normalized semantic embedding vector from text.
    In production Atlas, this is populated via OpenAI text-embedding-3-small or Gemini Embeddings.
    """
    cleaned = text.lower().strip()
    words = cleaned.split()
    vector = [0.0] * dimensions

    for idx, word in enumerate(words):
        # Hash each word into vector buckets with token weighting
        h = int(hashlib.sha256(word.encode("utf-8")).hexdigest(), 16)
        pos = h % dimensions
        weight = 1.0 / (1.0 + math.log(1 + idx))
        vector[pos] += weight

    # Normalize to unit length (L2 norm)
    magnitude = math.sqrt(sum(x * x for x in vector))
    if magnitude > 0.0:
        vector = [x / magnitude for x in vector]
    else:
        vector[0] = 1.0

    return vector


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes exact cosine similarity between two unit vectors."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    return max(0.0, min(1.0, dot_product))


class AtlasVectorIndex:
    """
    Simulates a MongoDB Atlas Vector Search Index configured with:
    - Path: "clause_embedding"
    - Similarity: "cosine"
    - NumDimensions: 64
    """

    def __init__(self):
        self.mandate_corpus = [
            {
                "rule_id": "GDPR-ART-28",
                "mandate": "GDPR Article 28: Data Processing Agreements",
                "required_terms": [
                    "processor shall only process personal data on documented instructions from controller",
                    "immediate breach notification within 72 hours without undue delay",
                    "deletion or return of personal data upon contract termination",
                ],
                "forbidden_terms": [
                    "unilateral retention of customer personal data after termination",
                    "waive data breach notification obligations",
                ],
            },
            {
                "rule_id": "HIPAA-164-312",
                "mandate": "HIPAA Security Rule §164.312 Technical Safeguards",
                "required_terms": [
                    "encryption of protected health information at rest and in transit using aes-256",
                    "automatic logoff and emergency access procedures",
                    "unique user identification and audit controls",
                ],
                "forbidden_terms": [
                    "unencrypted transmission of patient records",
                    "shared credentials without individual audit attribution",
                ],
            },
            {
                "rule_id": "SOC2-CC6",
                "mandate": "SOC 2 Trust Services Criteria CC6.1 Logical Access Controls",
                "required_terms": [
                    "multi-factor authentication enforced for all administrative and remote access",
                    "least-privilege role-based access control with quarterly entitlement reviews",
                ],
                "forbidden_terms": [
                    "single-factor password-only root or database administration access",
                ],
            },
            {
                "rule_id": "COMMERCIAL-INDEMNITY",
                "mandate": "Standard Commercial Indemnification & Liability Cap",
                "required_terms": [
                    "mutual indemnification for third-party intellectual property infringement",
                    "aggregate liability capped at twelve months fees paid under applicable order",
                ],
                "forbidden_terms": [
                    "uncapped consequential damages without liability limitation",
                    "unilateral customer assumption of all vendor platform negligence",
                ],
            },
        ]

        # Precompute vectors
        for item in self.mandate_corpus:
            combined = " ".join(item["required_terms"])
            item["vector"] = generate_semantic_embedding(combined)

    def search_nearest_mandate(
        self,
        query_text: str,
        k: int = 2,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Executes MongoDB Atlas Vector Search pipeline:
        [ { $vectorSearch: { index: "vector_index", path: "vector", queryVector: ..., limit: k } } ]
        """
        query_vector = generate_semantic_embedding(query_text)
        scores = []

        for mandate in self.mandate_corpus:
            sim = cosine_similarity(query_vector, mandate["vector"])
            scores.append((mandate, sim))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:k]
