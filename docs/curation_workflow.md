# Curation Workflow

Formal lifecycle for the Revit Standards SSOT Curation Workbench.

**Status:** Spec locked 2026-05-01. No promotions have been applied yet.

---

## Overview

The SQLite database is the **Curation Workbench** — the place where raw Revit evidence is
reconciled against firm standards before becoming approved YAML output. The pipeline has
two distinct validation tiers and two distinct data type vocabularies.

---

## Two-Tier Validation Model

### Tier 1 — Evidence (Ingest)

Ingest is **tolerant by design**. It captures exactly what Revit emits without imposing
firm standards on raw data.

- Accepts all records where `guid`, `name`, and `data_type` are present and non-empty.
- Preserves `data_type` exactly as Revit emitted it. No normalization.
- Accepts unusual, unknown, or non-standard `data_type` values with a `WARNING` log entry.
- Does not reject records for missing descriptions, duplicate names, non-standard data types,
  suspicious GUIDs, or source-authoring anomalies. These are review findings, not failures.
- Sets `status = raw` on every new record.

### Tier 2 — Standard (Promotion)

Promotion to `approved` enforces strict firm-standard rules.

- `standard_data_type` must be present and must be a member of `FIRM_STANDARD_DATA_TYPES`.
- Record must have passed human curation review.
- Record must not be a duplicate of an already-approved record.
- Promotion is handled by a dedicated tool (`promote.py`, future) with explicit validation
  gates. It is **not** handled by the messy bulk curation logic in `bulk_curate.py`.

---

## Two-Tier Data Type Vocabulary

### `data_type` — Immutable Raw Evidence

- Set during ingest from the raw Revit export.
- **Never modified** by any pipeline step after ingest.
- Validated during ingest only for non-empty format; no allowlist enforcement.
- Checked against `RAW_REVIT_DATA_TYPES` for warning-level diagnostics only.
- `RAW_REVIT_DATA_TYPES` is defined in `src/revit_standards_ssot/models.py`.

### `standard_data_type` — Curated Firm Mapping

- Nullable. Set during enrichment or curation, not during raw ingest.
- Maps messy or raw Revit vocabulary to the firm-approved canonical type string.
- Validated against `FIRM_STANDARD_DATA_TYPES` during **strict promotion only**.
- Example: `data_type = "Yes/No"` → `standard_data_type = "YesNo"` (if firm decides "YesNo"
  is canonical).
- `FIRM_STANDARD_DATA_TYPES` is defined in `src/revit_standards_ssot/models.py`.

---

## Lifecycle Stages

### Stage 1 — Raw Ingest

**Purpose:** Evidence capture.

- Run `ingest_file()` from `src/revit_standards_ssot/ingest.py`.
- All records enter with `status = raw`.
- Unknown `data_type` values produce `WARNING` log entries; records are still accepted.
- `curation_note` and `standard_data_type` are `NULL`.

**No human review required at this stage.**

---

### Stage 2 — Preflight Audit

**Purpose:** Understand what was ingested before deciding what to keep.

- Export review CSV via `export_review_csv.py`.
- Run analytical inspection queries against the DB.
- Identify:
  - Anomalous source-authoring errors (wrong `group`, wrong `data_type`)
  - Inherited or third-party parameter clusters
  - Duplicate names (same name, multiple GUIDs)
  - Conflicting records (same name, different `data_type`)
  - Suspicious GUIDs (hand-authored sequential patterns)
  - Unknown `data_type` values
- Produce an audit report under `docs/reports/`.

---

### Stage 3 — Decision Packet

**Purpose:** Governance artifact before any status mutations.

- Written document in `docs/decisions/` (one file per batch of decisions).
- Records:
  - Which records are proposed for deprecation and why.
  - Which records are candidates for proposed/approved status.
  - Dry-run `bulk_curate.py` commands to be applied.
  - Any unresolved decisions requiring Sage input.
- Must be committed before applying mutations to the DB.
- Decision packets are durable; they explain the "why" behind every status change.

