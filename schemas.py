from pydantic import BaseModel
from typing import Union

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    reply: Union[str, dict] 
