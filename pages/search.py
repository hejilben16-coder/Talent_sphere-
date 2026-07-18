"""Search page — semantic retrieval over the ingested document index."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import TOP_K  # noqa: E402
from src.embeddings import embed_query  # noqa: E402
from src.ui import empty_state, load_css, result_card, section_header  # noqa: E402
from src.vectorstore import search, stats  # noqa: E402

st.set_page_config(page_title="Search · Talent Sphere Elevate", page_icon="🔍", layout="wide")

load_css()

section_header(
    "🔍 Semantic Search",
    "Ask in natural language — retrieval returns the most relevant source passages.",
)

index = stats()

if index["total_chunks"] == 0:
    empty_state(
        "Your index is empty",
        "Head to the Ingest page to upload PDFs and build the index before searching.",
        icon="🗂️",
    )
    if hasattr(st, "page_link"):
        st.page_link("pages/Ingest.py", label="Go to Ingest →", icon="📥")
    else:
        st.info("Open the **Ingest** page from the sidebar to build your index.")
else:
    query = st.text_input(
        "Search query",
        placeholder="e.g. What is the company's onboarding process?",
    )
    top_k = st.slider("Results to return (Top-K)", min_value=1, max_value=15, value=TOP_K)

    if st.button("🔍 Search", disabled=not query.strip()):
        try:
            with st.spinner("Searching…"):
                query_vec = embed_query(query.strip())
                results = search(query_vec, top_k)
        except Exception as exc:  # noqa: BLE001 - friendly error, no raw traceback
            st.error(f"❌ Search failed: {exc}")
            results = []

        if not results:
            st.warning("No matching passages found. Try rephrasing your query.")
        else:
            st.caption(f"Showing top {len(results)} passages.")
            for hit in results:
                result_card(hit["source"], hit["page"], hit["score"], hit["text"])

# --- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚀 Talent Sphere Elevate")
    st.caption("Milestone 1 — Retrieval foundation")
    st.divider()
    st.caption(f"Indexed sources: **{index['sources']}**")
    st.caption(f"Indexed chunks: **{index['total_chunks']}**")