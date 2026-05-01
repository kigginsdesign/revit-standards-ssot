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
  guid               : str       — UUID format, primary key
  name               : str       — non-empty
  data_type          : str       — raw Revit-emitted value, immutable after ingest
  group              : str|None
  description        : str|None
  status             : Literal["raw","proposed","approved","deprecated"]
  source_file        : str       — filename of the originating raw JSON export
  curation_note      : str|None  — human/script reasoning for deprecation or curation
  standard_data_type : str|None  — optional firm-canonical type mapping (see below)
  created_at         : datetime
  updated_at         : datetime
```

## data_type vs standard_data_type

**`data_type`** is immutable raw evidence set during ingest. It is exactly what Revit
emitted and is never modified by any downstream step.

**`standard_data_type`** is an optional curated field set during enrichment. It maps the
raw Revit vocabulary to the firm-approved canonical type string (e.g., `data_type = "Yes/No"`
→ `standard_data_type = "YesNo"`). It is validated against `FIRM_STANDARD_DATA_TYPES`
only during strict promotion (future `promote.py`).

## data_type vocabulary constants

**`RAW_REVIT_DATA_TYPES`** — known raw strings emitted by Revit. Used only for
warning-level diagnostics during ingest. Values outside this set are accepted but logged.
Not an approval allowlist.

**`FIRM_STANDARD_DATA_TYPES`** — strict firm allowlist for `standard_data_type` during
promotion. Intentionally conservative. Not enforced until `promote.py` exists.

Both constants are defined in `src/revit_standards_ssot/models.py`.

## Curation Workbench

The SQLite database is the Curation Workbench. Two validation tiers apply:

- **Tier 1 — Evidence (ingest):** Tolerant. Accepts all records passing basic format
  validation. Unknown `data_type` values are warned, not rejected.
- **Tier 2 — Standard (promotion):** Strict. Future `promote.py` enforces
  `FIRM_STANDARD_DATA_TYPES`, no name duplicates among approved records, and mandatory
  `curation_note`.

Status lifecycle:
```
raw  →  proposed  →  approved
 ↓           ↓
deprecated  deprecated
```

- `* → deprecated`: `bulk_curate.py --apply` with mandatory `--curation-note`.
- `proposed → approved`: future `promote.py` with strict validation gates.

`curation_note` documents the governance reason for every status change applied by a tool.

For the full lifecycle specification, see `docs/curation_workflow.md`.

## Allowed data_type values

Values in `RAW_REVIT_DATA_TYPES` are accepted without a warning during ingest. All other
values are accepted but produce a `WARNING` log entry. The full set is defined in
`src/revit_standards_ssot/models.py`.

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
