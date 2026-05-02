import streamlit as st
import logging

from controllers.api_client import APIClient


st.title("Assistente de Conhecimento")

if not st.session_state.get("api_client"):
    st.session_state["api_client"] = APIClient()

if not st.session_state.get("thread"):
    st.session_state.thread = []

# Initial chat message
with st.chat_message("ai"):
    st.markdown("""
**Olá!** Sou um assistente conversacional com acesso a uma base de documentos indexados.

Posso responder perguntas gerais ou buscar informações específicas nos documentos disponíveis — \
basta perguntar naturalmente que identifico quando é necessário consultar a base de conhecimento.

**Sugestões para começar:**
- "Quais documentos estão disponíveis?"
- "O que você sabe sobre [tema]?"
- "Encontre trechos que mencionam [termo]."
""")

# Keeping the previous chat messages at the chat display
for message in st.session_state.thread:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something"):
    # Saving the user input
    message = {"role": "user", "content": prompt}
    st.session_state["thread"].append(message)

    # Displaying the user input at the chat
    with st.chat_message("user"):
        st.markdown(message["content"])

    # Helper instances
    api_client: APIClient = st.session_state.get("api_client")

    # Processing user message and generating an answer
    with st.spinner(text="Processando mensagem..."):
        response = api_client.ask_conversational_agent(
            user_prompt=prompt,
            thread_id=st.session_state.get("thread_id"),
        )
        answer = response.get("answer") or "Desculpe, houve um erro durante o processamento da sua mensagem :/"
        thread_id = response.get("thread_id")

        # Saving the thread_id to future reference of the same chat
        if thread_id:
            st.session_state["thread_id"] = thread_id
    
    # Displaying the AI answer
    with st.chat_message("ai"):
        st.write(answer)

    # Saving the AI answer
    st.session_state["thread"].append({"role": "ai", "content": answer})
