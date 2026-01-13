from pydantic import BaseModel
from typing import Optional, Union, Dict

class ChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    reply: Union[str, Dict]

class FilterRequest(BaseModel):
    context: str
    query: str

class FilterResponse(BaseModel):
    sql: str
