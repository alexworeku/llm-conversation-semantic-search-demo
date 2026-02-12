import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import chromadb

from src.models import ChatMessage

logger = logging.getLogger(__name__)

class ChatMessageVectorRepository:
    def __init__(self, collection_name: str = "chat_history", persist_path: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent
        db_path = Path(persist_path) if persist_path else (base_dir / "data" / "chat_history_db")
        self.client = chromadb.PersistentClient(path=str(db_path))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def search_messages(
        self, query: str, result_count: int = 10, threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        result = self.collection.query(
            query_texts=[query],
            n_results=result_count,
            include=["documents", "metadatas", "distances"],
        )

        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        documents = result.get("documents", [[]])[0]

        rows: List[Dict[str, Any]] = []
        for idx, metadata in enumerate(metadatas):
            distance = distances[idx] if idx < len(distances) else None
            if threshold is not None and distance is not None and distance > threshold:
                continue

            rows.append(
                {
                    "user_id": metadata.get("user_id", ""),
                    "conversation_id": metadata.get("conversation_id", ""),
                    "user_email": metadata.get("user_email", ""),
                    "create_time": metadata.get("create_time", ""),
                    "distance": distance,
                    "message": documents[idx] if idx < len(documents) else "",
                }
            )

        return rows

    def get_messages(self, query: str, result_count: int = 10, threshold: float = 0.5) -> List[str]:
        rows = self.search_messages(query=query, result_count=result_count, threshold=threshold)
        user_ids = {row.get("user_id", "") for row in rows if row.get("user_id")}
        return sorted(user_ids)

    def upsert_messages(self,messages: List[ChatMessage])->bool:
        docs = []
        metadatas = []
        ids =[]
        try:
            for message in messages:
                docs.append(message.message_text)
                metadatas.append(message.metadata)
                ids.append(message.message_id)
            
            self.collection.upsert(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            logger.error("Couldn't upsert messages: %s", e)
            return False
