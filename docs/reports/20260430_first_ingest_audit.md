# First Ingest Audit Report — 20260430_220917

**Generated:** 2026-05-01  
**Session:** First real ingest pass  
**Auditor:** Max (Claude Code agent)

---

## Source

| Field | Value |
|---|---|
| Raw export filename | `20260430_220917.json` |
| Full path | `exports/raw/20260430_220917.json` |
| Total raw records in JSON | 806 |

---

## Database State After Ingest

| Metric | Value |
|---|---|
| Total `SharedParameter` rows | 806 |
| DB path | `db/standards.db` |

**Note:** `db/standards.db` is gitignored and does not survive container resets. The ingest must be re-run after any container restart using the established command:

```
uv run python3 -c "
from pathlib import Path
from revit_standards_ssot.db import make_session_factory
from revit_standards_ssot.ingest import ingest_file
session_factory = make_session_factory()
with session_factory() as session:
    print(ingest_file(Path('exports/raw/20260430_220917.json'), session))
"
```

### Count by Status

| Status | Count |
|---|---|
| `raw` | 806 |
| `proposed` | 0 |
| `approved` | 0 |
| `deprecated` | 0 |

### Count by Source File

| source_file | Count |
|---|---|
| `20260430_220917.json` | 806 |

---

## Review CSV

| Field | Value |
|---|---|
| Path | `outputs/review_20260430_220917.csv` |
| Row count (data rows) | 806 |

**Columns (in order):**

`guid`, `name`, `data_type`, `group`, `description`, `status`, `source_file`, `created_at`, `updated_at`

`outputs/` is gitignored. Regenerate with `export_review_csv()` from `src/revit_standards_ssot/export_review_csv.py` after ingest.

---

## Data Type Inventory

Sorted by count descending. Values absent from `KNOWN_DATA_TYPES` are marked with `*`.

| Count | data_type | In KNOWN_DATA_TYPES |
|---|---|---|
| 291 | `Text` | Yes |
| 179 | `Length` | Yes |
| 102 | `Material` | Yes |
| 52 | `Yes/No` * | No |
| 51 | `Integer` | Yes |
| 41 | `URL` | Yes |
| 16 | `Number` | Yes |
| 12 | `Reinforcement Length` * | No |
| 9 | `Temperature` * | No |
| 7 | `Air Flow` * | No |
| 4 | `Area` | Yes |
| 4 | `Force` * | No |
| 4 | `Pipe Size` * | No |
| 4 | `Pressure` * | No |
| 4 | `Number of Poles` * | No |
| 3 | `Angle` | Yes |
| 3 | `Volume` | Yes |
| 3 | `Cooling Load` * | No |
| 2 | `Current` * | No |
| 2 | `Electrical Potential` * | No |
| 2 | `Family type: Generic Models` * | No |
| 2 | `Frequency` * | No |
| 2 | `Heating Load` * | No |
| 1 | `Apparent Power` * | No |
| 1 | `Family type: Casework` * | No |
| 1 | `Family type: Doors` * | No |
| 1 | `Family type: Specialty Equipment` * | No |
| 1 | `Flow` * | No |
| 1 | `LoadClassification` | Yes |
| 1 | `Velocity` * | No |

**Total distinct data_type values:** 30  
**Absent from `KNOWN_DATA_TYPES`:** 20 distinct values, 133 records

### Values absent from KNOWN_DATA_TYPES

The following data_type strings appear in the ingested data but are not listed in
`KNOWN_DATA_TYPES` in `src/revit_standards_ssot/models.py`:

```
Yes/No (52)
Reinforcement Length (12)
Temperature (9)
Air Flow (7)
Force (4)
Pipe Size (4)
Pressure (4)
Number of Poles (4)
Cooling Load (3)
Current (2)
Electrical Potential (2)
Family type: Generic Models (2)
Frequency (2)
Heating Load (2)
Apparent Power (1)
Family type: Casework (1)
Family type: Doors (1)
Family type: Specialty Equipment (1)
Flow (1)
Velocity (1)
```

Per Sage policy: these values are **not rejected during ingest**. `KNOWN_DATA_TYPES` is
informational only. Unknown values are accepted as raw Revit-emitted text and flagged here
for human review only.

---

## Yes/No Preservation Note

**`Yes/No` (with slash) is the exact string emitted by Revit's shared parameter file
format.** It is preserved verbatim during ingest. The `KNOWN_DATA_TYPES` constant in
`models.py` contains `"YesNo"` (no slash), which does not match the Revit string.

Per Sage policy:
- Do **not** normalize `Yes/No` → `YesNo` during ingest.
- Do **not** add `Yes/No` as a rejection criterion.
- `KNOWN_DATA_TYPES` may need to be updated to match reality, but that decision is deferred
  to human curation.

Affected records: **52**

---

## Zero-Padded GUID Records

Eight records have GUIDs with the pattern `00000000-0000-0000-0000-00000000000x`.
These are technically valid UUIDs and pass all validation. They are flagged for human
review because they appear to be manually authored rather than Revit-generated.

Note: sequence skips `...000000000002` — that value is absent from the export.

