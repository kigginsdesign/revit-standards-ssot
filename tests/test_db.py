"""SQLAlchemy insert / update / query tests using an in-memory SQLite database."""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from revit_standards_ssot.models import Base, SharedParameterRecord

GUID_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
GUID_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        yield s


def _make_record(guid: str, name: str = "Test Param", status: str = "raw") -> SharedParameterRecord:
    now = datetime.now(timezone.utc)
    return SharedParameterRecord(
        guid=guid,
        name=name,
        data_type="Text",
        status=status,
        source_file="test.json",
        created_at=now,
        updated_at=now,
    )


def test_insert_and_query(session):
    session.add(_make_record(GUID_A))
    session.commit()

    result = session.get(SharedParameterRecord, GUID_A)
    assert result is not None
    assert result.name == "Test Param"
    assert result.status == "raw"


def test_upsert_updates_name(session):
    session.add(_make_record(GUID_A, name="Original"))
    session.commit()

    record = session.get(SharedParameterRecord, GUID_A)
    record.name = "Updated"
    session.commit()

    refreshed = session.get(SharedParameterRecord, GUID_A)
    assert refreshed.name == "Updated"


def test_multiple_records(session):
    session.add(_make_record(GUID_A))
    session.add(_make_record(GUID_B, name="Other Param"))
    session.commit()

    all_records = session.query(SharedParameterRecord).all()
    assert len(all_records) == 2


def test_status_filter(session):
    session.add(_make_record(GUID_A, status="approved"))
    session.add(_make_record(GUID_B, status="raw"))
    session.commit()

    approved = (
        session.query(SharedParameterRecord)
        .filter(SharedParameterRecord.status == "approved")
        .all()
    )
    assert len(approved) == 1
    assert approved[0].guid == GUID_A


def test_guid_is_primary_key(session):
    session.add(_make_record(GUID_A))
    session.commit()

    duplicate = _make_record(GUID_A, name="Duplicate")
    session.merge(duplicate)
    session.commit()

    all_records = session.query(SharedParameterRecord).all()
    assert len(all_records) == 1


def test_new_fields_default_null_on_insert(session):
    session.add(_make_record(GUID_A))
    session.commit()

    r = session.get(SharedParameterRecord, GUID_A)
    assert r.curation_note is None
    assert r.standard_data_type is None


def test_new_fields_roundtrip(session):
    now = datetime.now(timezone.utc)
    record = SharedParameterRecord(
        guid=GUID_A,
        name="Test Param",
        data_type="Yes/No",
        status="deprecated",
        source_file="test.json",
        curation_note="Inherited from vendor",
        standard_data_type="YesNo",
        created_at=now,
        updated_at=now,
    )
    session.add(record)
    session.commit()

    r = session.get(SharedParameterRecord, GUID_A)
    assert r.curation_note == "Inherited from vendor"
    assert r.standard_data_type == "YesNo"
    assert r.data_type == "Yes/No"


def test_deprecated_status_with_curation_note(session):
    now = datetime.now(timezone.utc)
    session.add(SharedParameterRecord(
        guid=GUID_A,
        name="Test Param",
        data_type="Text",
        status="raw",
        source_file="test.json",
        created_at=now,
        updated_at=now,
    ))
    session.commit()

    r = session.get(SharedParameterRecord, GUID_A)
    r.status = "deprecated"
    r.curation_note = "Not a firm standard"
    session.commit()

    refreshed = session.get(SharedParameterRecord, GUID_A)
    assert refreshed.status == "deprecated"
    assert refreshed.curation_note == "Not a firm standard"
    assert refreshed.standard_data_type is None
