class FetchError(Exception):
    """raised when a feed cannot be fetched after all retries."""

    def __init__(self, source_name: str, reason: str) -> None:
        self.source_name = source_name
        self.reason = reason
        super().__init__(f"[{source_name}] {reason}")


class RateLimitedError(FetchError):
    """raised when a source returns HTTP 429."""
