from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langfuse.langchain import CallbackHandler
import uuid

from src.agents.tools.rag_tools import RAGToolkit
from src.services.files_service import FilesService
from src.settings import Settings


class RAGAgent:
    """Agente conversacional com Retrieval-Augmented Generation (RAG).

    Mantém memória de conversas por thread e usa ferramentas de busca vetorial
    para enriquecer as respostas do LLM com documentos relevantes.

    Attributes:
        _model (str): Identificador do modelo LLM atual (ex.: ``"openai:gpt-4o-mini"``).
        _files_service (FilesService): Serviço de acesso ao banco de documentos.
        _settings (Settings): Configurações da aplicação.
        _checkpointer (BaseCheckpointSaver): Gerenciador de estado das conversas.
        _llm: Instância do modelo de linguagem inicializado.
        _agent: Grafo do agente LangGraph.
    """

    def __init__(
            self, files_service: FilesService, settings: Settings,
            checkpointer: BaseCheckpointSaver
        ):
        """Inicializa e constrói o agente RAG.

        Args:
            files_service (FilesService): Serviço usado pelas ferramentas de busca.
            settings (Settings): Configurações com modelo padrão e limites de busca.
            checkpointer (BaseCheckpointSaver): Saver de estado para memória de conversas.
        """
        self._model = settings.rag_agent_default_model
        self._files_service = files_service
        self._settings = settings
        self._checkpointer = checkpointer

        self._build()

    def _rebuild(self, model: str):
        """Substitui o modelo LLM e reconstrói o agente.

        Args:
            model (str): Novo identificador de modelo (ex.: ``"openai:gpt-4o"``).
        """
        self._model = model
        self._build()

    def _build(self):
        """Instancia o LLM, cria as ferramentas RAG e compila o grafo do agente."""
        self._llm = init_chat_model(self._model)

        tools = RAGToolkit(
            files_service=self._files_service, settings=self._settings
        ).get_tools()

        self._agent = create_agent(
            model=self._llm,
            system_prompt="",
            tools=tools,
            checkpointer=self._checkpointer
        )

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

    async def ainvoke(self, message: str, thread_id: str = None, model: str = None) -> dict:
        """Envia uma mensagem ao agente e retorna a resposta.

        Args:
            message (str): Mensagem do usuário.
            thread_id (str | None): ID da conversa. Se ``None``, inicia uma nova.
            model (str | None): Modelo a usar nesta invocação. Se diferente do atual,
                reconstrói o agente antes de invocar.

        Returns:
            dict: Dicionário com as chaves:
                - ``answer`` (str): Resposta gerada pelo agente.
                - ``thread_id`` (str): ID da conversa usada.
        """
        if isinstance(model, str) and model != self._model:
            self._rebuild(model=model)

        input = {"messages": [{"role": "user", "content": message}]}

        callbacks = [
            # O cliente Langfuse é inicializado em api/main.py para
            # o handler funcionar.
            CallbackHandler()
        ]

        thread_id = await self._assert_thread_id(thread_id)

        response = await self._agent.ainvoke(
            input=input,
            config={
                "callbacks": callbacks,
                "configurable": {"thread_id": thread_id}
            }
        )

        answer = response["messages"][-1].content
        return {
            "answer": answer,
            "thread_id": thread_id
        }
    