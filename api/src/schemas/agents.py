from pydantic import BaseModel
from typing import Optional


class AgentRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Olá",
                "thread_id": ""
            }
        }

class AgentResponse(BaseModel):
    answer: str
    thread_id: str
