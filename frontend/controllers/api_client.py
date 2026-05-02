import requests
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class APIClient:
    """
    Responsible for handling API requests to the backend.
    """
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL")
        self.api_key = os.getenv("API_KEY")

    def ask_conversational_agent(self, user_prompt: str, thread_id: str | None):
        """
        Sends a user prompt to the conversational agent and retrieves the response.

        Args:
            user_prompt (str): The user's input prompt.
            thread_id (str): The ID of the conversation thread.

        Returns:
            dict: The JSON response from the API, containing the updated thread information.
        """

        headers = {
            "X-API-KEY": self.api_key
        }
        data = {
            "message": user_prompt,
            "thread_id": thread_id
        }
        try:
            response = requests.post(
                url=f"{self.base_url}/agents/conversational_agent",
                headers=headers,
                json=data
            )
        except requests.exceptions.ConnectionError:
            answer = "Desculpe, houve um erro durante o processamento da sua mensagem :/"
            thread_id = None
            logger.exception("Erro ao processamento mensagem do usuário.")
        else:
            response.raise_for_status()
            response_json = response.json()
            if response_json:
                answer = response_json.get("answer")
                thread_id = response_json.get("thread_id")
            else:
                answer = "Desculpe, houve um erro durante o processamento da sua mensagem :/"
                thread_id = None
        
        return {
            "answer": answer,
            "thread_id": thread_id
        }

    def _headers(self) -> dict:
        return {"X-API-KEY": self.api_key}

    def _http_error_message(self, exc: requests.exceptions.HTTPError, fallback: str) -> str:
        try:
            return exc.response.json().get("detail", fallback)
        except Exception:
            return fallback

    def upload_source(self, file_bytes: bytes, filename: str) -> dict:
        try:
            response = requests.post(
                url=f"{self.base_url}/sources/upload_source",
                headers=self._headers(),
                files={"file": (filename, file_bytes, "application/pdf")}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": self._http_error_message(e, "Erro ao fazer upload do arquivo.")}
        except requests.exceptions.RequestException:
            logger.exception("Erro ao fazer upload da fonte.")
            return {"error": "Erro ao fazer upload do arquivo."}

    def get_sources(self, page: int = 1) -> dict:
        try:
            response = requests.get(
                url=f"{self.base_url}/sources/get_sources",
                headers=self._headers(),
                params={"page": page}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": self._http_error_message(e, "Erro ao listar fontes.")}
        except requests.exceptions.RequestException:
            logger.exception("Erro ao listar fontes.")
            return {"error": "Erro ao listar fontes."}

    def search_sources_regex(self, pattern: str, page: int = 1) -> dict:
        try:
            response = requests.get(
                url=f"{self.base_url}/sources/search_sources_regex",
                headers=self._headers(),
                params={"pattern": pattern, "page": page}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": self._http_error_message(e, "Erro ao buscar fontes.")}
        except requests.exceptions.RequestException:
            logger.exception("Erro ao buscar fontes por regex.")
            return {"error": "Erro ao buscar fontes."}

    def delete_source(self, source_title: str) -> dict:
        try:
            response = requests.delete(
                url=f"{self.base_url}/sources/delete_source",
                headers=self._headers(),
                params={"source_title": source_title}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            return {"error": self._http_error_message(e, "Erro ao deletar a fonte.")}
        except requests.exceptions.RequestException:
            logger.exception("Erro ao deletar fonte.")
            return {"error": "Erro ao deletar a fonte."}