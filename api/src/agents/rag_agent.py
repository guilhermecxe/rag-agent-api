from langchain.chat_models import init_chat_model
from langchain.agents import create_agent

from src.agents.tools.rag_tools import RAGToolkit
from src.services.files_service import FilesService
from src.settings import Settings


class RAGAgent:
    def __init__(self, files_service: FilesService, settings: Settings):
        self._model = settings.rag_agent_default_model
        self._files_service = files_service
        self._settings = settings

        self._build()

    def _rebuild(self, model: str):
        self._model = model
        self._build()

    def _build(self):
        self._llm = init_chat_model(self._model)

        tools = RAGToolkit(
            files_service=self._files_service, settings=self._settings
        ).get_tools()

        self._agent = create_agent(
            model=self._llm,
            system_prompt="",
            tools=tools
        )

    async def ainvoke(self, message: str, thread_id: str = None, model: str = None) -> str:
        if isinstance(model, str) and model != self._model:
            self._rebuild(model=model)

        input = {"messages": [{"role": "user", "content": message}]}

        response = await self._agent.ainvoke(
            input=input
        )

        result = response["messages"][-1].content
        return result
    