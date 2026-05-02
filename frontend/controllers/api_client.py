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