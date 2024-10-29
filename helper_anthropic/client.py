import asyncio
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
from tkr_utils import setup_logging, logs_and_exceptions

# Setup logging
logger = setup_logging(__name__)

class AnthropicHelper:
    """Helper class to interact with the Anthropic API."""

    def __init__(self, api_key: Optional[str], model: str):
        """Initialize the Anthropic client."""
        if not api_key:
            raise ValueError("Anthropic API key is required")
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        logger.info("AnthropicHelper initialized with model: %s", self.model)

    @logs_and_exceptions(logger)
    def send_message(self, messages: List[Dict[str, Any]], temperature: float = 0.0, max_tokens: int = 1024) -> str:
        """Send a message to the Anthropic API and return the response."""
        logger.debug("Sending message to Anthropic API with model: %s", self.model)

        # Format messages for Anthropic API
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                formatted_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

        response = self.client.messages.create(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.debug("Message sent successfully")
        return response.content[0].text if response.content else ""

    @logs_and_exceptions(logger)
    def send_message_json(self, messages: List[Dict[str, Any]], temperature: float = 0.0, max_tokens: int = 1024) -> str:
        """Send a message expecting JSON response."""
        logger.debug("Sending JSON message to Anthropic API with model: %s", self.model)

        system_message = "Always respond in valid JSON format."

        response = self.client.messages.create(
            model=self.model,
            system=system_message,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        logger.debug("JSON message sent successfully")
        return response.content[0].text if response.content else ""

    @logs_and_exceptions(logger)
    def stream_response(self, messages: List[Dict[str, Any]], max_tokens: int = 1024) -> None:
        """Stream a response from the API."""
        logger.debug("Starting to stream response from Anthropic API")

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


class AnthropicBatchClient:
    """Combined client handling both single and batch requests."""

    def __init__(self, api_key: str, model: str):
        """Initialize the batch client with helper."""
        self.helper = AnthropicHelper(api_key=api_key, model=model)
        self.requests_processed = 0
        self.request_queue = asyncio.Queue()

async def process_batch(
    self,
    requests: List[Dict[str, Any]],
    output_file: Optional[str] = None
) -> List[str]:
    """Process a batch of requests with rate limiting."""
    responses = []

    for request in requests:
        await self.request_queue.put(request)

    while not self.request_queue.empty():
        request = await self.request_queue.get()
        try:
            # Flatten the message structure - request is already a Dict
            response = self.helper.send_message([request])
            responses.append(response)
            if output_file:
                self.save_response(output_file, response)
            self.requests_processed += 1
            logger.info(f"Processed request {self.requests_processed}/{len(requests)}")
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
        finally:
            self.request_queue.task_done()

    return responses

    def save_response(self, output_file: str, response: str) -> None:
        """Save the response to the output file."""
        with open(output_file, 'a') as file:
            file.write(json.dumps({"response": response}) + "\n")
        logger.debug("Response saved successfully")
