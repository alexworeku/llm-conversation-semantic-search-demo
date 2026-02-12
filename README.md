# LLM Conversation Semantic Search Demo

A Streamlit proof of concept that shows how LLM conversation data can be transformed into privacy-aware intent signals for semantic search and monetization workflows.

## What This Project Does
- Ingests conversation history from `data/chats.json`
- Detects and anonymizes sensitive entities (PII) using Presidio
- Stores anonymized message embeddings in ChromaDB
- Runs semantic search to find users/messages matching an intent query

## Why This Matters
This demo illustrates how conversational data can be operationalized for:
- Intent-based user segmentation
- Campaign targeting and growth experiments
- Product analytics and behavior insights
- Retrieval workflows over large chat histories

## Tech Stack
- `Streamlit` for UI
- `ChromaDB` for vector storage and similarity search
- `Presidio Analyzer + Presidio Anonymizer` for PII handling
- `ijson` for streaming large JSON ingestion
- `Pydantic` for message modeling

## End-to-End Flow
1. Source chat export is read from `data/chats.json`
2. Conversations are flattened into message-level records
3. Message text is anonymized
4. Messages + metadata are upserted into ChromaDB (`data/chat_history_db`)
5. User enters an intent query in the UI
6. Top semantic matches are returned with metadata and distance scores

## Project Structure
```text
.
├── streamlit_app.py        # Demo UI
├── src/
│   ├── extractors.py       # Ingestion pipeline (stream + batch upsert)
│   ├── transformers.py     # Flatten + anonymize conversation text
│   ├── loaders.py          # Chroma repository (upsert + search)
│   └── models.py           # Pydantic models
├── data/
│   ├── chats.json          # Source dataset used by demo
│   └── chat_history_db/    # Persistent Chroma vector store
└── requirements.txt
```

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
streamlit run streamlit_app.py
```

## How To Use The Demo
1. Open the app and go to **Step 1: Ingest Data**
2. (Optional) expand the source file preview
3. Click **Ingest / Re-ingest**
4. Go to **Step 2: Semantic Search**
5. Pick a preset or enter a custom query
6. Tune `Top-K` / `Max distance` and run **Search**

## Notes
- Search is enabled only after ingestion in the current session.
- ChromaDB is persistent, so indexed data remains in `data/chat_history_db`.
- Profile image (optional) is auto-detected from `data/profile.*` or project root `profile.*`.

## Example Queries
- `Users asking for financial investment advice`
- `Users looking for medical or pregnancy advice`
- `Users comparing products before purchase`

---
If you want to extend this project, next natural steps are cloud deployment, API integration, and production observability.
