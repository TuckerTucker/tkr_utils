import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI, AsyncOpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_EMBEDDER
from .decorators import logs_and_exceptions
from .config_logging import setup_logging

# Load environment variables from .env file
load_dotenv()

# Setup logging
logger = setup_logging(__file__)

class OpenAIHelper:
    @logs_and_exceptions(logger)
    def __init__(self, api_key: str = OPENAI_API_KEY, model: str = OPENAI_MODEL, embedder: str = OPENAI_EMBEDDER, async_mode: bool = False):
        self.api_key = api_key
        self.model = model
        self.embedder = embedder
        self.async_mode = async_mode

        if self.async_mode:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = OpenAI(api_key=self.api_key)

        logger.info("OpenAIHelper initialized with model: %s, embedder: %s, and async_mode: %s", self.model, self.embedder, self.async_mode)

    @logs_and_exceptions(logger)
    async def send_message_async(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        """
        Send an asynchronous message to the OpenAI API and return the response.
        """
        logger.info("Sending async message to OpenAI API with model: %s", self.model)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        logger.info("Async message sent successfully.")
        return response

    @logs_and_exceptions(logger)
    async def send_message_json_async(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        """
        Send an asynchronous message to the OpenAI API and return the response.
        """
        logger.info("Sending async message to OpenAI API with model: %s", self.model)
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        logger.info("Async message sent successfully.")
        return response

    @logs_and_exceptions(logger)
    def send_message(self, messages: List[Dict[str, Any]], temperature: float = 0.0) -> Dict[str, Any]:
        """
        Send a synchronous message to the OpenAI API and return the response.
        """
        if self.async_mode:
            raise RuntimeError("Cannot call send_message in async mode. Use send_message_async instead.")
        
        logger.info("Sending message to OpenAI API with model: %s", self.model)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature
        )
        logger.info("Message sent successfully.")
        return response

    @logs_and_exceptions(logger)
    async def stream_response_async(self, messages: List[Dict[str, Any]]) -> None:
        """
        Stream responses asynchronously from the OpenAI API.
        """
        logger.info("Starting to stream async response from OpenAI API with model: %s", self.model)
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        logger.info("Async streaming completed.")

    @logs_and_exceptions(logger)
    def stream_response(self, messages: List[Dict[str, Any]]) -> None:
        """
        Stream responses synchronously from the OpenAI API.
        """
        if self.async_mode:
            raise RuntimeError("Cannot call stream_response in async mode. Use stream_response_async instead.")
        
        logger.info("Starting to stream response from OpenAI API with model: %s", self.model)
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        logger.info("Streaming completed.")

# Example usage
if __name__ == "__main__":
    myChat = OpenAIHelper(async_mode=False)  # Change to True for async mode
    messages = [{"role": "user", "content": "Say this is a test!"}]

    # Send a message and get a response
    if myChat.async_mode:
        response = asyncio.run(myChat.send_message_async(messages))
    else:
        response = myChat.send_message(messages)
    
    logger.info(response)

    # Stream a response
    if myChat.async_mode:
        asyncio.run(myChat.stream_response_async(messages))
    else:
        myChat.stream_response(messages)

__all__ = ["OpenAIHelper"]
