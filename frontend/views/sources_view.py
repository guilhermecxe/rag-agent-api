import streamlit as st

from controllers.api_client import APIClient

st.title("Gerenciamento de Fontes")

if not st.session_state.get("api_client"):
    st.session_state["api_client"] = APIClient()

api_client: APIClient = st.session_state["api_client"]

tab_add, tab_read, tab_delete = st.tabs(["Adicionar", "Consultar", "Remover"])


with tab_add:
    st.subheader("Adicionar fonte")
    uploaded_file = st.file_uploader("Selecione um arquivo PDF", type=["pdf"])
    if st.button("Enviar", disabled=uploaded_file is None):
        with st.spinner("Enviando arquivo..."):
            result = api_client.upload_source(
                file_bytes=uploaded_file.read(),
                filename=uploaded_file.name
            )
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"**{uploaded_file.name}** indexado com sucesso.")


with tab_read:
    st.subheader("Consultar fontes")

    list_tab, search_tab = st.tabs(["Listar", "Buscar"])

    with list_tab:
        page = st.number_input("Página", min_value=1, value=1, step=1, key="list_page")
        if st.button("Listar", key="btn_list"):
            with st.spinner("Carregando..."):
                result = api_client.get_sources(page=page)
            if "error" in result:
                st.error(result["error"])
            else:
                sources_page = result.get("sources", {})
                items = sources_page.get("sources", [])
                if items:
                    for name in items:
                        st.markdown(f"- {name}")
                    st.caption(
                        f"Página {sources_page.get('current_page')} "
                        f"de {sources_page.get('last_page')}"
                    )
                else:
                    st.info("Nenhuma fonte encontrada.")

    with search_tab:
        pattern = st.text_input("Padrão regex", key="search_pattern")
        page_s = st.number_input("Página", min_value=1, value=1, step=1, key="search_page")
        if st.button("Buscar", key="btn_search", disabled=not pattern):
            with st.spinner("Buscando..."):
                result = api_client.search_sources_regex(pattern=pattern, page=page_s)
            if "error" in result:
                st.error(result["error"])
            else:
                items = result.get("sources", [])
                if items:
                    for name in items:
                        st.markdown(f"- {name}")
                    st.caption(
                        f"Página {result.get('current_page')} "
                        f"de {result.get('last_page')}"
                    )
                else:
                    st.info("Nenhuma fonte encontrada para esse padrão.")


with tab_delete:
    st.subheader("Remover fonte")
    source_title = st.text_input("Nome exato da fonte")
    if st.button("Remover", type="primary", disabled=not source_title):
        with st.spinner("Removendo..."):
            result = api_client.delete_source(source_title=source_title)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"**{source_title}** removida com sucesso.")
