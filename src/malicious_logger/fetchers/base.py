from __future__ import annotations

import logging
from http import HTTPStatus

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

from malicious_logger.config import settings
from malicious_logger.exceptions import FetchError, RateLimitedError

logger = logging.getLogger(__name__)

# we define what's worth retrying and what's not
_RETRYABLE = (
    httpx.ConnectError,
    httpx.TimeoutException,
    httpx.RemoteProtocolError,
)

RETRYABLE_STATUS_CODES = {
    HTTPStatus.TOO_MANY_REQUESTS,       
    HTTPStatus.INTERNAL_SERVER_ERROR,  
    HTTPStatus.BAD_GATEWAY,             
    HTTPStatus.SERVICE_UNAVAILABLE,    
    HTTPStatus.GATEWAY_TIMEOUT,        
}

# duck vs goose typing here?? not sure yet
def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, _RETRYABLE):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS_CODES
    return False


def build_client() -> httpx.Client:
    return httpx.Client(
        timeout=settings.request_timeout,
        follow_redirects=True,
        headers={"User-Agent": "ioc-ingestor/1.0"},
    )


class BaseFetcher:
    _registry: dict[str, type[BaseFetcher]] = {}

    source_name: str
    source_url: str

    def __init_subclass__(cls, source_name: str, **kw: object) -> None:
        super().__init_subclass__(**kw)
        BaseFetcher._registry[source_name] = cls
        cls.source_name = source_name

    def fetch(self, client: httpx.Client) -> bytes:
        @retry(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(settings.max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            reraise=False,
        )
        def _do_fetch() -> bytes:
            try:
                response = client.get(self.source_url)
                response.raise_for_status()
                return response.content
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    raise RateLimitedError(self.source_name, "rate limited")
                if exc.response.status_code in RETRYABLE_STATUS_CODES:
                    raise
                # nonretryable
                raise FetchError(
                    self.source_name,
                    f"HTTP {exc.response.status_code}: {exc.response.reason_phrase}",
                ) from exc
            except _RETRYABLE as exc:
                raise FetchError(self.source_name, str(exc)) from exc

        try:
            return _do_fetch()
        except (FetchError, RateLimitedError):
            raise
        except Exception as exc:
            raise FetchError(self.source_name, f"failed after retries: {exc}") from exc
