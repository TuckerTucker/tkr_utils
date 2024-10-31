# tkr_bias_stories/tkr_utils/helper_anthropic/async_manager.py

import asyncio
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from tkr_utils import setup_logging, logs_and_exceptions
from .models import RateLimits

logger = setup_logging(__file__)

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker pattern."""
    failure_threshold: int = 5
    reset_timeout: float = 60.0  # seconds
    half_open_timeout: float = 5.0  # seconds

class CircuitBreaker:
    """Implements circuit breaker pattern for API requests."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failures = 0
        self.last_failure_time = 0
        self.state = "closed"  # closed, open, half-open
        self._lock = asyncio.Lock()

    async def record_failure(self):
        """Record a failure and potentially open the circuit."""
        async with self._lock:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.config.failure_threshold:
                self.state = "open"
                logger.warning("Circuit breaker opened due to %d failures", self.failures)

    async def can_execute(self) -> bool:
        """Check if a request can be executed based on circuit state."""
        async with self._lock:
            if self.state == "closed":
                return True

            if self.state == "open":
                if time.time() - self.last_failure_time > self.config.reset_timeout:
                    self.state = "half-open"
                    return True
                return False

            # Half-open state
            if time.time() - self.last_failure_time > self.config.half_open_timeout:
                return True
            return False

    async def record_success(self):
        """Record a successful request and potentially close the circuit."""
        async with self._lock:
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
                logger.info("Circuit breaker closed after successful request")

class AsyncRequestManager:
    """Manages async request orchestration with rate limiting and circuit breaking."""

    def __init__(
        self,
        rate_limits: RateLimits,
        max_concurrent: int = 5,
        chunk_size: int = 10
    ):
        """Initialize the async request manager.

        Args:
            rate_limits: Rate limiting configuration
            max_concurrent: Maximum number of concurrent requests
            chunk_size: Size of request chunks for batch processing
        """
        self.rate_limits = rate_limits
        self._max_concurrent = max_concurrent
        self.chunk_size = chunk_size
        self.circuit_breaker = CircuitBreaker(CircuitBreakerConfig())

        # Initialize but don't create semaphore yet
        self._semaphore = None

        # Rate limiting state
        self.requests_made = 0
        self.tokens_used = 0
        self.last_reset = time.time()
        self._rate_limit_lock = asyncio.Lock()

        # Track active permits
        self._active_permits = 0
        self._permits_lock = asyncio.Lock()

        logger.info(
            "AsyncRequestManager initialized with max_concurrent=%d, chunk_size=%d",
            max_concurrent,
            chunk_size
        )

    @property
    def semaphore(self) -> asyncio.Semaphore:
        """Lazy initialization of semaphore."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self._max_concurrent)
        return self._semaphore

    def chunk_requests(self, requests: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Split requests into chunks for processing."""
        return [
            requests[i:i + self.chunk_size]
            for i in range(0, len(requests), self.chunk_size)
        ]

    async def check_rate_limits(self, tokens: int = 0) -> bool:
        """Check if request can proceed under rate limits."""
        async with self._rate_limit_lock:
            current_time = time.time()
            elapsed = current_time - self.last_reset

            # Reset counters if minute has elapsed
            if elapsed >= 60:
                self.requests_made = 0
                self.tokens_used = 0
                self.last_reset = current_time
                return True

            # Check limits
            if (self.requests_made >= self.rate_limits.requests_per_minute or
                self.tokens_used + tokens >= self.rate_limits.tokens_per_minute):
                return False

            # Update counters
            self.requests_made += 1
            self.tokens_used += tokens
            return True

    async def acquire_permit(self) -> bool:
        """Acquire permission to make a request checking all constraints."""
        if not await self.circuit_breaker.can_execute():
            logger.warning("Circuit breaker preventing request execution")
            return False

        try:
            await self.semaphore.acquire()
            async with self._permits_lock:
                self._active_permits += 1

            if await self.check_rate_limits():
                return True

            # Release if rate limits exceeded
            await self.release_permit()
            return False

        except Exception as e:
            logger.error("Error acquiring request permit: %s", str(e))
            await self.release_permit()
            return False

    async def release_permit(self):
        """Safely release a permit."""
        try:
            if self._semaphore is not None:
                self._semaphore.release()
                async with self._permits_lock:
                    if self._active_permits > 0:
                        self._active_permits -= 1
        except ValueError:  # Handle case where release called without acquire
            logger.warning("Attempted to release an unacquired permit")
        except Exception as e:
            logger.error("Error releasing permit: %s", str(e))

    async def cleanup(self):
        """Clean up resources and ensure all permits are released."""
        try:
            # Release any remaining permits
            async with self._permits_lock:
                while self._active_permits > 0:
                    await self.release_permit()

            # Clear the semaphore
            self._semaphore = None
            logger.info("AsyncRequestManager cleanup completed")
        except Exception as e:
            logger.error("Error during AsyncRequestManager cleanup: %s", str(e))

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.cleanup()

    async def record_success(self) -> None:
        """Record a successful API request."""
        try:
            await self.circuit_breaker.record_success()
            logger.debug("Successfully recorded API request success")
        except Exception as e:
            logger.error("Error recording request success: %s", str(e))

    async def record_failure(self) -> None:
        """Record a failed API request."""
        try:
            await self.circuit_breaker.record_failure()
            logger.warning("Recorded API request failure")
        except Exception as e:
            logger.error("Error recording request failure: %s", str(e))
