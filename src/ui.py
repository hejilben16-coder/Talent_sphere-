"""UI helpers: CSS injection and reusable styled HTML components.

This is the only module in ``src/`` allowed to call Streamlit. It keeps the
LinkedIn-themed enterprise look consistent across every page.
"""

from __future__ import annotations

import html
from functools import lru_cache
from pathlib import Path

import streamlit as st

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
_CSS_PATH = _ASSETS_DIR / "styles.css"


@lru_cache(maxsize=1)
def _read_css() -> str:
    try:
        return _CSS_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""


def load_css() -> None:
    """Inject the custom LinkedIn-theme stylesheet. Call at the top of every page."""
    css = _read_css()
    if css:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def hero(title: str, subtitle: str) -> None:
    """Render the gradient hero header."""
    st.markdown(
        f"""
        <div class="ts-hero">
            <div class="ts-hero-title">{html.escape(title)}</div>
            <div class="ts-hero-subtitle">{html.escape(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str | None = None) -> None:
    """Render a gradient-accented section header."""
    sub = f'<div class="ts-section-subtitle">{html.escape(subtitle)}</div>' if subtitle else ""
    st.markdown(
        f"""
        <div class="ts-section">
            <div class="ts-section-title">{html.escape(title)}</div>
            {sub}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, icon: str = "") -> None:
    """Render a white surface card with an optional icon + title and HTML body."""
    icon_html = f'<span class="ts-card-icon">{html.escape(icon)}</span>' if icon else ""
    title_html = (
        f'<div class="ts-card-title">{icon_html}{html.escape(title)}</div>' if title else ""
    )
    st.markdown(
        f"""
        <div class="ts-card">
            {title_html}
            <div class="ts-card-body">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_tile(label: str, value: str) -> None:
    """Render a metric tile with a left accent bar, big value, and small label."""
    st.markdown(
        f"""
        <div class="ts-metric">
            <div class="ts-metric-value">{html.escape(str(value))}</div>
            <div class="ts-metric-label">{html.escape(str(label))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_badge(score: float) -> str:
    """Return HTML for a similarity pill, color-scaled by score.

    High (>=0.75) green, mid (0.5-0.75) blue, low (<0.5) gray.
    """
    if score >= 0.75:
        cls = "ts-badge-high"
    elif score >= 0.5:
        cls = "ts-badge-mid"
    else:
        cls = "ts-badge-low"
    return f'<span class="ts-badge {cls}">{score:.3f}</span>'


def result_card(source: str, page, score: float, text: str) -> None:
    """Render a single search result as a card with a source/page/score header."""
    st.markdown(
        f"""
        <div class="ts-card ts-result">
            <div class="ts-result-head">
                <span class="ts-result-source">📄 {html.escape(str(source))}</span>
                <span class="ts-result-page">Page {html.escape(str(page))}</span>
                {score_badge(score)}
            </div>
            <div class="ts-result-text">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str, icon: str = "🗂️") -> None:
    """Render a friendly empty-state card."""
    st.markdown(
        f"""
        <div class="ts-card ts-empty">
            <div class="ts-empty-icon">{html.escape(icon)}</div>
            <div class="ts-empty-title">{html.escape(title)}</div>
            <div class="ts-empty-body">{html.escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )