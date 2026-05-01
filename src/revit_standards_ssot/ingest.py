"""Ingest raw JSON exports into the SQLite database.

Raw files under exports/raw/ are never modified. Records are upserted by GUID.
New records receive status='raw'. Existing status is never downgraded.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError
from sqlalchemy.orm import Session

from revit_standards_ssot.models import (
    RAW_REVIT_DATA_TYPES,
    RawSharedParameter,
    SharedParameter,
    SharedParameterRecord,
)

logger = logging.getLogger(__name__)


def ingest_file(path: Path, session: Session) -> dict[str, int]:
    """Parse one raw JSON export file and upsert records into the DB.

    Returns a dict with counts: {"inserted": N, "updated": N, "rejected": N}.
    """
    counts = {"inserted": 0, "updated": 0, "rejected": 0}
    unknown_dtype_counts: dict[str, int] = {}
    unknown_dtype_samples: dict[str, list[str]] = {}

    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError(f"Expected a JSON array in {path}, got {type(raw).__name__}")

    for item in raw:
        try:
            raw_param = RawSharedParameter.model_validate(item)
            param = SharedParameter.model_validate({
                **raw_param.model_dump(),
                "source_file": path.name,
            })
        except ValidationError as exc:
            logger.warning("Rejected record from %s: %s", path.name, exc)
            counts["rejected"] += 1
            continue

        if param.data_type not in RAW_REVIT_DATA_TYPES:
            unknown_dtype_counts[param.data_type] = unknown_dtype_counts.get(param.data_type, 0) + 1
            samples = unknown_dtype_samples.setdefault(param.data_type, [])
            if len(samples) < 3:
                samples.append(param.name)

        existing = session.get(SharedParameterRecord, param.guid)
        now = datetime.now(UTC)

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

    for dtype in sorted(unknown_dtype_counts, key=lambda d: -unknown_dtype_counts[d]):
        logger.warning(
            "data_type not in RAW_REVIT_DATA_TYPES: %r — %d record(s), e.g. %s",
            dtype,
            unknown_dtype_counts[dtype],
            ", ".join(repr(n) for n in unknown_dtype_samples[dtype]),
        )

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
