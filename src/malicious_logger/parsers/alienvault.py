from __future__ import annotations

import logging
from collections.abc import Iterator

from pydantic import ValidationError

from malicious_logger.parsers.models import AlienVaultRecord

logger = logging.getLogger(__name__)

_FIELDS = ("address", "reliability", "risk", "threat_type", "country", "city", "coords", "_count")


def parse(raw: bytes) -> Iterator[AlienVaultRecord]:
    for line in raw.decode("utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("#")
        if len(parts) < len(_FIELDS):
            logger.warning("alienvault: skipping short line: %s", line[:60])
            continue
        row = dict(zip(_FIELDS, parts))
        try:
            yield AlienVaultRecord.model_validate(row)
        except ValidationError as exc:
            logger.warning("alienvault: skipping malformed row %s — %s", row.get("address"), exc)
