# tkr_bias_stories/tkr_utils/helper_anthropic/processor.py

import asyncio
from typing import List, Dict, Any, Optional
from tkr_utils import setup_logging, logs_and_exceptions
from tkr_utils.config import MAX_REQUESTS_PER_MINUTE, MAX_TOKENS_PER_MINUTE
from .models import RateLimits, APIResponse
from .client import AnthropicHelper
from .async_manager import AsyncRequestManager

logger = setup_logging(__file__)

class RequestProcessor:
    """Handles processing of API requests with concurrent processing and rate limiting."""

    def __init__(
        self,
        client: AnthropicHelper,
        rate_limits: Optional[RateLimits] = None,
        max_concurrent: int = 5,
        chunk_size: int = 10
    ):
        """Initialize the request processor.

        Args:
            client: AnthropicHelper instance
            rate_limits: Optional RateLimits configuration
            max_concurrent: Maximum number of concurrent requests
            chunk_size: Size of request chunks for batch processing
        """
        self.client = client

        # Configure rate limits
        if rate_limits:
            logger.info(
                "Using provided rate limits: %d requests/min, %d tokens/min",
                rate_limits.requests_per_minute,
                rate_limits.tokens_per_minute
            )
            self.rate_limits = rate_limits
        else:
            logger.info(
                "Using default rate limits: %d requests/min, %d tokens/min",
                MAX_REQUESTS_PER_MINUTE,
                MAX_TOKENS_PER_MINUTE
            )
            self.rate_limits = RateLimits(
                requests_per_minute=MAX_REQUESTS_PER_MINUTE,
                tokens_per_minute=MAX_TOKENS_PER_MINUTE
            )

        # Initialize request manager
        self.request_manager = AsyncRequestManager(
            rate_limits=self.rate_limits,
            max_concurrent=max_concurrent,
            chunk_size=chunk_size
        )

        # Processing statistics
        self.stats = {
            "processed": 0,
            "failed": 0,
            "total_chunks": 0,
            "active_requests": 0
        }
        self._stats_lock = asyncio.Lock()

    async def _update_stats(self, **kwargs: Dict[str, int]) -> None:
        """Thread-safe update of processing statistics."""
        async with self._stats_lock:
            for key, value in kwargs.items():
                if key in self.stats:
                    self.stats[key] += value

    async def process_chunk(
        self,
        chunk: List[Dict[str, Any]]
    ) -> List[APIResponse]:
        """Process a chunk of requests concurrently.

        Args:
            chunk: List of request dictionaries

        Returns:
            List of APIResponse objects
        """
        responses = []
        tasks = []

        async with asyncio.TaskGroup() as tg:
            for request in chunk:
                if await self.request_manager.acquire_permit():
                    task = tg.create_task(self._process_single_request(request))
                    tasks.append(task)
                else:
                    logger.warning("Failed to acquire permit for request")
                    responses.append(
                        APIResponse(
                            content="",
                            request_id="",
                            success=False,
                            error="Failed to acquire request permit"
                        )
                    )

        for task in tasks:
            try:
                response = await task
                responses.append(response)

                if response.success:
                    await self._update_stats(processed=1)
                else:
                    await self._update_stats(failed=1)

            except Exception as e:
                logger.error("Task error in chunk processing: %s", str(e))
                await self._update_stats(failed=1)
                responses.append(
                    APIResponse(
                        content="",
                        request_id="",
                        success=False,
                        error=str(e)
                    )
                )

        return responses

    async def _process_single_request(
        self,
        request: Dict[str, Any]
    ) -> APIResponse:
        """Process a single request with error handling and rate limiting.

        Args:
            request: Request dictionary containing role and content

        Returns:
            APIResponse object
        """
        try:
            await self._update_stats(active_requests=1)

            # Format request for AnthropicHelper
            messages = [{"role": "user", "content": request["content"]}]

            response = await self.client.send_message(
                messages=messages,
                temperature=request.get("temperature", 0.0),
                max_tokens=request.get("max_tokens", 1024)
            )

            await self.request_manager.record_success()
            return response

        except Exception as e:
            logger.error("Error processing single request: %s", str(e))
            await self.request_manager.record_failure()
            return APIResponse(
                content="",
                request_id="",
                success=False,
                error=str(e)
            )
        finally:
            await self._update_stats(active_requests=-1)
            await self.request_manager.release_permit()

    async def process_batch(
        self,
        requests: List[Dict[str, Any]]
    ) -> List[APIResponse]:
        """Process a batch of requests with chunking and concurrent execution.

        Args:
            requests: List of request dictionaries

        Returns:
            List of APIResponse objects
        """
        logger.info("Starting batch processing of %d requests", len(requests))

        # Reset stats
        self.stats = {
            "processed": 0,
            "failed": 0,
            "total_chunks": 0,
            "active_requests": 0
        }

        # Chunk requests
        chunks = self.request_manager.chunk_requests(requests)
        await self._update_stats(total_chunks=len(chunks))

        all_responses = []

        try:
            async with self.request_manager:
                for i, chunk in enumerate(chunks, 1):
                    logger.info("Processing chunk %d/%d", i, len(chunks))

                    try:
                        chunk_responses = await self.process_chunk(chunk)
                        all_responses.extend(chunk_responses)

                        # Add delay between chunks if needed
                        if i < len(chunks):
                            await asyncio.sleep(0.1)

                    except Exception as e:
                        logger.error("Error processing chunk %d: %s", i, str(e))
                        # Add failed responses for the chunk
                        all_responses.extend([
                            APIResponse(
                                content="",
                                request_id="",
                                success=False,
                                error=f"Chunk {i} failed: {str(e)}"
                            ) for _ in chunk
                        ])
                        await self._update_stats(failed=len(chunk))

        except Exception as e:
            logger.error("Batch processing error: %s", str(e))
        finally:
            # Log completion status
            logger.info(
                "Batch processing completed. Processed: %d, Failed: %d, Total Chunks: %d",
                self.stats["processed"],
                self.stats["failed"],
                self.stats["total_chunks"]
            )

        return all_responses

    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        async with self._stats_lock:
            stats_copy = self.stats.copy()
            total = stats_copy["processed"] + stats_copy["failed"]
            stats_copy["success_rate"] = (
                (stats_copy["processed"] / total * 100)
                if total > 0 else 0
            )
            return stats_copy
