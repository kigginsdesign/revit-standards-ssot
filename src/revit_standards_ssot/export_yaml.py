"""Export approved shared parameters to YAML.

Only records with status='approved' are included.
Output is deterministic: records sorted by GUID, keys sorted alphabetically.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from revit_standards_ssot.models import SharedParameterRecord

_OUTPUT_FIELDS = ("guid", "name", "data_type", "group", "description")


def export_yaml(session: Session, output_path: Path) -> int:
    """Write approved parameters to output_path. Returns the count written."""
    records = (
        session.query(SharedParameterRecord)
        .filter(SharedParameterRecord.status == "approved")
        .order_by(SharedParameterRecord.guid)
        .all()
    )

    data = [
        {k: getattr(r, k) for k in sorted(_OUTPUT_FIELDS)}
        for r in records
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, sort_keys=True, default_flow_style=False)

    return len(data)
