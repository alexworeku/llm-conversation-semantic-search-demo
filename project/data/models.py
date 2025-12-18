import datetime
from typing import List


class RawChatMessage:
    def __init__(self, user_id:str,chat_id:str, message_text:str, timestamp:datetime, metadata:dict):
        self.user_id = user_id
        self.chat_id = chat_id
        self.message_text = message_text
        self.timestamp = timestamp
        self.metadata = metadata
        
class ProcessedRecord:
    def __init__(self,record_id:str, sanitized_text:str, embedding_vector:List[float],topics: List[str], original_timestamp:datetime):
        self.record_id = record_id
        self.sanitized_text = sanitized_text
        self.embedding_vector = embedding_vector
        self.topics =topics
        self.original_timestamp=original_timestamp
        