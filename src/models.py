from pydantic import BaseModel


class ChatMessage(BaseModel):

    message_id:str
    message_text:str
    metadata:dict
