import uuid
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    description: str = ""

    @abstractmethod
    def _build(self): ...

    def _rebuild(self, model: str):
        """Substitui o modelo LLM e reconstrói o agente.

        Args:
            model (str): Novo identificador de modelo (ex.: ``"openai:gpt-4o"``).
        """
        self._model = model
        self._build()

    async def _assert_thread_id(self, thread_id: str | None) -> str:
        """Valida ou gera um thread_id para a conversa.

        Se ``thread_id`` não for fornecido, cria um novo UUID. Se for fornecido,
        verifica que existe no checkpointer.

        Args:
            thread_id (str | None): ID da conversa existente ou ``None`` para nova.

        Returns:
            str: Thread ID válido para uso na invocação.

        Raises:
            ValueError: Se o ``thread_id`` fornecido não existir no checkpointer.
        """
        if not thread_id:
            thread_id = str(uuid.uuid4())
        elif not await self._checkpointer.aget({"configurable": {"thread_id": thread_id}}):
            raise ValueError(f"The provided thread_id ({thread_id}) does not exist.")

        return thread_id
    