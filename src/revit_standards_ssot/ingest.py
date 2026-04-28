"""Ingest raw JSON exports into the SQLite database.

Raw files under exports/raw/ are never modified. Records are upserted by GUID.
New records receive status='raw'. Existing status is never downgraded.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from revit_standards_ssot.models import SharedParameter, SharedParameterRecord

logger = logging.getLogger(__name__)


def ingest_file(path: Path, session: Session) -> dict[str, int]:
    """Parse one raw JSON export file and upsert records into the DB.

    Returns a dict with counts: {"inserted": N, "updated": N, "rejected": N}.
    """
    counts = {"inserted": 0, "updated": 0, "rejected": 0}

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in {path}, got {type(raw).__name__}")

    for item in raw:
        item.setdefault("source_file", path.name)
        try:
            param = SharedParameter.model_validate(item)
        except ValidationError as exc:
            logger.warning("Rejected record from %s: %s", path.name, exc)
            counts["rejected"] += 1
            continue

        existing = session.get(SharedParameterRecord, param.guid)
        now = datetime.now(timezone.utc)

        if existing is None:
            record = SharedParameterRecord(
                guid=param.guid,
                name=param.name,
                data_type=param.data_type,
                group=param.group,
                description=param.description,
                status="raw",
                source_file=param.source_file,
                created_at=now,
                updated_at=now,
            )
            session.add(record)
            counts["inserted"] += 1
            logger.info("Inserted %s (%s)", param.name, param.guid)
        else:
            existing.name = param.name
            existing.data_type = param.data_type
            existing.group = param.group
            existing.description = param.description
            existing.source_file = param.source_file
            existing.updated_at = now
            counts["updated"] += 1
            logger.info("Updated %s (%s)", param.name, param.guid)

    session.commit()
    return counts


def ingest_directory(raw_dir: Path, session: Session) -> dict[str, int]:
    """Ingest all *.json files found in raw_dir."""
    totals = {"inserted": 0, "updated": 0, "rejected": 0}
    files = sorted(raw_dir.glob("*.json"))
    if not files:
        logger.warning("No JSON files found in %s", raw_dir)
    for f in files:
        result = ingest_file(f, session)
        for k in totals:
            totals[k] += result[k]
    return totals
