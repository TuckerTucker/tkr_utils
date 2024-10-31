# tkr_bias_stories/tkr_utils/helper_anthropic/client.py

import asyncio
from typing import List, Dict, Any, Optional, Union, AsyncGenerator
from anthropic import Anthropic
from tkr_utils import setup_logging, logs_and_exceptions
from .models import APIResponse

logger = setup_logging(__file__)

class AnthropicHelper:
    """Helper class to interact with the Anthropic API asynchronously."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-sonnet-20240307"
    ):
        """Initialize Anthropic client with API key and model.

        Args:
            api_key: Anthropic API key
            model: Model identifier to use
        """
        if not api_key:
            raise ValueError("Anthropic API key is required")

        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        self.loop = asyncio.get_running_loop()

        logger.info("AnthropicHelper initialized with model: %s", self.model)

    async def _run_in_executor(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Run synchronous client methods in thread pool.

        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Response from function execution
        """
        if self.loop is None:
            self.loop = asyncio.get_running_loop()

        return await self.loop.run_in_executor(
            None,
            lambda: func(*args, **kwargs)
        )

    @logs_and_exceptions(logger)
    async def send_message(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.0,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Union[APIResponse, AsyncGenerator[str, None]]:
        """Send a message to the Anthropic API with option to stream.

        Args:
            messages: List of message dicts with role and content
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Either APIResponse object or AsyncGenerator for streaming
        """
        try:
            # Format messages for Anthropic API
            anthropic_messages = [
                {
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                }
                for msg in messages
            ]

            # Create message parameters
            message_params = {
                "messages": anthropic_messages,
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }

            # Call Anthropic API in executor
            response = await self._run_in_executor(
                self.client.messages.create,
                **message_params
            )

            if stream:
                return self._stream_response(response)

            # Handle non-streaming response
            return APIResponse(
                content=response.content[0].text if response.content else "",
                request_id=response.id,
                success=True,
                metadata={
                    "usage": response.usage,
                    "model": response.model,
                    "role": response.role,
                    "stop_reason": response.stop_reason,
                    "stop_sequence": response.stop_sequence
                }
            )

        except Exception as e:
            logger.error("Error in send_message: %s", str(e))
            if not stream:
                return APIResponse(
                    content="",
                    request_id="",
                    success=False,
                    error=str(e)
                )
            raise

    async def _stream_response(self, response: Any) -> AsyncGenerator[str, None]:
        """Process streaming response from Anthropic API.

        Args:
            response: Streaming response from Anthropic

        Yields:
            Text content from stream
        """
        try:
            async for chunk in response:
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content[0].text
                await asyncio.sleep(0)  # Yield control

        except Exception as e:
            logger.error("Error in stream processing: %s", str(e))
            yield ""

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.client = None
