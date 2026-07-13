"""Streamlit chat UI over the ragkit pipeline.

Runs keyless by default (local embeddings + extractive answers). If an
ANTHROPIC_API_KEY or OPENAI_API_KEY is present, generation upgrades
automatically. This file is also the Hugging Face Spaces entrypoint.
"""

import streamlit as st

from ragkit.pipeline import Answer, Pipeline

st.set_page_config(page_title="grounded-notes", page_icon=":books:", layout="centered")


@st.cache_resource(show_spinner="Loading models and index (first run takes a minute)...")
def get_pipeline() -> Pipeline:
    """Build the pipeline once per process; ingest if the index is empty."""
    pipeline = Pipeline()
    if pipeline.store.count() == 0:
        pipeline.ingest()
    return pipeline


pipeline = get_pipeline()

with st.sidebar:
    st.title("grounded-notes")
    st.markdown(
        "A grounded RAG assistant over a **fictional consultancy knowledge "
        "base** (Lanternfish Consulting). Every answer cites its sources; "
        "questions the corpus can't answer are refused, not invented."
    )
    st.divider()
    st.markdown(
        f"**Provider:** `{pipeline.provider.name}`  \n"
        f"**Chunks indexed:** {pipeline.store.count()}  \n"
        f"**Retrieval:** hybrid (BM25 + vectors)"
    )
    if pipeline.provider.name == "extractive":
        st.caption(
            "Running keyless: answers are extracted quotes. Set "
            "ANTHROPIC_API_KEY or OPENAI_API_KEY (with `uv sync --extra "
            "cloud`) for fluent LLM answers."
        )
    st.divider()
    st.markdown(
        "**Try asking:**\n"
        "- How much does an Automation Sprint cost?\n"
        "- What went wrong on the Granite Peak project?\n"
        "- Who can declare a major incident?\n"
        "- What is the empty-chair test?\n"
        "- *What's Lanternfish's phone number?* (refused)"
    )

if "history" not in st.session_state:
    st.session_state.history = []


def render_answer(answer: Answer) -> None:
    """Render an answer with its grounding status and citations."""
    st.markdown(answer.text)
    if answer.grounded:
        st.caption(f"answered by `{answer.provider}` · {answer.decision.reason}")
    else:
        st.caption(f"refused by the grounding guard · {answer.decision.reason}")
    with st.expander("Sources" if answer.grounded else "Closest documents (not sufficient)"):
        for citation in answer.citations:
            st.markdown(f"`[{citation.number}]` **{citation.source}** — {citation.heading}")


for question, answer in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        render_answer(answer)

if question := st.chat_input("Ask about Lanternfish Consulting..."):
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Retrieving..."):
            answer = pipeline.ask(question)
        render_answer(answer)
    st.session_state.history.append((question, answer))
