# tkr_bias_stories/tkr_utils/helper_anthropic/processor.py
import asyncio
import json
import time
from typing import List, Dict, Any, Optional
from tkr_utils.helper_anthropic.client import AnthropicBatchClient
from tkr_utils.helper_anthropic.models import RateLimits
from tkr_utils import setup_logging, logs_and_exceptions

logger = setup_logging(__name__)

class RequestProcessor:
    """Handles the processing of API requests with rate limiting."""

    def __init__(self, client: AnthropicBatchClient, rate_limits: RateLimits):
        """Initialize the request processor."""
        self.client = client
        self.rate_limits = rate_limits
        self.last_request_time = time.time()
        self.requests_made = 0
        self.tokens_used = 0

    async def process_batch(
        self,
        messages: List[Dict[str, Any]],
        output_file: Optional[str] = None
    ) -> List[str]:
        """
        Process a batch of message requests.

        Args:
            messages: List of message dictionaries to process
            output_file: Optional file to save responses to

        Returns:
            List of response strings from the API
        """
        logger.info("Starting batch processing of %d messages", len(messages))

        responses = []
        for message in messages:
            await self.throttle_requests()
            response = self.client.helper.send_message([message])
            responses.append(response)

            if output_file:
                self.save_response(output_file, response)

            logger.debug("Processed message %d/%d", len(responses), len(messages))

        logger.info("Completed batch processing")
        return responses

    async def throttle_requests(self) -> None:
        """Throttle requests to adhere to rate limits."""
        current_time = time.time()
        elapsed_time = current_time - self.last_request_time

        if self.requests_made >= self.rate_limits.requests_per_minute:
            wait_time = 60 - elapsed_time
            if wait_time > 0:
                logger.info("Rate limit reached. Waiting for %.2f seconds.", wait_time)
                await asyncio.sleep(wait_time)
            self.requests_made = 0
            self.last_request_time = time.time()

        if self.tokens_used >= self.rate_limits.tokens_per_minute:
            wait_time = 60 - elapsed_time
            if wait_time > 0:
                logger.info("Token limit reached. Waiting for %.2f seconds.", wait_time)
                await asyncio.sleep(wait_time)
            self.tokens_used = 0
            self.last_request_time = time.time()

        self.requests_made += 1

    def save_response(self, output_file: str, response: str) -> None:
        """Save the response to the output file."""
        with open(output_file, 'a') as file:
            file.write(json.dumps({"response": response}) + "\n")
        logger.debug("Response saved to %s", output_file)
