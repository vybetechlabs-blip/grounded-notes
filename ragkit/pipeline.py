"""The end-to-end question-answering pipeline.

One object wires the pieces: retrieve → grounding check → (answer | refuse).
Both the CLI and the Streamlit app call this and nothing lower-level.
"""

from pydantic import BaseModel

from ragkit.config import Settings, get_settings
from ragkit.embed.local import SentenceTransformersEmbedder
from ragkit.generate.factory import make_provider
from ragkit.grounding.citations import Citation, citations_from_results
from ragkit.grounding.guard import REFUSAL_TEXT, GroundingDecision, check_grounding
from ragkit.ingest.chunker import chunk_document
from ragkit.ingest.loader import load_corpus
from ragkit.retrieve.hybrid import HybridRetriever
from ragkit.retrieve.rerank import CrossEncoderReranker
from ragkit.store.chroma import ChromaStore


class Answer(BaseModel):
    """Everything a caller needs to render a response honestly."""

    question: str
    text: str
    grounded: bool
    citations: list[Citation]
    decision: GroundingDecision
    provider: str


class Pipeline:
    """Owns the store, embedder, retriever, and provider for one corpus."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.embedder = SentenceTransformersEmbedder(self.settings.embedding_model)
        self.store = ChromaStore(self.settings.data_dir, self.settings.collection_name)
        self.retriever = HybridRetriever(self.store, self.embedder)
        self.reranker = (
            CrossEncoderReranker(self.settings.rerank_model) if self.settings.rerank else None
        )
        self.provider = make_provider(self.settings, self.embedder)

    def ingest(self) -> tuple[int, int, int]:
        """Load, chunk, embed, and sync the corpus. Returns (docs, chunks, deleted)."""
        docs = load_corpus(self.settings.corpus_dir)
        chunks = [
            chunk
            for doc in docs
            for chunk in chunk_document(doc, self.settings.chunk_size, self.settings.chunk_overlap)
        ]
        embeddings = self.embedder.embed_texts([c.context_text for c in chunks])
        upserted, deleted = self.store.sync(chunks, embeddings)
        return len(docs), upserted, deleted

    def ask(self, question: str, top_k: int | None = None) -> Answer:
        """Answer a question with citations, or refuse when grounding fails."""
        k = top_k or self.settings.top_k
        if self.reranker is not None:
            candidates = self.retriever.retrieve(question, max(k, self.settings.rerank_candidates))
            results = self.reranker.rerank(question, candidates)[:k]
        else:
            results = self.retriever.retrieve(question, k)
        decision = check_grounding(
            results,
            score_threshold=self.settings.min_score,
            coverage=self.retriever.coverage(question, results),
            coverage_threshold=self.settings.min_coverage,
        )
        text = self.provider.answer(question, results) if decision.grounded else REFUSAL_TEXT
        return Answer(
            question=question,
            text=text,
            grounded=decision.grounded,
            citations=citations_from_results(results),
            decision=decision,
            provider=self.provider.name if decision.grounded else "refused",
        )
