"""YAML export tests — only approved records must appear in output."""

import yaml
import pytest
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from revit_standards_ssot.models import Base, SharedParameterRecord
from revit_standards_ssot.export_yaml import export_yaml

GUID_APPROVED = "cccccccc-cccc-cccc-cccc-cccccccccccc"
GUID_RAW = "dddddddd-dddd-dddd-dddd-dddddddddddd"
GUID_DEPRECATED = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    with Session() as s:
        yield s


def _add_record(session, guid: str, name: str, status: str) -> None:
    now = datetime.now(timezone.utc)
    session.add(SharedParameterRecord(
        guid=guid,
        name=name,
        data_type="Text",
        status=status,
        source_file="test.json",
        created_at=now,
        updated_at=now,
    ))
    session.commit()


def test_only_approved_in_yaml(session, tmp_path):
    _add_record(session, GUID_APPROVED, "Approved Param", "approved")
    _add_record(session, GUID_RAW, "Raw Param", "raw")
    _add_record(session, GUID_DEPRECATED, "Deprecated Param", "deprecated")

    out = tmp_path / "params.yaml"
    count = export_yaml(session, out)

    assert count == 1
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["guid"] == GUID_APPROVED


def test_empty_yaml_when_no_approved(session, tmp_path):
    _add_record(session, GUID_RAW, "Raw Only", "raw")

    out = tmp_path / "params.yaml"
    count = export_yaml(session, out)

    assert count == 0
    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    assert data is None or data == []


def test_yaml_sorted_by_guid(session, tmp_path):
    _add_record(session, "ffffffff-ffff-ffff-ffff-ffffffffffff", "Z Param", "approved")
    _add_record(session, "00000000-0000-0000-0000-000000000000", "A Param", "approved")

    out = tmp_path / "params.yaml"
    export_yaml(session, out)

    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    guids = [r["guid"] for r in data]
    assert guids == sorted(guids)


def test_yaml_contains_expected_fields(session, tmp_path):
    _add_record(session, GUID_APPROVED, "Field Test Param", "approved")

    out = tmp_path / "params.yaml"
    export_yaml(session, out)

    data = yaml.safe_load(out.read_text(encoding="utf-8"))
    record = data[0]
    for field in ("guid", "name", "data_type", "group", "description"):
        assert field in record
