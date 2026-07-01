from __future__ import annotations

import csv
import logging
from collections.abc import Iterator

from pydantic import ValidationError

from malicious_logger.parsers.models import URLHausRecord

logger = logging.getLogger(__name__)

_COLUMNS = ("urlhaus_id", "date_added", "url", "url_status", "last_online", "threat", "tags", "urlhaus_link", "reporter")


def parse(raw: bytes) -> Iterator[URLHausRecord]:
    text = raw.decode("utf-8", errors="replace")
    reader = csv.DictReader(
        (line for line in text.splitlines() if not line.startswith("#")),
        fieldnames=_COLUMNS,
    )
    for row in reader:
        try:
            yield URLHausRecord.model_validate(row)
        except ValidationError as exc:
            logger.warning("urlhaus: skipping malformed row %s — %s", row.get("url"), exc)
