"""
RAG Pipeline: Vector store creation and dual retriever implementation.
Handles both simulation retrieval and evaluation retrieval.
"""

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path

import numpy as np
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from knowledge_base.corpus import ALL_DOCUMENTS


CACHE_DIR = Path(".cache")
SIM_INDEX_PATH = CACHE_DIR / "sim_faiss_index"
EVAL_INDEX_PATH = CACHE_DIR / "eval_faiss_index"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


def get_embeddings() -> HuggingFaceEmbeddings:
    """Initialize embedding model."""
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_langchain_documents(raw_docs: List[Dict]) -> List[Document]:
    """Convert raw knowledge base dicts to LangChain Document objects."""
    documents = []
    for doc in raw_docs:
        lc_doc = Document(
            page_content=doc["content"].strip(),
            metadata={**doc["metadata"], "id": doc["id"], "title": doc["title"]},
        )
        documents.append(lc_doc)
    return documents


def build_vector_stores(force_rebuild: bool = False) -> tuple:
    """
    Build or load both simulation and evaluation FAISS vector stores.
    Returns (sim_store, eval_store).
    """
    CACHE_DIR.mkdir(exist_ok=True)
    embeddings = get_embeddings()
    all_docs = build_langchain_documents(ALL_DOCUMENTS)

    # Simulation store: all documents (grounds objection generation)
    if not force_rebuild and SIM_INDEX_PATH.exists():
        sim_store = FAISS.load_local(
            str(SIM_INDEX_PATH), embeddings, allow_dangerous_deserialization=True
        )
    else:
        sim_store = FAISS.from_documents(all_docs, embeddings)
        sim_store.save_local(str(SIM_INDEX_PATH))

    # Evaluation store: only transcripts and playbooks (comparison benchmarks)
    eval_doc_types = {"transcript", "playbook"}
    eval_docs = [d for d in all_docs if d.metadata.get("document_type") in eval_doc_types]

    if not force_rebuild and EVAL_INDEX_PATH.exists():
        eval_store = FAISS.load_local(
            str(EVAL_INDEX_PATH), embeddings, allow_dangerous_deserialization=True
        )
    else:
        eval_store = FAISS.from_documents(eval_docs, embeddings)
        eval_store.save_local(str(EVAL_INDEX_PATH))

    return sim_store, eval_store


class HybridRetriever:
    """
    Hybrid retriever: vector similarity search + metadata filtering.
    Used for both simulation and evaluation retrieval.
    """

    def __init__(self, vector_store: FAISS, top_k: int = 5):
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(
        self,
        query: str,
        metadata_filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None,
    ) -> List[Document]:
        """
        Retrieve documents using vector similarity, then apply metadata filters.
        Returns top_k most relevant documents after filtering.
        """
        k = top_k or self.top_k
        # Fetch more candidates to allow post-filter narrowing
        candidate_k = min(k * 4, 20)
        candidates = self.vector_store.similarity_search(query, k=candidate_k)

        if not metadata_filters:
            return candidates[:k]

        # Apply metadata filters
        filtered = []
        for doc in candidates:
            if self._matches_filters(doc.metadata, metadata_filters):
                filtered.append(doc)

        # If strict filtering returns too few results, relax to partial match
        if len(filtered) < 2:
            filtered = self._partial_match(candidates, metadata_filters, k)

        return filtered[:k]

    def _matches_filters(self, doc_meta: Dict, filters: Dict) -> bool:
        """Check if document metadata matches all filters."""
        for key, value in filters.items():
            doc_val = doc_meta.get(key)
            if doc_val is None:
                continue
            # "all" means no restriction on this field
            if doc_val == "all" or value == "all":
                continue
            if isinstance(value, list):
                if doc_val not in value:
                    return False
            else:
                if doc_val != value:
                    return False
        return True

    def _partial_match(
        self, candidates: List[Document], filters: Dict, k: int
    ) -> List[Document]:
        """Score documents by how many filters they match, return best matches."""
        scored = []
        for doc in candidates:
            score = 0
            for key, value in filters.items():
                doc_val = doc.metadata.get(key)
                if doc_val == "all" or value == "all":
                    score += 0.5
                elif doc_val == value:
                    score += 1
                elif isinstance(value, list) and doc_val in value:
                    score += 1
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:k]]

    def retrieve_sim_context(
        self,
        persona: str,
        industry: str,
        deal_size: str,
        stage: str,
        objection_focus: str,
    ) -> List[Document]:
        """
        Simulation-specific retrieval: persona objections, stage challenges,
        industry patterns, historical deal segments.
        """
        query = (
            f"{persona} objections {objection_focus} {industry} {stage} negotiation"
        )
        filters = {
            "persona": persona,
            "industry": [industry, "all"],
        }
        return self.retrieve(query, filters, top_k=4)

    def retrieve_eval_context(
        self,
        user_response: str,
        objection_type: str,
        persona: str,
    ) -> Dict[str, List[Document]]:
        """
        Evaluation-specific retrieval: winning patterns, losing patterns,
        strong rebuttals, competitive differentiation.
        """
        win_query = f"successful response {objection_type} {persona} winning rebuttal"
        win_filters = {
            "outcome": "won",
            "objection_type": [objection_type, "all"],
        }
        winning_docs = self.retrieve(win_query, win_filters, top_k=3)

        lose_query = f"failed response {objection_type} {persona} losing deal"
        lose_filters = {
            "outcome": "lost",
            "objection_type": [objection_type, "all"],
        }
        losing_docs = self.retrieve(lose_query, lose_filters, top_k=2)

        playbook_query = f"best practices {objection_type} objection handling"
        playbook_filters = {"document_type": "playbook", "objection_type": [objection_type, "all"]}
        playbook_docs = self.retrieve(playbook_query, playbook_filters, top_k=2)

        return {
            "winning_patterns": winning_docs,
            "losing_patterns": losing_docs,
            "playbook_guidance": playbook_docs,
        }


def format_retrieved_docs(docs: List[Document], max_chars: int = 2000) -> str:
    """Format retrieved documents into a concise context string."""
    if not docs:
        return "No relevant context found."
    parts = []
    total = 0
    for doc in docs:
        excerpt = doc.page_content[:500]
        entry = f"[{doc.metadata.get('title', 'Document')}]\n{excerpt}"
        if total + len(entry) > max_chars:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n---\n\n".join(parts)
