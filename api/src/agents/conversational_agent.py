from langgraph.checkpoint.base import BaseCheckpointSaver
from langchain_core.tools import StructuredTool
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langfuse.langchain import CallbackHandler
from langfuse import propagate_attributes
import uuid

from src.agents.base_agent import BaseAgent
from src.agents.middlewares import trim_messages
from src.settings import Settings


class ConversationalAgent(BaseAgent):
    def __init__(self, settings: Settings, checkpointer: BaseCheckpointSaver, subagents: list[BaseAgent] = []):
        self._model = settings.conversational_agent_default_model
        self._settings = settings
        self._checkpointer = checkpointer
        self._subagents = subagents

        self._build()

    def _build(self):
        self._llm = init_chat_model(self._model)

        subagents_as_tools = [
            StructuredTool.from_function(
                coroutine=subagent.ainvoke_as_tool,
                name=type(subagent).__name__,
                description=subagent.description,
            )
            for subagent in self._subagents
        ]

        tools = subagents_as_tools
        
        self._agent = create_agent(
            model=self._llm,
            system_prompt="",
            tools=tools,
            checkpointer=self._checkpointer,
            middleware=[trim_messages]
        ).with_config({"callbacks": [CallbackHandler()]})
    
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

        thread_id = await self._assert_thread_id(thread_id)

        with propagate_attributes(trace_name="ConversationalAgent", session_id=thread_id):
            response = await self._agent.ainvoke(
                input=input,
                config={
                    "configurable": {"thread_id": thread_id}
                }
            )

        answer = response["messages"][-1].content
        return {
            "answer": answer,
            "thread_id": thread_id
        }
    