"""Container-side ingest behavior tests."""

import json
import logging
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from revit_standards_ssot.ingest import ingest_file
from revit_standards_ssot.models import (
    Base,
    FIRM_STANDARD_DATA_TYPES,
    RAW_REVIT_DATA_TYPES,
    RawSharedParameter,
    SharedParameterRecord,
)

INGEST_LOGGER = "revit_standards_ssot.ingest"

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


def test_known_data_type_produces_no_unknown_warning(session, tmp_path, caplog):
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Wall Height", "data_type": "Length"}])

    with caplog.at_level(logging.WARNING, logger=INGEST_LOGGER):
        ingest_file(raw_file, session)

    unknown_warnings = [r for r in caplog.records if "RAW_REVIT_DATA_TYPES" in r.message]
    assert unknown_warnings == []


def test_yes_no_is_not_an_unknown_data_type(session, tmp_path, caplog):
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Is Structural", "data_type": "Yes/No"}])

    with caplog.at_level(logging.WARNING, logger=INGEST_LOGGER):
        counts = ingest_file(raw_file, session)

    assert counts == {"inserted": 1, "updated": 0, "rejected": 0}
    unknown_warnings = [r for r in caplog.records if "RAW_REVIT_DATA_TYPES" in r.message]
    assert unknown_warnings == []


def test_unknown_data_type_is_accepted_not_rejected(session, tmp_path):
    # "Family type: Casework" is intentionally deferred from RAW_REVIT_DATA_TYPES.
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Screen Type", "data_type": "Family type: Casework"}])

    counts = ingest_file(raw_file, session)

    assert counts == {"inserted": 1, "updated": 0, "rejected": 0}
    record = session.get(SharedParameterRecord, GUID_A)
    assert record is not None
    assert record.data_type == "Family type: Casework"


def test_unknown_data_type_produces_warning(session, tmp_path, caplog):
    # "Family type: Casework" is intentionally deferred from RAW_REVIT_DATA_TYPES.
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Screen Type", "data_type": "Family type: Casework"}])

    with caplog.at_level(logging.WARNING, logger=INGEST_LOGGER):
        ingest_file(raw_file, session)

    unknown_warnings = [r for r in caplog.records if "RAW_REVIT_DATA_TYPES" in r.message]
    assert len(unknown_warnings) == 1
    assert "Family type: Casework" in unknown_warnings[0].message
    assert "Screen Type" in unknown_warnings[0].message


def test_unknown_data_type_warning_includes_count_and_samples(session, tmp_path, caplog):
    # "Reinforcement Length" is intentionally deferred from RAW_REVIT_DATA_TYPES.
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [
        {"guid": GUID_A, "name": "Bar Diameter", "data_type": "Reinforcement Length"},
        {"guid": GUID_B, "name": "Hook Length", "data_type": "Reinforcement Length"},
    ])

    with caplog.at_level(logging.WARNING, logger=INGEST_LOGGER):
        counts = ingest_file(raw_file, session)

    assert counts == {"inserted": 2, "updated": 0, "rejected": 0}
    unknown_warnings = [r for r in caplog.records if "RAW_REVIT_DATA_TYPES" in r.message]
    assert len(unknown_warnings) == 1
    msg = unknown_warnings[0].message
    assert "Reinforcement Length" in msg
    assert "2" in msg


def test_newly_added_raw_revit_type_does_not_warn(session, tmp_path, caplog):
    # Temperature and Air Flow were added to RAW_REVIT_DATA_TYPES in the vocabulary split.
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [
        {"guid": GUID_A, "name": "Supply Temp", "data_type": "Temperature"},
        {"guid": GUID_B, "name": "Supply Air", "data_type": "Air Flow"},
    ])

    with caplog.at_level(logging.WARNING, logger=INGEST_LOGGER):
        counts = ingest_file(raw_file, session)

    assert counts == {"inserted": 2, "updated": 0, "rejected": 0}
    unknown_warnings = [r for r in caplog.records if "RAW_REVIT_DATA_TYPES" in r.message]
    assert unknown_warnings == []


def test_family_type_variants_still_warn(session, tmp_path, caplog):
    # "Family type: <X>" variants are intentionally deferred from RAW_REVIT_DATA_TYPES.
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [
        {"guid": GUID_A, "name": "Screen Type", "data_type": "Family type: Casework"},
    ])

    with caplog.at_level(logging.WARNING, logger=INGEST_LOGGER):
        counts = ingest_file(raw_file, session)

    assert counts == {"inserted": 1, "updated": 0, "rejected": 0}
    unknown_warnings = [r for r in caplog.records if "RAW_REVIT_DATA_TYPES" in r.message]
    assert len(unknown_warnings) == 1
    assert "Family type: Casework" in unknown_warnings[0].message


def test_firm_standard_data_types_not_used_to_reject_raw_ingest(session, tmp_path):
    # A data_type absent from FIRM_STANDARD_DATA_TYPES must not cause rejection.
    non_standard_type = "Temperature"
    assert non_standard_type not in FIRM_STANDARD_DATA_TYPES
    assert non_standard_type in RAW_REVIT_DATA_TYPES

    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Room Temp", "data_type": non_standard_type}])

    counts = ingest_file(raw_file, session)

    assert counts["rejected"] == 0
    assert counts["inserted"] == 1


def test_standard_data_type_is_optional_on_raw_record(session, tmp_path):
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Wall Height", "data_type": "Length"}])

    ingest_file(raw_file, session)

    record = session.get(SharedParameterRecord, GUID_A)
    assert record.standard_data_type is None


def test_ingest_succeeds_without_curation_fields_in_raw_data(session, tmp_path):
    raw_file = tmp_path / "test.json"
    _write_raw(raw_file, [{"guid": GUID_A, "name": "Wall Height", "data_type": "Length"}])

    counts = ingest_file(raw_file, session)

    record = session.get(SharedParameterRecord, GUID_A)
    assert counts["inserted"] == 1
    assert record.curation_note is None
    assert record.standard_data_type is None


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