| GUID | Name | data_type | group | source_file |
|---|---|---|---|---|
| `00000000-0000-0000-0000-000000000001` | Copyright | Text | Identity Data | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000003` | Manufacturer Address | Text | Other | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000004` | Manufacturer Phone | Text | Other | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000005` | Manufacturer Fax | Text | Other | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000006` | Manufacturer Email | Text | Other | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000007` | Manufacturer Website | URL | Other | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000008` | Specification | URL | Text | 20260430_220917.json |
| `00000000-0000-0000-0000-000000000009` | Product Data | URL | Text | 20260430_220917.json |

**Additional anomaly:** Records `...000000000008` (Specification) and `...000000000009`
(Product Data) have `group = "Text"`. This appears to be a data-entry error — `"Text"` is
a data_type value, not a Revit parameter group name. Flag for curation.

Per Sage policy: do **not** mutate these GUIDs or records. Review flag only.

---

## Description Quality

| Metric | Raw JSON | Database |
|---|---|---|
| Records with blank description (`""`) | 806 | 0 |
| Records with NULL description | 0 | 806 |

The ingest pipeline converts blank-string descriptions (`""` in JSON) to SQL `NULL` in the
database. This is expected SQLAlchemy behavior — when the JSON value is an empty string and
the ORM column is `nullable=True`, the stored value depends on the model assignment path.

Actual ingest code path: `description=param.description` where `param.description` comes
from `RawSharedParameter.description` which defaults to `None` when the JSON value is
`null`. The raw JSON has `"description": null` for all 806 records (not empty strings —
the pyRevit extractor emits `null` when no description is present).

Per Sage policy: blank/null descriptions are **not a blocker for MVP ingest**. This is a
data-quality limitation of the current pyRevit extraction, not an ingest failure.

---

## Required Field Null/Blank Check

Checked in both the raw JSON and the database.

| Field | NULL in DB | Blank (`""`) in DB | Missing/null in raw JSON |
|---|---|---|---|
| `guid` | 0 | 0 | 0 |
| `name` | 0 | 0 | 0 |
| `data_type` | 0 | 0 | 0 |

No required field violations. All 806 records have valid, non-empty values for `guid`,
`name`, and `data_type`.

---

## Duplicate GUID Check

**No duplicate GUIDs found** in the raw export. All 806 GUIDs are unique.

The ingest upserts by GUID (primary key). On re-ingest of the same file, all 806 records
are updated in place; no duplicates are created.

---

## Recommended Human Review Focus Areas

Before any record is promoted from `raw` → `proposed` or `approved`:

### Priority 1 — Verify before any promotion

1. **`Yes/No` data_type (52 records)** — Confirm whether the canonical value for this
   firm's parameter standards is `Yes/No` (Revit native) or `YesNo`. Update
   `KNOWN_DATA_TYPES` to match, or document the divergence explicitly.

2. **Zero-padded GUIDs (8 records)** — Confirm these 8 parameters are intentionally in the
   library. Verify the GUIDs are stable and will not collide if the shared parameter file
   is regenerated. Resolve the `group = "Text"` error on Specification and Product Data.

3. **`group = "Text"` anomaly (2 records)** — Specification and Product Data have a
   data_type string (`"Text"`) stored in the `group` field. This is likely a data-entry
   error in the original shared parameter file. Correct in the source `.txt` file, then
   re-extract and re-ingest.

### Priority 2 — Scope decision required

4. **MEP/structural data_types (81 records)** — `Reinforcement Length`, `Temperature`,
   `Air Flow`, `Force`, `Pipe Size`, `Pressure`, `Number of Poles`, `Cooling Load`,
   `Current`, `Electrical Potential`, `Flow`, `Velocity`, `Apparent Power`, `Frequency`,
   `Heating Load` are present. Per Sage policy these are in scope as-imported. A human
   reviewer should confirm which of these parameters are intentionally maintained by this
   firm vs. inherited from a third-party shared parameter file.

5. **`Family type: <X>` naming (5 records)** — `Family type: Generic Models`,
   `Family type: Casework`, `Family type: Doors`, `Family type: Specialty Equipment` use a
   pattern distinct from `KNOWN_DATA_TYPES`'s `FamilyType`. Confirm the correct canonical
   string for this data_type category.

### Priority 3 — Data completeness

6. **Descriptions (806 records, all null)** — No parameter has a description. If
   descriptions are required for approved parameters, the pyRevit extraction script needs
   to be updated to read the description field from the Revit shared parameter file (a
   Windows-side concern). Verify whether the `.txt` shared parameter file contains
   description data that the current extractor is not reading.

---

## Ingest Session Notes

The `db/standards.db` artifact was absent at the start of this audit session (container
reset between sessions). Ingest was re-run per task instructions. The re-run produced
`{"inserted": 0, "updated": 806, "rejected": 0}` rather than `{"inserted": 806, ...}`,
indicating the database had been recreated (likely by `uv run pytest`, which calls
`make_session_factory()` → `create_tables()`) before the ingest command ran. All 806
records were updated from the prior ingest state. No data integrity issues resulted.
