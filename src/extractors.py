import logging
from typing import Dict, List
import ijson
from src.loaders import ChatMessageVectorRepository
from src.models import ChatMessage
from src.transformers import flatten_and_anonymize_conversation_history

logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO
# )

BATCH_SIZE = 10
def ingest_data(json_file_path: str, batch_size: int = BATCH_SIZE) -> Dict[str, int]:
    messages_repo = ChatMessageVectorRepository()
    batch_messages: List[ChatMessage] = []
    stats = {
        "users_processed": 0,
        "conversations_processed": 0,
        "messages_transformed": 0,
        "messages_upserted": 0,
        "batch_size": batch_size,
    }

    try:
        with open(json_file_path, "rb") as f:
            for user in ijson.items(f, "item"):
                stats["users_processed"] += 1

                for conversation in user.get("conversations", []):
                    stats["conversations_processed"] += 1
                    messages = flatten_and_anonymize_conversation_history(
                        user.get("user_id", ""),
                        user.get("email", ""),
                        conversation,
                    )
                    stats["messages_transformed"] += len(messages)
                    batch_messages.extend(messages)

                    if len(batch_messages) >= batch_size:
                        result = messages_repo.upsert_messages(messages=batch_messages)
                        if not result:
                            raise RuntimeError("Failed to upsert a message batch.")
                        stats["messages_upserted"] += len(batch_messages)
                        batch_messages.clear()

        if batch_messages:
            result = messages_repo.upsert_messages(messages=batch_messages)
            if not result:
                raise RuntimeError("Failed to upsert the final message batch.")
            stats["messages_upserted"] += len(batch_messages)

        return stats
    except Exception as e:
        logger.error("Ingestion failed for %s: %s", json_file_path, e)
        raise
