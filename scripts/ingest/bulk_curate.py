"""Controlled bulk curation utility — set matching records to status=deprecated.

Default behaviour is dry-run. Pass --apply to commit changes.
--curation-note is required for --apply.

All filtering uses SQLAlchemy ORM queries. Raw SQL strings are not supported.

Usage examples:
  # Dry-run: preview all 'Identity Data' name matches
  uv run python scripts/ingest/bulk_curate.py --name-exact "Identity Data"

  # Apply deprecation with a note
  uv run python scripts/ingest/bulk_curate.py \\
      --name-exact "Identity Data" \\
      --curation-note "Placeholder name — not a real parameter" \\
      --apply

  # Preview by data_type
  uv run python scripts/ingest/bulk_curate.py --data-type-exact "Reinforcement Length"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy.orm import Session

# Allow running from repo root without installing the package.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from revit_standards_ssot.db import make_session_factory
from revit_standards_ssot.models import SharedParameterRecord

_PREVIEW_LIMIT = 20


def _build_query(session: Session, args: argparse.Namespace):
    q = session.query(SharedParameterRecord)
    if args.name_exact:
        q = q.filter(SharedParameterRecord.name == args.name_exact)
    if args.name_contains:
        q = q.filter(SharedParameterRecord.name.ilike(f"%{args.name_contains}%"))
    if args.data_type_exact:
        q = q.filter(SharedParameterRecord.data_type == args.data_type_exact)
    if args.group_exact:
        q = q.filter(SharedParameterRecord.group == args.group_exact)
    if args.source_file:
        q = q.filter(SharedParameterRecord.source_file == args.source_file)
    if args.guid:
        q = q.filter(SharedParameterRecord.guid == args.guid.lower())
    if args.status:
        q = q.filter(SharedParameterRecord.status == args.status)
    return q


def _has_any_filter(args: argparse.Namespace) -> bool:
    return any([
        args.name_exact,
        args.name_contains,
        args.data_type_exact,
        args.group_exact,
        args.source_file,
        args.guid,
        args.status,
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Bulk-deprecate shared parameter records via controlled ORM filters.",
    )
    parser.add_argument("--name-exact", metavar="NAME")
    parser.add_argument("--name-contains", metavar="SUBSTR")
    parser.add_argument("--data-type-exact", metavar="DATA_TYPE")
    parser.add_argument("--group-exact", metavar="GROUP")
    parser.add_argument("--source-file", metavar="FILENAME")
    parser.add_argument("--guid", metavar="GUID")
    parser.add_argument("--status", metavar="STATUS",
                        help="Filter by current status (e.g. 'raw')")
    parser.add_argument("--curation-note", metavar="NOTE",
                        help="Required with --apply; recorded on every changed record.")
    parser.add_argument("--apply", action="store_true",
                        help="Commit changes to the database (default is dry-run).")
    parser.add_argument("--db-path", metavar="PATH",
                        help="Override the default database path.")

    args = parser.parse_args(argv)

    if not _has_any_filter(args):
        print("ERROR: No filter criteria provided. Refusing to run against all records.")
        print("Use at least one of: --name-exact, --name-contains, --data-type-exact,")
        print("  --group-exact, --source-file, --guid, --status")
        return 1

    if args.apply and not (args.curation_note and args.curation_note.strip()):
        print("ERROR: --curation-note is required when using --apply.")
        return 1

    db_path = Path(args.db_path) if args.db_path else None
    session_factory = make_session_factory(db_path)

    with session_factory() as session:
        matched = _build_query(session, args).all()
        count = len(matched)

        print(f"Matched records: {count}")

        if count == 0:
            print("No records matched. Nothing to do.")
            return 0

        preview_rows = matched[:_PREVIEW_LIMIT]
        print(f"\nPreview (up to {_PREVIEW_LIMIT}):")
        print(f"  {'GUID':<38}  {'name':<35}  {'data_type':<22}  {'group':<25}  status")
        print(f"  {'-'*38}  {'-'*35}  {'-'*22}  {'-'*25}  ------")
        for r in preview_rows:
            print(
                f"  {r.guid:<38}  {r.name[:35]:<35}  {r.data_type[:22]:<22}"
                f"  {(r.group or '')[:25]:<25}  {r.status}"
            )
        if count > _PREVIEW_LIMIT:
            print(f"  ... and {count - _PREVIEW_LIMIT} more.")

        if not args.apply:
            print("\nDry-run mode. No changes made. Pass --apply to commit.")
            return 0

        note = args.curation_note.strip()
        changed = 0
        for r in matched:
            r.status = "deprecated"
            r.curation_note = note
            changed += 1

        session.commit()
        print(f"\nApplied: {changed} record(s) set to deprecated.")
        print(f"curation_note: {note!r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
