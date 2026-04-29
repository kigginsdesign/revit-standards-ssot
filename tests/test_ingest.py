"""Container-side ingest behavior tests."""

import json
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from revit_standards_ssot.ingest import ingest_file
from revit_standards_ssot.models import Base, RawSharedParameter, SharedParameterRecord

GUID_A = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
GUID_B = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        yield s


def _write_raw(path, records):
    path.write_text(json.dumps(records), encoding="utf-8")


def test_raw_record_without_source_file_validates():
    param = RawSharedParameter.model_validate({
        "guid": GUID_A,
        "name": "Wall Height",
        "data_type": "Length",
        "group": "Dimensions",
        "description": "Nominal wall height",
    })

    assert param.guid == GUID_A
    assert param.name == "Wall Height"


@pytest.mark.parametrize(
    "missing_field",
    ["guid", "name", "data_type"],
)
def test_raw_record_missing_required_field_is_rejected(missing_field):
    record = {
        "guid": GUID_A,
        "name": "Wall Height",
        "data_type": "Length",
    }
    record.pop(missing_field)

    with pytest.raises(ValidationError):
        RawSharedParameter.model_validate(record)


def test_ingest_assigns_source_file_from_input_filename(session, tmp_path):
    raw_file = tmp_path / "20260429_120000.json"
    _write_raw(raw_file, [{
        "guid": GUID_A,
        "name": "Wall Height",
        "data_type": "Length",
    }])

    counts = ingest_file(raw_file, session)

    record = session.get(SharedParameterRecord, GUID_A)
    assert counts == {"inserted": 1, "updated": 0, "rejected": 0}
    assert record.source_file == raw_file.name


def test_ingest_does_not_downgrade_existing_status_on_upsert(session, tmp_path):
    now = datetime.now(UTC)
    session.add(SharedParameterRecord(
        guid=GUID_B,
        name="Original",
        data_type="Text",
        status="approved",
        source_file="original.json",
        created_at=now,
        updated_at=now,
    ))
    session.commit()

    raw_file = tmp_path / "20260429_130000.json"
    _write_raw(raw_file, [{
        "guid": GUID_B,
        "name": "Updated",
        "data_type": "Number",
    }])

    counts = ingest_file(raw_file, session)

    record = session.get(SharedParameterRecord, GUID_B)
    assert counts == {"inserted": 0, "updated": 1, "rejected": 0}
    assert record.name == "Updated"
    assert record.status == "approved"
    assert record.source_file == raw_file.name
