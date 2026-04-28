"""Pydantic validation tests for SharedParameter."""

import pytest
from pydantic import ValidationError

from revit_standards_ssot.models import SharedParameter

VALID_GUID = "12345678-1234-1234-1234-123456789abc"


def test_valid_parameter():
    p = SharedParameter(guid=VALID_GUID, name="Wall Height", data_type="Length")
    assert p.guid == VALID_GUID
    assert p.status == "raw"


def test_guid_normalised_to_lowercase():
    p = SharedParameter(guid=VALID_GUID.upper(), name="X", data_type="Text")
    assert p.guid == VALID_GUID.lower()


def test_missing_guid_raises():
    with pytest.raises(ValidationError):
        SharedParameter(name="Wall Height", data_type="Length")


def test_missing_name_raises():
    with pytest.raises(ValidationError):
        SharedParameter(guid=VALID_GUID, data_type="Length")


def test_missing_data_type_raises():
    with pytest.raises(ValidationError):
        SharedParameter(guid=VALID_GUID, name="Wall Height")


def test_invalid_guid_format_raises():
    with pytest.raises(ValidationError):
        SharedParameter(guid="not-a-uuid", name="X", data_type="Text")


def test_empty_name_raises():
    with pytest.raises(ValidationError):
        SharedParameter(guid=VALID_GUID, name="   ", data_type="Text")


def test_empty_data_type_raises():
    with pytest.raises(ValidationError):
        SharedParameter(guid=VALID_GUID, name="X", data_type="")


def test_invalid_status_raises():
    with pytest.raises(ValidationError):
        SharedParameter(guid=VALID_GUID, name="X", data_type="Text", status="unknown")


def test_optional_fields_default_to_none():
    p = SharedParameter(guid=VALID_GUID, name="X", data_type="Text")
    assert p.group is None
    assert p.description is None
