
import logging
from typing import List
import chromadb

from src.models import ChatMessage

logger = logging.getLogger(__name__)

class ChatMessageVectorRepository:
    def __init__(self,collection_name="chat_history"):
        # self.client = chromadb.Client()
        self.client = chromadb.PersistentClient('../data/chat_history_db')
        self.collection = self.client.get_or_create_collection(name=collection_name)
    def get_messages(self, query:str,result_count:int=10, threshold=0.5)->List[str]:
        result = self.collection.query(
            query_texts=[query],
            n_results=result_count,
            include= ['metadatas','distances']
        )

        user_ids = set()
        for idx, metadata in enumerate(result.get('metadatas',{})[0]):
            # distance = result.get('distances')[0][idx]
            # if distance<=threshold:
            user_ids.add(metadata.get('user_id',''))
            
        return user_ids
        
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