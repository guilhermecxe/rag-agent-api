from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langfuse.langchain import CallbackHandler
from langfuse import propagate_attributes

from src.agents.base_agent import BaseAgent
from src.agents.tools.sources_tools import SourcesToolkit
from src.agents.prompts.knowledge_agent import SYSTEM_PROMPT, SYSTEM_PROMPT_AS_TOOL
from src.services.sources_service import SourcesService
from src.settings import Settings


class KnowledgeAgent(BaseAgent):
    """Agente especializado em acessar a base de conhecimento indexada.

    Mantém memória de conversas por thread e usa ferramentas de busca para
    recuperar e sintetizar informações dos documentos indexados.

    Attributes:
        _model (str): Identificador do modelo LLM atual (ex.: ``"openai:gpt-4o-mini"``).
        _sources_service (SourcesService): Serviço de acesso ao banco de documentos.
        _settings (Settings): Configurações da aplicação.
        _checkpointer (BaseCheckpointSaver): Gerenciador de estado das conversas.
        _llm: Instância do modelo de linguagem inicializado.
        _agent: Grafo do agente LangGraph.
    """

    description: str = (
        "Agente especializado em acessar a base de conhecimento indexada. "
        "Pode listar as fontes disponíveis, buscar fontes por nome (regex), "
        "buscar trechos por conteúdo (busca regex ou semântica) e recuperar "
        "trechos vizinhos pelo índice para ampliar o contexto. "
        "Use para qualquer consulta sobre o conteúdo dos documentos indexados."
    )

    def __init__(
            self, sources_service: SourcesService, settings: Settings,
            checkpointer: BaseCheckpointSaver
        ):
        """Inicializa e constrói o agente de conhecimento.

        Args:
            sources_service (SourcesService): Serviço usado pelas ferramentas de busca.
            settings (Settings): Configurações com modelo padrão e limites de busca.
            checkpointer (BaseCheckpointSaver): Saver de estado para memória de conversas.
        """
        self._model = settings.knowledge_agent_default_model
        self._sources_service = sources_service
        self._settings = settings
        self._checkpointer = checkpointer

        self._build()

    def _build(self):
        """Instancia o LLM, cria as ferramentas de busca e compila os grafos do agente."""
        self._llm = init_chat_model(self._model)

        tools = SourcesToolkit(
            sources_service=self._sources_service
        ).get_tools()

        self._agent = create_agent(
            model=self._llm,
            system_prompt=SYSTEM_PROMPT,
            tools=tools,
            checkpointer=self._checkpointer
        )

        self._agent_as_tool = create_agent(
            model=self._llm,
            system_prompt=SYSTEM_PROMPT_AS_TOOL,
            tools=tools,
        )

    async def ainvoke(
            self, message: str, thread_id: str = None,
            model: str = None, as_tool: bool = False
        ) -> dict:
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

        callbacks = []
        configurable = {}
        thread_id = None
        if as_tool:
            agent = self._agent_as_tool
        else:
            agent = self._agent
            # O cliente Langfuse é inicializado em api/main.py para
            # o handler funcionar.
            callbacks.append(CallbackHandler())

            # Criando thread para salvar histórico
            thread_id = await self._assert_thread_id(thread_id)
            configurable["thread_id"] = thread_id

        with propagate_attributes(trace_name="KnowledgeAgent", session_id=thread_id):
            response = await agent.ainvoke(
                input=input,
                config={
                    "callbacks": callbacks,
                    "configurable": configurable
                }
            )

        answer = response["messages"][-1].content
        return {
            "answer": answer,
            "thread_id": thread_id
        }
    
    async def ainvoke_as_tool(self, message: str) -> str:
        result = await self.ainvoke(
            message=message,
            as_tool=True
        )
        return result["answer"]
