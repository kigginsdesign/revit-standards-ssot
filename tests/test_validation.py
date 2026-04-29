"""Pydantic validation tests for shared parameter models."""

import pytest
from pydantic import ValidationError

from revit_standards_ssot.models import RawSharedParameter, SharedParameter

VALID_GUID = "12345678-1234-1234-1234-123456789abc"


def test_valid_parameter():
    p = RawSharedParameter(guid=VALID_GUID, name="Wall Height", data_type="Length")
    assert p.guid == VALID_GUID


def test_guid_normalised_to_lowercase():
    p = RawSharedParameter(guid=VALID_GUID.upper(), name="X", data_type="Text")
    assert p.guid == VALID_GUID.lower()


def test_missing_guid_raises():
    with pytest.raises(ValidationError):
        RawSharedParameter(name="Wall Height", data_type="Length")


def test_missing_name_raises():
    with pytest.raises(ValidationError):
        RawSharedParameter(guid=VALID_GUID, data_type="Length")


def test_missing_data_type_raises():
    with pytest.raises(ValidationError):
        RawSharedParameter(guid=VALID_GUID, name="Wall Height")


def test_invalid_guid_format_raises():
    with pytest.raises(ValidationError):
        RawSharedParameter(guid="not-a-uuid", name="X", data_type="Text")


def test_empty_name_raises():
    with pytest.raises(ValidationError):
        RawSharedParameter(guid=VALID_GUID, name="   ", data_type="Text")


def test_empty_data_type_raises():
    with pytest.raises(ValidationError):
        RawSharedParameter(guid=VALID_GUID, name="X", data_type="")


def test_invalid_status_raises():
    with pytest.raises(ValidationError):
        SharedParameter(
            guid=VALID_GUID,
            name="X",
            data_type="Text",
            source_file="raw.json",
            status="unknown",
        )


def test_optional_fields_default_to_none():
    p = RawSharedParameter(guid=VALID_GUID, name="X", data_type="Text")
    assert p.group is None
    assert p.description is None


def test_persisted_parameter_requires_source_file():
    with pytest.raises(ValidationError):
        SharedParameter(guid=VALID_GUID, name="X", data_type="Text")


def test_persisted_parameter_defaults_to_raw_status():
    p = SharedParameter(
        guid=VALID_GUID,
        name="X",
        data_type="Text",
        source_file="raw.json",
    )

    assert p.status == "raw"
    assert p.source_file == "raw.json"
