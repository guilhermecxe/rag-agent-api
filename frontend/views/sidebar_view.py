import streamlit as st

def show_sidebar():
    with st.sidebar:
        body = (
            "This is an application developed by **Guilherme Alves**. "
            "You can reach me out at [Github](https://github.com/guilhermecxe) "
            "or [LinkedIn](https://www.linkedin.com/in/guilhermecxe).\n\n"
            "\n\n---\n"
            "Esta é uma aplicação desenvolvida por **Guilherme Alves**. "
            "Você consegue encontrar me encontrar no [Github](https://github.com/guilhermecxe) "
            "ou no [LinkedIn](https://www.linkedin.com/in/guilhermecxe).\n\n"
        )
        st.markdown(body)
        