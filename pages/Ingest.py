"""Ingest page — upload PDFs, chunk, embed, and build the persistent index."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.embeddings import embed_documents  # noqa: E402
from src.ingest import chunk_pages, extract_pages, file_hash  # noqa: E402
from src.ui import card, load_css, metric_tile, section_header  # noqa: E402
from src.vectorstore import add_chunks, ingested_hashes, reset_collection, stats  # noqa: E402

st.set_page_config(page_title="Ingest · Talent Sphere Elevate", page_icon="📥", layout="wide")

load_css()

section_header(
    "📥 Ingest Documents",
    "Upload training PDFs and build the searchable vector index.",
)

# --- Uploader --------------------------------------------------------------
uploaded = st.file_uploader(
    "Drop PDF files here",
    type=["pdf"],
    accept_multiple_files=True,
    help="Upload one or more training PDFs. Re-uploading the same file is de-duplicated.",
)

build = st.button("🔧 Build Index", disabled=not uploaded, use_container_width=False)

if build and uploaded:
    known_hashes = ingested_hashes()
    files_processed = 0
    chunks_added = 0
    duplicates = 0

    progress = st.progress(0.0, text="Starting…")
    total = len(uploaded)

    for i, file in enumerate(uploaded, start=1):
        label = f"Processing {file.name} ({i}/{total})"
        progress.progress((i - 1) / total, text=label)

        try:
            data = file.getvalue()
            digest = file_hash(data)

            if digest in known_hashes:
                duplicates += 1
                st.info(f"⏭️ **{file.name}** is already indexed — skipped (duplicate).")
                progress.progress(i / total, text=label)
                continue

            pages = extract_pages(file)
            if not pages:
                st.warning(f"⚠️ No extractable text found in **{file.name}** — skipped.")
                progress.progress(i / total, text=label)
                continue

            chunks = chunk_pages(pages, file.name)
            embeddings = embed_documents([c["text"] for c in chunks])
            added = add_chunks(chunks, embeddings, digest)

            known_hashes.add(digest)
            files_processed += 1
            chunks_added += added
            st.success(f"✅ **{file.name}** — {added} chunks from {len(pages)} pages.")

        except Exception as exc:  # noqa: BLE001 - never dump a raw traceback
            st.error(f"❌ Failed to process **{file.name}**: {exc}")

        progress.progress(i / total, text=label)

    progress.progress(1.0, text="Done")

    st.write("")
    card(
        "Ingestion summary",
        f"Files processed: <b>{files_processed}</b> &nbsp;·&nbsp; "
        f"Chunks added: <b>{chunks_added}</b> &nbsp;·&nbsp; "
        f"Duplicates skipped: <b>{duplicates}</b>",
        icon="📦",
    )

st.write("")

# --- Current index stats ---------------------------------------------------
section_header("Current index")

index = stats()
col1, col2 = st.columns(2)
with col1:
    metric_tile("Documents Ingested", index["sources"])
with col2:
    metric_tile("Total Chunks", index["total_chunks"])

if index["source_names"]:
    st.caption("Indexed sources: " + ", ".join(index["source_names"]))

st.write("")

# --- Reset index (destructive) --------------------------------------------
section_header("Danger zone", "Clear all ingested data from the index.")

if "confirm_reset" not in st.session_state:
    st.session_state.confirm_reset = False

st.markdown('<div class="ts-danger">', unsafe_allow_html=True)
if not st.session_state.confirm_reset:
    if st.button("🗑️ Reset index", type="secondary"):
        st.session_state.confirm_reset = True
        st.rerun()
else:
    st.warning("This will permanently delete every chunk from the index. Are you sure?")
    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("Yes, delete everything", type="secondary"):
            reset_collection()
            st.session_state.confirm_reset = False
            st.success("Index cleared.")
            st.rerun()
    with c2:
        if st.button("Cancel", type="secondary"):
            st.session_state.confirm_reset = False
            st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# --- Sidebar ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🚀 Talent Sphere Elevate")
    st.caption("Milestone 1 — Retrieval foundation")
    st.divider()
    st.caption(f"Indexed sources: **{index['sources']}**")
    st.caption(f"Indexed chunks: **{index['total_chunks']}**")