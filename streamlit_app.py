from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from src.extractors import ingest_data
from src.loaders import ChatMessageVectorRepository

PROFILE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


st.set_page_config(
    page_title="LLM Conversation Semantic Search Demo",
    layout="wide",
)

st.markdown(
    """
<style>
.step-card {
  border: 1px solid #d6dbe1;
  border-radius: 10px;
  padding: 14px 14px 8px 14px;
  background: #fbfcfe;
}
.step-head {
  font-size: 1.05rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
}
.step-sub {
  color: #4a5568;
  font-size: 0.92rem;
  margin-bottom: 0.8rem;
}
.about-card {
  background: #252734;
  border-radius: 6px;
  padding: 20px;
  color: #f3f4f6;
}
.about-title {
  font-size: 1.6rem;
  font-weight: 700;
  margin-bottom: 0.7rem;
}
.about-text {
  font-size: 1.15rem;
  font-weight: 500;
  line-height: 1.3;
  margin-bottom: 1rem;
}
.about-link {
  display: inline-block;
  background: #0c7dbc;
  color: #ffffff !important;
  text-decoration: none;
  font-weight: 800;
  letter-spacing: 0.18em;
  font-size: 0.9rem;
  padding: 0.65rem 1.2rem;
}
.social-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}
.social-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  color: #ffffff !important;
  text-decoration: none;
  font-weight: 700;
  font-size: 0.78rem;
  letter-spacing: 0.06em;
  padding: 0.58rem 0.28rem;
  border-radius: 4px;
}
.social-icon {
  width: 12px;
  height: 12px;
  display: inline-block;
  flex-shrink: 0;
}
.linkedin-link {
  background: #0a66c2;
}
.github-link {
  background: #111111;
}
</style>
""",
    unsafe_allow_html=True,
)

st.title("LLM Conversation Semantic Search Demo")
st.caption(
    "A proof of concept for semantic search and monetization intelligence: transform LLM conversations into privacy-aware intent signals."
)

if "ingestion_completed" not in st.session_state:
    st.session_state.ingestion_completed = False
if "ingestion_stats" not in st.session_state:
    st.session_state.ingestion_stats = None

def _read_preview(file_path: str, max_chars: int = 6000) -> str:
    text = Path(file_path).read_text(encoding="utf-8")
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}\n\n... [truncated for preview]"


def _get_collection_size() -> int:
    try:
        return ChatMessageVectorRepository().collection.count()
    except Exception:
        return 0


def _find_profile_image() -> Path | None:
    for directory in (Path("data"), Path(".")):
        if not directory.exists():
            continue
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.stem.lower() == "profile" and path.suffix.lower() in PROFILE_IMAGE_EXTENSIONS:
                return path
    return None


with st.sidebar:
    st.subheader("Libraries & Tools Used")
    st.markdown("- `Streamlit`")
    st.markdown("- `ChromaDB`")
    st.markdown("- `Presidio Analyzer`")
    st.markdown("- `Presidio Anonymizer`")
    st.markdown("- `ijson`")
    st.markdown("- `Pydantic`")

