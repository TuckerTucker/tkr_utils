# openai_helper.py
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDER
from .decorators import logs_and_exceptions
from .config_logging import setup_logging

client = OpenAI(api_key=OPENAI_API_KEY)

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = setup_logging(__file__)

class OpenAIHelper:
    @logs_and_exceptions(logger)
    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = OPENAI_MODEL, embedder: str = OPENAI_EMBEDDER):
        self.api_key = api_key
        self.model = model
        self.embedder = embedder
        logger.info("OpenAIHelper initialized with model: %s and embedder: %s", self.model, self.embedder)

    @logs_and_exceptions(logger)
    def send_message(self, messages: List[Dict[str, Any]], temperature: float = 0.3) -> Dict[str, Any]:
        """
        Send a message to the OpenAI API and return the response.

        Args:
            messages (List[Dict[str, Any]]): List of message objects for the API call.
            temperature (float): Sampling temperature for the response.

        Returns:
            Dict[str, Any]: Response from the OpenAI API.
        """
        try:
            logger.info("Sending message to OpenAI API with model: %s", self.model)
            response = client.chat.completions.create(model=self.model,
            messages=messages,
            temperature=temperature)
            logger.info("Message sent successfully.")
            return response
        except Exception as e:
            logger.error("An error occurred while sending the message: %s", e)
            raise

    @logs_and_exceptions(logger)    
    def stream_response(self, messages: List[Dict[str, Any]]) -> None:
        """
        Stream responses from the OpenAI API.

        Args:
            messages (List[Dict[str, Any]]): List of message objects for the API call.
        """
        try:
            logger.info("Starting to stream response from OpenAI API with model: %s", self.model)
            stream = client.chat.completions.create(model=self.model,
            messages=messages,
            stream=True)
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
            logger.info("Streaming completed.")
        except Exception as e:
            logger.error("An error occurred while streaming the response: %s", e)
            raise

# Example usage
if __name__ == "__main__":
    myChat = OpenAIHelper()
    messages = [{"role": "user", "content": "Say this is a test!"}]

    # Send a message and get a response
    response = myChat.send_message(messages)
    logger.info(response)

    # Stream a response
    myChat.stream_response(messages)

__all__ = ["OpenAIHelper"]