from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class RequestMetadata:
    """Metadata for request tracking."""
    request_id: str
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class RateLimits:
    """Rate limiting configuration."""
    requests_per_minute: int
    tokens_per_minute: int

    def __post_init__(self):
        """Validate and convert rate limits to integers."""
        self.requests_per_minute = int(self.requests_per_minute)
        self.tokens_per_minute = int(self.tokens_per_minute)

@dataclass
class APIResponse:
    """Structured API response."""
    content: str
    request_id: str
    metadata: Optional[Dict[str, Any]] = None
    success: bool = True
    error: Optional[str] = None
    @dataclass
    class APIResponse:
        """Structured API response."""
        content: str
        request_id: str
        success: bool = True
        error: Optional[str] = None
        metadata: Optional[Dict[str, Any]] = None

        def __post_init__(self):
            """Validate response fields."""
            if not isinstance(self.content, str):
                raise ValueError("Content must be a string")
            if not isinstance(self.request_id, str):
                raise ValueError("Request ID must be a string")
            if not isinstance(self.success, bool):
                raise ValueError("Success must be a boolean")
            if self.error is not None and not isinstance(self.error, str):
                raise ValueError("Error must be a string or None")
            if self.metadata is not None and not isinstance(self.metadata, dict):
                raise ValueError("Metadata must be a dict or None")
