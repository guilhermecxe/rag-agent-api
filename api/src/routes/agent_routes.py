from fastapi import APIRouter, Depends, HTTPException
import logging

from src.di import get_rag_agent
from src.agents.rag_agent import RAGAgent


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

@router.post("/talk")
async def talk(
    message: str,
    thread_id: str = None,
    rag_agent: RAGAgent = Depends(get_rag_agent)
):
    try:
        answer = await rag_agent.ainvoke(
            message=message,
            thread_id=thread_id
        )
        
        return {
            "answer": answer
        }
    except Exception as e:
        logger.exception("Fail on /talk")
        raise HTTPException(status_code=500, detail=str(e))
    