from typing import List
from dateutil import parser
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from ..data.models import RawChatMessage

PII_ENTITIES = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS", "CREDIT_CARD","LOCATION"]

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def extract_raw_message(record):
    message = RawChatMessage(
        chat_id= record['conversation_id'],
        user_id=record['user_id'],
        timestamp=parser.parse(record['timestamp']),
        message_text=flatten_message(record),
        metadata= record['metadata'])
    return message

def flatten_message(messages:List[dict]):
    flattened_message =""
    
    for message in messages:
        flattened_message+= f"[{message['role']}] {message['content']} \n\n"
    
    return flatten_message

def sanitize_text(text:str) -> str:
    result = analyzer.analyze(text=text,entities=PII_ENTITIES, language='en')
    cleaned_text = anonymizer.anonymize(text=text, analyzer_results=result)

    return cleaned_text

def vectorize(text:str) -> List[float]:
    pass
def classify(text:str) -> List[str]:
    pass