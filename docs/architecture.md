# Architecture

## ETL Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  EXTERNAL (Windows + Revit 2026 + pyRevit)                      │
│                                                                  │
│   Revit Model  ──►  scripts/pyrevit/extract_shared_params.py    │
│                           │                                      │
│                           ▼                                      │
│                  exports/raw/<timestamp>.json  (immutable)       │
└──────────────────────────┬──────────────────────────────────────┘
                           │  (mount / copy into repo)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  CONTAINER (Python 3.12 + uv)                                   │
│                                                                  │
│   exports/raw/*.json                                             │
│         │                                                        │
│         ▼                                                        │
│   ingest.py  ──►  Pydantic validation  ──►  SQLite DB           │
│                                               │                  │
│                        ┌─────────────────────┤                  │
│                        ▼                     ▼                  │
│                 export_yaml.py        export_review_csv.py      │
│                 (approved only)        (all statuses)           │
│                        │                     │                  │
│                        ▼                     ▼                  │
│              outputs/params.yaml    outputs/review.csv          │
└─────────────────────────────────────────────────────────────────┘
```

## Stages

### 1. Extraction (external)

- **Tool**: pyRevit script running inside Revit 2026 on Windows.
- **Output**: `exports/raw/<YYYYMMDD_HHMMSS>.json`
- **Contract**: One JSON array of shared parameter objects per run. Never overwrite an
  existing file — always write a new timestamped file.
- **Fields**: `guid`, `name`, `data_type`, `group`, `description`
- **Note**: `source_file` is assigned during container-side ingest from the raw JSON
  filename. It is not written by the pyRevit extraction script.

### 2. Ingest

- **Module**: `src/revit_standards_ssot/ingest.py`
- **Input**: One or more files from `exports/raw/`
- **Steps**:
  1. Load JSON
  2. Validate each raw record with Pydantic (`RawSharedParameter` model)
  3. Add `source_file` from the input filename and validate the persisted record
     shape (`SharedParameter` model)
  4. Upsert into SQLite by GUID (insert new, update changed fields)
  5. Set `status = raw` on new records; never downgrade existing status
- **Rule**: Raw export files are not modified.

### 3. Review (manual)

- Export review CSV (`export_review_csv.py`) to inspect all records.
- Update `status` field in the DB (raw → proposed → approved or deprecated).
- This is the only step where humans write to the database.

### 4. Export

- **YAML** (`export_yaml.py`): Queries `status = approved`, writes deterministic YAML
  sorted by GUID. This is the "published standard."
- **Review CSV** (`export_review_csv.py`): All records, all statuses, for human review.

## Data model

```
SharedParameter
  guid        : str  (UUID format, primary key)
  name        : str  (non-empty)
  data_type   : str  (e.g. Text, Integer, Number, Length, YesNo, ...)
  group       : str | None
  description : str | None
  status      : Literal["raw", "proposed", "approved", "deprecated"]
  source_file : str  (filename of the raw JSON export it came from)
  created_at  : datetime
  updated_at  : datetime
```

## Allowed data_type values (Revit shared parameter types)

Text, Integer, Number, Length, Area, Volume, Angle, URL, Material, YesNo,
MultilineText, Currency, LoadClassification, Image, FamilyType

Other values are accepted but logged as warnings during ingest.

---

## Future roadmap (post-MVP, do not implement now)

- **Downstream consumers**: Dynamo scripts, Revit shared parameter files (.txt),
  company template synchronization.
- **Remote database**: PostgreSQL for multi-user collaboration.
- **Review UI**: Simple web interface for approving/deprecating parameters.
- **CI/CD**: Automated YAML regeneration on DB changes.
- **Audit log**: Track who changed status and when.
- **Multi-file models**: Ingest from multiple Revit models and reconcile conflicts.
- **Project parameters**: Extend scope beyond shared parameters.
