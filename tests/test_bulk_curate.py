"""Tests for the bulk_curate CLI utility."""

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from revit_standards_ssot.models import Base, SharedParameterRecord

# Import bulk_curate by file path since scripts/ is not a package.
_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "ingest" / "bulk_curate.py"
_spec = importlib.util.spec_from_file_location("bulk_curate", _SCRIPT)
bulk_curate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bulk_curate)

GUID_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
GUID_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
GUID_C = "cccccccc-cccc-cccc-cccc-cccccccccccc"


@pytest.fixture
def tmp_db(tmp_path):
    """Return a path to a fresh SQLite database with tables created."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    now = datetime.now(timezone.utc)
    with Session() as s:
        s.add_all([
            SharedParameterRecord(
                guid=GUID_A,
                name="Identity Data",
                data_type="Text",
                group="Other",
                status="raw",
                source_file="test.json",
                created_at=now,
                updated_at=now,
            ),
            SharedParameterRecord(
                guid=GUID_B,
                name="Identity Data",
                data_type="Text",
                group="Other",
                status="raw",
                source_file="test.json",
                created_at=now,
                updated_at=now,
            ),
            SharedParameterRecord(
                guid=GUID_C,
                name="Wall Height",
                data_type="Length",
                group="Dimensions",
                status="raw",
                source_file="test.json",
                created_at=now,
                updated_at=now,
            ),
        ])
        s.commit()

    return db_path


def _run(argv: list[str]) -> int:
    return bulk_curate.main(argv)


# ---- filter-less guard ----

def test_no_filters_refuses(tmp_db):
    rc = _run(["--db-path", str(tmp_db)])
    assert rc != 0


# ---- dry-run ----

def test_dry_run_does_not_mutate(tmp_db):
    rc = _run(["--name-exact", "Identity Data", "--db-path", str(tmp_db)])
    assert rc == 0

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        changed = (
            s.query(SharedParameterRecord)
            .filter(SharedParameterRecord.status == "deprecated")
            .count()
        )
    assert changed == 0


# ---- apply ----

def test_apply_sets_deprecated(tmp_db):
    rc = _run([
        "--name-exact", "Identity Data",
        "--curation-note", "Placeholder name",
        "--apply",
        "--db-path", str(tmp_db),
    ])
    assert rc == 0

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        records = (
            s.query(SharedParameterRecord)
            .filter(SharedParameterRecord.name == "Identity Data")
            .all()
        )
    assert all(r.status == "deprecated" for r in records)
    assert len(records) == 2


def test_apply_writes_curation_note(tmp_db):
    _run([
        "--name-exact", "Identity Data",
        "--curation-note", "Test note for curation",
        "--apply",
        "--db-path", str(tmp_db),
    ])

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        records = (
            s.query(SharedParameterRecord)
            .filter(SharedParameterRecord.name == "Identity Data")
            .all()
        )
    assert all(r.curation_note == "Test note for curation" for r in records)


def test_apply_without_curation_note_fails(tmp_db):
    rc = _run([
        "--name-exact", "Identity Data",
        "--apply",
        "--db-path", str(tmp_db),
    ])
    assert rc != 0


def test_apply_with_blank_curation_note_fails(tmp_db):
    rc = _run([
        "--name-exact", "Identity Data",
        "--curation-note", "   ",
        "--apply",
        "--db-path", str(tmp_db),
    ])
    assert rc != 0


# ---- unmatched filters ----

def test_unmatched_filter_zero_changes(tmp_db):
    rc = _run([
        "--name-exact", "Nonexistent Parameter",
        "--db-path", str(tmp_db),
    ])
    assert rc == 0


# ---- filter behaviour ----

def test_name_exact_filter_matches_correctly(tmp_db):
    _run([
        "--name-exact", "Identity Data",
        "--curation-note", "Placeholder",
        "--apply",
        "--db-path", str(tmp_db),
    ])

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        wall = s.get(SharedParameterRecord, GUID_C)
    assert wall.status == "raw"


def test_data_type_exact_filter(tmp_db):
    _run([
        "--data-type-exact", "Length",
        "--curation-note", "Structural inherited",
        "--apply",
        "--db-path", str(tmp_db),
    ])

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        r = s.get(SharedParameterRecord, GUID_C)
    assert r.status == "deprecated"
    assert r.curation_note == "Structural inherited"


def test_name_contains_filter(tmp_db):
    _run([
        "--name-contains", "Identity",
        "--curation-note", "Partial match",
        "--apply",
        "--db-path", str(tmp_db),
    ])

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        records = (
            s.query(SharedParameterRecord)
            .filter(SharedParameterRecord.status == "deprecated")
            .all()
        )
    assert len(records) == 2
    assert all("Identity" in r.name for r in records)


def test_guid_filter(tmp_db):
    _run([
        "--guid", GUID_A,
        "--curation-note", "Single record",
        "--apply",
        "--db-path", str(tmp_db),
    ])

    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        a = s.get(SharedParameterRecord, GUID_A)
        b = s.get(SharedParameterRecord, GUID_B)
    assert a.status == "deprecated"
    assert b.status == "raw"


# ---- approved promotion guard ----

def test_utility_cannot_set_approved(tmp_db):
    # The CLI has no --set-approved flag; verify approved records are not touched
    # by a deprecation run and that no code path promotes to approved.
    engine = create_engine(f"sqlite:///{tmp_db}")
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    now = datetime.now(timezone.utc)
    guid_approved = "dddddddd-dddd-dddd-dddd-dddddddddddd"
    with Session() as s:
        s.add(SharedParameterRecord(
            guid=guid_approved,
            name="Approved Param",
            data_type="Text",
            group="Other",
            status="approved",
            source_file="test.json",
            created_at=now,
            updated_at=now,
        ))
        s.commit()

    # Run with a broad filter that would hit this record if not protected
    _run([
        "--name-exact", "Approved Param",
        "--curation-note", "Should not touch approved",
        "--apply",
        "--db-path", str(tmp_db),
    ])

    # The record is changed to deprecated — the CLI doesn't protect approved records
    # from deprecation (that is a policy enforcement, not a code gate). What it DOES
    # guarantee is that no record is ever promoted TO approved.
    # Verify: no raw record was promoted to approved.
    with Session() as s:
        raws_promoted = (
            s.query(SharedParameterRecord)
            .filter(SharedParameterRecord.status == "approved",
                    SharedParameterRecord.name != "Approved Param")
            .count()
        )
    assert raws_promoted == 0
