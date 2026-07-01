from __future__ import annotations

import logging
from collections.abc import Iterator

from pydantic import ValidationError

from malicious_logger.parsers.models import OpenPhishRecord

logger = logging.getLogger(__name__)


def parse(raw: bytes) -> Iterator[OpenPhishRecord]:
    for line in raw.decode("utf-8", errors="replace").splitlines():
        url = line.strip()
        if not url:
            continue
        try:
            yield OpenPhishRecord.model_validate({"url": url})
        except ValidationError as exc:
            logger.warning("openphish: skipping malformed line %s — %s", url[:60], exc)
