"""Pydantic validation models and SQLAlchemy ORM models for shared parameters."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

Status = Literal["raw", "proposed", "approved", "deprecated"]

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Raw Revit-emitted data_type strings — used only for warning-level diagnostics during
# ingest. Unknown values are accepted but logged. This set represents the known raw
# vocabulary emitted by Revit shared parameter files; it is NOT an approval allowlist.
# "Yes/No" is the exact Revit-emitted string — do not normalize to "YesNo" during ingest.
RAW_REVIT_DATA_TYPES: frozenset[str] = frozenset({
    # Core parameter types
    "Text", "Integer", "Number", "Length", "Area", "Volume", "Angle",
    "URL", "Material", "Yes/No", "MultilineText", "Currency",
    "LoadClassification", "Image", "FamilyType",
    # MEP/structural built-in types confirmed present in the 20260430 export
    "Air Flow", "Apparent Power", "Cooling Load", "Current",
    "Electrical Potential", "Flow", "Force", "Frequency",
    "Heating Load", "Number of Poles", "Pipe Size", "Pressure",
    "Reinforcement Length", "Temperature", "Velocity",
    # Note: "Number of Poles" is a confirmed Revit built-in type. Two Phase records
    # have it assigned erroneously — that is a data-quality issue, not a type error.
    # Note: "Reinforcement Length" is a confirmed Revit built-in type. The single-letter
    # name cluster (K, B, O, …) is a data-quality issue under review, not a type error.
    # Deferred — canonical naming unresolved:
    # "Family type: Generic Models", "Family type: Casework",
    # "Family type: Doors", "Family type: Specialty Equipment"
})

# Firm-approved standard data_type vocabulary — used for future strict promotion gates
# (promote.py). Intentionally conservative. Not enforced during raw ingest.
# Not enforced until promotion tooling exists and the firm vocabulary is finalised.
FIRM_STANDARD_DATA_TYPES: frozenset[str] = frozenset({
    "Text", "Integer", "Number", "Length", "Area", "Volume", "Angle",
    "URL", "Material", "YesNo", "MultilineText", "LoadClassification",
})


# ---------------------------------------------------------------------------
# Pydantic validation model
# ---------------------------------------------------------------------------

class RawSharedParameter(BaseModel):
    """Validated representation of one raw pyRevit extraction record."""

    model_config = ConfigDict(extra="forbid")

    guid: str
    name: str
    data_type: str
    group: str | None = None
    description: str | None = None

    @field_validator("guid")
    @classmethod
    def guid_must_be_uuid(cls, v: str) -> str:
        if not _UUID_RE.match(v):
            raise ValueError(f"guid must be a valid UUID string, got: {v!r}")
        return v.lower()

    @field_validator("name")
    @classmethod
    def name_must_be_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("name must not be empty or whitespace")
        return v

    @field_validator("data_type")
    @classmethod
    def data_type_must_be_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("data_type must not be empty or whitespace")
        return v


class SharedParameter(RawSharedParameter):
    """Validated representation of a persisted shared parameter record."""

    status: Status = "raw"
    source_file: str
    curation_note: str | None = None
    standard_data_type: str | None = None

    @field_validator("source_file")
    @classmethod
    def source_file_must_be_nonempty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("source_file must not be empty or whitespace")
        return v


# ---------------------------------------------------------------------------
# SQLAlchemy ORM
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class SharedParameterRecord(Base):
    __tablename__ = "shared_parameters"

    guid: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[str] = mapped_column(String(64), nullable=False)
    group: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="raw")
    source_file: Mapped[str] = mapped_column(String(512), nullable=False)
    curation_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    standard_data_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return (
            f"<SharedParameterRecord guid={self.guid!r} "
            f"name={self.name!r} status={self.status!r}>"
        )
