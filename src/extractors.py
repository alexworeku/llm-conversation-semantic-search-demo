import logging
from typing import List
import ijson
from src.loaders import ChatMessageVectorRepository
from src.models import ChatMessage
from src.transformers import flatten_and_anonymize_conversation_history

logger = logging.getLogger(__name__)
# logging.basicConfig(
#     level=logging.INFO
# )

BATCH_SIZE = 10
def ingest_data(json_file_path):
    try:
        
        messages_repo = ChatMessageVectorRepository()
        
        with open("data/chats.json",'+rb') as f:
            batch_messages =[]

            for user in ijson.items(f,'item'):
                # Extract & Transform
                for conversation in user.get('conversations',[]):
                   
                    batch_messages.extend(flatten_and_anonymize_conversation_history(user.get('user_id',''),user.get('email',''), conversation))
                   
                    if len(batch_messages) >=BATCH_SIZE:
                        # Load to DB
                        result = messages_repo.upsert_messages(messages=batch_messages)
                        print(f"{len(batch_messages)} messages upserted: {result}")
                        batch_messages.clear()
    except Exception as e:
        logger.error(e)
    
       