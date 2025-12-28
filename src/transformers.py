from datetime import datetime
import logging
from typing import List
from dateutil import parser
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer.analyzer_engine import NlpEngineProvider
from src.models import ChatMessage


PII_ENTITIES = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD","LOCATION"]

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def get_message_text_from_mapping(mapping:dict)->str:
    content = mapping.get('message',{}).get('content',{})
   
    if content.get('content_type') in ['text','code']:
        merged_text = "".join(content.get('parts'))
        role = mapping.get('message',{}).get('author',{}).get('role','')
        return f"[{role.capitalize()}] {merged_text}"
    return ""

def flatten_and_anonymize_conversation_history(user_id:str, user_email:str, conversation:dict)->List[ChatMessage]:
    raw_messages:List[ChatMessage] = []
    for message_id, mapping in conversation.get("mapping",{}).items():
                   
            parent_message_text = ""
            
            if mapping.get('parent') and conversation.get("mapping").get(mapping.get('parent')):
                parent_message_text = get_message_text_from_mapping(conversation.get("mapping").get(mapping.get('parent')))
                parent_message_text+='\n'
            
            current_message_text = get_message_text_from_mapping(mapping)

            metadata = {
                            
                            'user_email' : user_email,
                            'conversation_id' : conversation.get('conversation_id', ''),
                            'user_id' :user_id
                        }
            if conversation.get('create_time'):
                metadata['create_time'] = datetime.fromtimestamp(float(conversation.get('create_time'))).isoformat()
            
            cleaned_message_text = sanitize_text(text=parent_message_text + current_message_text)    
            message = ChatMessage(
                        message_id = message_id,
                        message_text = cleaned_message_text,
                        metadata = metadata
                       )
      
            raw_messages.append(message)
    return raw_messages

def sanitize_text(text:str) -> str:
    result = analyzer.analyze(text=text,entities=PII_ENTITIES, language='en')
    cleaned_text = anonymizer.anonymize(text=text, analyzer_results=result).text

    return cleaned_text