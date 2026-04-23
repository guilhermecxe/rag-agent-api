from pydantic import BaseModel
from typing import Optional


class TalkRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Olá",
                "thread_id": ""
            }
        }

class TalkResponse(BaseModel):
    answer: str
    thread_id: str
