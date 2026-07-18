"""Talent Sphere Elevate — Home page and app entry point (Milestone 1).

Run with:  ``streamlit run app.py``

This page is intentionally thin: it renders the themed home dashboard and
delegates all real work to the ``src/`` package.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is importable when Streamlit runs this file directly.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.config import EMBEDDING_MODEL  # noqa: E402
from src.ui import card, hero, load_css, metric_tile, section_header  # noqa: E402
from src.vectorstore import stats  # noqa: E402

st.set_page_config(
    page_title="Talent Sphere Elevate",
    page_icon="🚀",
    layout="wide",
)

load_css()

hero(
    "Talent Sphere Elevate",
    "Milestone 1 · Document ingestion & semantic retrieval — no LLM yet, "
    "proving that search finds the right passages first.",
)

# --- Live index metrics ----------------------------------------------------
index = stats()

col1, col2, col3 = st.columns(3)
with col1:
    metric_tile("Documents Ingested", index["sources"])
with col2:
    metric_tile("Total Chunks", index["total_chunks"])
with col3:
    metric_tile("Embedding Model", EMBEDDING_MODEL.split("/")[-1])

st.write("")

# --- How it works ----------------------------------------------------------
section_header("How it works", "Three stages take a raw PDF to ranked, sourced answers.")

c1, c2, c3 = st.columns(3)
with c1:
    card(
        "1 · Ingest",
        "Upload training PDFs. Each page is extracted, cleaned, and split into "
        "overlapping chunks with source metadata.",
        icon="📥",
    )
with c2:
    card(
        "2 · Embed",
        "Chunks are encoded with <b>BAAI/bge-large-en-v1.5</b> into 1024-dim "
        "normalized vectors and stored persistently in ChromaDB.",
        icon="🧠",
    )
with c3:
    card(
        "3 · Search",
        "Your query is embedded and matched by cosine similarity, returning the "
        "top passages with source, page, and a similarity score.",
        icon="🔍",
    )

st.write("")

# --- Primary CTA -----------------------------------------------------------
section_header("Get started")

cta_col, _ = st.columns([1, 3])
with cta_col:
    if hasattr(st, "page_link"):
        st.page_link("pages/Ingest.py", label="Go to Ingest →", icon="📥")
    else:  # graceful fallback on older Streamlit
        st.info("Open the **Ingest** page from the sidebar to build your index.")

# --- Sidebar branding ------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚀 Talent Sphere Elevate")
    st.caption("Milestone 1 — Retrieval foundation")
    st.divider()
    st.caption(f"Indexed sources: **{index['sources']}**")
    st.caption(f"Indexed chunks: **{index['total_chunks']}**")