---

### Stage 4 — Bulk Deprecation

**Purpose:** Prune records that are not firm standards from the active set.

- Tool: `scripts/ingest/bulk_curate.py`
- Sets `status = deprecated` with a mandatory `--curation-note`.
- Dry-run by default; requires explicit `--apply`.
- Raw record evidence is **preserved** — records are marked deprecated, never deleted.
- The `curation_note` documents the reason (e.g., "Inherited from vendor file",
  "Placeholder name — not a real parameter").

**Current scope:** Deprecation only. `bulk_curate.py` does not promote to `approved`.

---

### Stage 5 — Propose Selection *(future)*

**Purpose:** Select candidate records for firm-standard review.

- Sets `status = proposed` on chosen records.
- This is not approval — it is a staging step for human review.
- Records entering `proposed` should already have passed basic deduplication and anomaly
  checks from Stage 4.
- **Not yet implemented** in `bulk_curate.py`. Future scope: add `--set-proposed` flag
  with appropriate guards.

---

### Stage 6 — Enrichment *(future)*

**Purpose:** Populate curated fields to prepare for strict promotion.

- Set `standard_data_type` to the firm-canonical type mapping.
- Optionally update or supplement `curation_note` with human reasoning.
- `data_type` is **never modified** during enrichment.
- Tool: `bulk_curate.py` (future: `--set-standard-data-type` flag) or direct DB update
  with a recorded decision packet.

---

### Stage 7 — Strict Promotion *(future — not implemented)*

**Purpose:** Promote `proposed` → `approved` with strict validation gates.

- Tool: `promote.py` (future, separate from `bulk_curate.py`).
- Enforces:
  - `standard_data_type` is present and is a member of `FIRM_STANDARD_DATA_TYPES`.
  - No duplicate name among already-approved records.
  - `curation_note` present.
  - Record has been in `proposed` status (not promoted directly from `raw`).
- Must not be handled by the messy bulk wrangling logic in `bulk_curate.py`.
- `FIRM_STANDARD_DATA_TYPES` is defined but **not enforced** until this tool exists.

---

### Stage 8 — YAML Export

**Purpose:** Publish the approved firm standard.

- Tool: `export_yaml.py` from `src/revit_standards_ssot/`.
- Queries only `status = approved` records.
- Output is deterministic: sorted by GUID, alphabetical keys.
- YAML is the published standard. Nothing else is authoritative.

---

## Tool Boundaries

| Tool | Role | Allowed status transitions |
|---|---|---|
| `ingest.py` | Raw evidence capture | None → `raw` |
| `bulk_curate.py` | Messy curation and enrichment | `raw`/`proposed` → `deprecated` |
| `promote.py` *(future)* | Strict approval gating | `proposed` → `approved` |
| `export_yaml.py` | Publishing | None (read-only) |
| `export_review_csv.py` | Human review export | None (read-only) |

`bulk_curate.py` deliberately does not support promotion to `approved`. That boundary
is enforced by keeping approval logic in a separate, stricter tool.

---

## Governance Artifact Locations

| Location | Contents |
|---|---|
| `docs/reports/` | Analysis reports, audit findings, preflight summaries. Read-only after commit. |
| `docs/decisions/` | Durable governance decisions. Decision packets before status mutations. |
| `sessions/` | Sage session logs. |

Decision packets in `docs/decisions/` must be committed **before** the corresponding
`bulk_curate.py --apply` run is executed.

---

## Current Curation Status

As of 2026-05-01:

- All 806 records are `status = raw`.
- No records have been promoted or deprecated.
- `curation_note` and `standard_data_type` are `NULL` on all records.
- Preflight audit is complete: see `docs/reports/20260430_curation_preflight.md`.
- Pending decisions are listed in that report, Section H.
- No decision packets have been created in `docs/decisions/` yet.
- `FIRM_STANDARD_DATA_TYPES` is defined but not enforced (no promotion tooling exists yet).