left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-head">Step 1: Ingest Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-sub">Choose a source file and load anonymized vectors into ChromaDB.</div>',
        unsafe_allow_html=True,
    )
    local_path = "data/chats.json"
    st.write("Source Json file")

    with st.expander(local_path, expanded=False):
        try:
            st.code(_read_preview(local_path), language="json", height=400)
        except Exception as exc:
            st.error(f"Unable to preview file: {exc}")

    st.caption("Expand the file path above to preview the source JSON used for ingestion.")
    batch_size = st.slider(
        "Batch size",
        min_value=5,
        max_value=100,
        value=10,
        step=5,
        help="Number of transformed messages upserted to ChromaDB per write operation.",
    )

    if st.button("Ingest / Re-ingest", type="primary"):
        try:
            with st.spinner("Ingesting conversations into vector DB..."):
                stats = ingest_data(local_path, batch_size=batch_size)
            st.success("Ingestion completed")
            st.caption("Next step: go to Step 2, choose a query preset, and click `Search`.")
            st.json(stats)
            st.session_state.ingestion_completed = True
            st.session_state.ingestion_stats = stats
        except Exception as exc:
            st.error(f"Ingestion failed: {exc}")
            st.session_state.ingestion_completed = False
            st.session_state.ingestion_stats = None
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-head">Step 2: Semantic Search</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="step-sub">Run intent-based search over ingested conversations.</div>',
        unsafe_allow_html=True,
    )
    query_presets = {
        "Financial intent": "Users asking for financial investment advice",
        "Health intent": "Users looking for medical or pregnancy advice",
        "Shopping intent": "Users comparing products before purchase",
        "Custom": "",
    }
    selected_preset = st.selectbox(
        "Query preset",
        options=list(query_presets.keys()),
        help="Quick-start semantic intents. Choose Custom to write your own search intent.",
    )
    default_query = query_presets[selected_preset]
    query_text = st.text_area(
        "Query",
        value=default_query,
        height=100,
        placeholder="Describe the user intent",
        help="Natural-language intent used to retrieve semantically similar chat messages.",
    )

    controls_col1, controls_col2 = st.columns(2)
    with controls_col1:
        result_count = st.slider(
            "Top-K results",
            min_value=1,
            max_value=20,
            value=5,
            help="Maximum number of nearest semantic matches to return.",
        )
    with controls_col2:
        threshold = st.slider(
            "Max distance",
            min_value=0.0,
            max_value=3.0,
            value=1.8,
            step=0.1,
            help="Only used when threshold filtering is enabled. Lower values are stricter.",
        )
    use_threshold = st.checkbox(
        "Apply distance threshold",
        help=(
            "Distance measures semantic difference between your query and matched messages. "
            "Lower distance means better match. Enable this to keep only results with "
            "distance less than or equal to Max distance."
        ),
    )

    if not st.session_state.ingestion_completed:
        st.info("Ingest data first to enable search for this demo session.")
    else:
        collection_size = _get_collection_size()
        st.caption(f"Indexed messages available: {collection_size:,}")
        if st.session_state.ingestion_stats:
            st.caption(
                f"Last run: {st.session_state.ingestion_stats['messages_upserted']:,} messages "
                f"from {st.session_state.ingestion_stats['conversations_processed']:,} conversations."
            )

    if st.button(
        "Search",
        disabled=not st.session_state.ingestion_completed,
        help="Run semantic retrieval on the ingested vector index.",
    ):
        try:
            repo = ChatMessageVectorRepository()
            effective_threshold = threshold if use_threshold else None
            rows = repo.search_messages(
                query=query_text,
                result_count=result_count,
                threshold=effective_threshold,
            )

            if not rows:
                st.warning("No matches found for this query.")
            else:
                user_ids = sorted({row["user_id"] for row in rows if row.get("user_id")})
                st.success(f"Matched {len(rows)} messages across {len(user_ids)} user(s)")
                st.dataframe(rows, use_container_width=True)

                with st.expander("Unique user IDs"):
                    st.write(user_ids)
        except Exception as exc:
            st.error(f"Search failed: {exc}")
    st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.divider()
    profile_path = _find_profile_image()
    about_html = """
<div class="about-card">
  <div class="about-title">About</div>
"""
    if profile_path:
        image_bytes = profile_path.read_bytes()
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_suffix = profile_path.suffix.lower()
        mime_subtype = "jpeg" if image_suffix in {".jpg", ".jpeg"} else image_suffix.lstrip(".")
        about_html += f"""
  <div style="display:flex;justify-content:flex-start;margin-top:6px;margin-bottom:10px;">
    <img src="data:image/{mime_subtype};base64,{image_b64}"
         style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid #3f4759;" />
  </div>
"""
    about_html += """
  <div class="about-text">Made with ❤️ by Alex Ababu</div>
</div>
"""
    st.markdown(about_html, unsafe_allow_html=True)
    st.markdown(
        """
<div class="social-row">
  <a class="social-link linkedin-link" href="https://www.linkedin.com/in/alex-ababu/" target="_blank">
    <svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="white" d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zM7.119 20.452H3.555V9h3.564v11.452z"/>
    </svg>
    <span>LINKEDIN</span>
  </a>
  <a class="social-link github-link" href="https://github.com/alexworeku" target="_blank">
    <svg class="social-icon" viewBox="0 0 24 24" aria-hidden="true">
      <path fill="white" d="M12 0C5.37 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577 0-.285-.011-1.04-.016-2.041-3.338.724-4.042-1.61-4.042-1.61-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.236 1.839 1.236 1.07 1.834 2.807 1.304 3.492.997.108-.776.418-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.519 11.519 0 0 1 12 6.844c1.018.005 2.045.138 3.003.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.91 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222 0 1.606-.014 2.898-.014 3.293 0 .319.192.694.801.576C20.565 21.796 24 17.299 24 12c0-6.627-5.373-12-12-12z"/>
    </svg>
    <span>GITHUB</span>
  </a>
</div>
""",
        unsafe_allow_html=True,
    )
