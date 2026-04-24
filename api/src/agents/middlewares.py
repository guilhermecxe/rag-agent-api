from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain.messages import SystemMessage, RemoveMessage, ToolMessage, AIMessage, AnyMessage
from langgraph.runtime import Runtime
from langgraph.graph.message import REMOVE_ALL_MESSAGES


def _trim_orphaned_tools(messages: list[AnyMessage]):
    tool_calls_ids = []
    kept_messages = []

    for message in messages:
        if isinstance(message, AIMessage) and message.tool_calls:
            for tool_call in message.tool_calls:
                tool_calls_ids.append(tool_call["id"])
        elif isinstance(message, ToolMessage):
            if message.tool_call_id not in tool_calls_ids:
                continue # Não será mantida no histórico

        kept_messages.append(message)

    return kept_messages

@before_model
def trim_messages(state: AgentState, runtime: Runtime, limit: int = 20):
    """
    Keep only the last `limit` messages in the conversation history.
    """

    messages = state["messages"]
    if len(messages) < limit:
        return None # No update necessary

    # Encontrando e mantendo SystemMessage's
    system_messages = [msg for msg in messages if isinstance(msg, SystemMessage)]
    
    # Mantendo as últimas `limit` mensagens (não-sistema)
    other_messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
    kept_messages = system_messages + other_messages[-limit:]

    # Removendo respostas de tools cujas chamadas não aparecem mais
    kept_messages = _trim_orphaned_tools(kept_messages)

    return {
        "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *kept_messages]
    }
