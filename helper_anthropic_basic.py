from typing import List, Dict, Any
from dotenv import load_dotenv
from anthropic import Anthropic

from .config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from tkr_utils import setup_logging, logs_and_exceptions

# Setup logging
logger = setup_logging(__file__)

# Load environment variables from .env file
load_dotenv()

class AnthropicHelper:
    @logs_and_exceptions(logger)
    def __init__(self, api_key: str = ANTHROPIC_API_KEY, model: str = ANTHROPIC_MODEL):
        """
        Initialize the Anthropic client.

        Args:
            api_key: Anthropic API key
            model: Model to use for completions
        """
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=self.api_key)

        logger.info("AnthropicHelper initialized with model: %s", self.model)

    @logs_and_exceptions(logger)
    def send_message(self, messages: List[Dict[str, Any]], temperature: float = 0.0, max_tokens: int = 1024) -> Dict[str, Any]:
        """
        Send a message to the Anthropic API and return the response.

        Args:
            messages: List of message dictionaries
            temperature: Controls randomness in the response (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            Dict containing the API response
        """
        logger.debug("Sending message to Anthropic API with model: %s", self.model)
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.debug("Message sent successfully")
        # Extract text from first content block
        return response.content[0].text if response.content else ""

    @logs_and_exceptions(logger)
    def send_message_json(self, messages: List[Dict[str, Any]], temperature: float = 0.0, max_tokens: int = 1024) -> str:
        """
        Send a message to the Anthropic API expecting a JSON response.

        Args:
            messages: List of message dictionaries
            temperature: Controls randomness in the response (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate

        Returns:
            String containing the response text
        """
        logger.debug("Sending JSON message to Anthropic API with model: %s", self.model)

        # Add system message as a top-level parameter
        system_message = "Always respond in valid JSON format."

        response = self.client.messages.create(
            model=self.model,
            system=system_message,  # System message as top-level parameter
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.debug("JSON message sent successfully")
        # Extract text from first content block
        return response.content[0].text if response.content else ""

    @logs_and_exceptions(logger)
    def stream_response(self, messages: List[Dict[str, Any]], max_tokens: int = 1024) -> None:
        """
        Stream a response from the Anthropic API.

        Args:
            messages: List of message dictionaries
            max_tokens: Maximum number of tokens to generate
        """
        logger.debug("Starting to stream response from Anthropic API with model: %s", self.model)
        with self.client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            stream=True
        ) as stream:
            for chunk in stream:
                if chunk.type == 'content_block_delta':
                    print(chunk.delta.text, end="")
        logger.debug("Streaming completed")

# Example usage
if __name__ == "__main__":
    myChat = AnthropicHelper()
    messages = [{"role": "user", "content": "Say hi. This is a test :)"}]

    # Send a message and get a response
    response = myChat.send_message(messages)
    logger.info(response)

    # Stream a response
    myChat.stream_response(messages)

__all__ = ["AnthropicHelper"]
