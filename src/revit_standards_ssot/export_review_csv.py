"""Export all shared parameter records to CSV for human review.

All statuses are included. Reviewers update status values in the DB directly.
This script does not write back to exports/raw/.
"""

from __future__ import annotations

import csv
from pathlib import Path

from sqlalchemy.orm import Session

from revit_standards_ssot.models import SharedParameterRecord

_COLUMNS = ["guid", "name", "data_type", "group", "description", "status", "source_file",
            "created_at", "updated_at"]


def export_review_csv(session: Session, output_path: Path) -> int:
    """Write all parameter records to output_path as CSV. Returns row count."""
    records = (
        session.query(SharedParameterRecord)
        .order_by(SharedParameterRecord.status, SharedParameterRecord.name)
        .all()
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_COLUMNS)
        writer.writeheader()
        for r in records:
            writer.writerow({col: getattr(r, col) for col in _COLUMNS})

    return len(records)
