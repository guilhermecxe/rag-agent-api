from fastapi import APIRouter, Depends, HTTPException, Body
import logging

from src.di import get_rag_agent
from src.agents.rag_agent import RAGAgent
from src.schemas.agents import TalkRequest, TalkResponse


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()


@router.post("/talk", response_model=TalkResponse)
async def talk(
    request: TalkRequest = Body(...),
    rag_agent: RAGAgent = Depends(get_rag_agent)
):
    """Envia uma mensagem ao agente RAG e retorna a resposta gerada.

    Suporta conversas contínuas por meio do ``thread_id``. Se omitido, uma
    nova thread é criada automaticamente e seu ID é retornado na resposta.

    Args:
        request (TalkRequest): Corpo da requisição com os campos:
            - ``message`` (str): Mensagem do usuário.
            - ``thread_id`` (str | None): ID da conversa existente ou ``None``
              para iniciar uma nova thread.
        rag_agent (RAGAgent): Injetado pelo FastAPI via DI.

    Returns:
        TalkResponse: Objeto com os campos:
            - ``answer`` (str): Resposta gerada pelo agente.
            - ``thread_id`` (str): ID da thread usada ou criada.

    Raises:
        HTTPException: 500 se ocorrer qualquer erro durante a invocação do agente.
    """
    try:
        request.thread_id = None if not request.thread_id else request.thread_id

        result = await rag_agent.ainvoke(
            message=request.message,
            thread_id=request.thread_id
        )

        return {
            "answer": result.get("answer"),
            "thread_id": result.get("thread_id")
        }
    except Exception as e:
        logger.exception("Fail on /talk")
        raise HTTPException(status_code=500, detail=str(e))
    