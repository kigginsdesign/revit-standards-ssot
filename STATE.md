# STATE.md

## Active focus

Spec Alignment / Governance Review: review first proposed deprecation decision packet
with Q/Sage before any DB mutation.

## Last execution outcome

This session completed first-ingest stabilization and built the full Curation Workbench
architecture. In sequence:

- First real ingest run completed and stabilized (806 inserted, 0 updated, 0 rejected)
  against exports/raw/20260430_220917.json. Runtime DB: /workspace/db/standards.db.
- Runtime DB path bug fixed (parents[3] → parents[2] in db.py); prior ingests had written
  to /db/standards.db (filesystem root). Fixed commit: e4d7fc3.
- Test/runtime DB isolation guard added (conftest.py session-scoped autouse fixture).
- Warning-level raw data_type diagnostics implemented via RAW_REVIT_DATA_TYPES; Yes/No
  aligned with raw Revit string.
- First ingest audit report committed: docs/reports/20260430_first_ingest_audit.md.
- Curation preflight report committed: docs/reports/20260430_curation_preflight.md.
  Surfaced 23 hand-authored GUIDs (not 8 as originally stated), 32 "Identity Data"
  placeholder records, 82 duplicate names, 13 conflicting data_type cases.
- Q reviewed project state and recommended formalizing the Curation Workbench layer.
- curation_note (nullable Text) and standard_data_type (nullable String) added to model.
- bulk_curate.py created: controlled deprecation CLI, dry-run by default, ORM-only
  filters, mandatory curation_note on apply, no approved-promotion path.
- docs/curation_workflow.md created: formal 8-stage lifecycle spec.
- KNOWN_DATA_TYPES split into RAW_REVIT_DATA_TYPES (ingest diagnostics only) and
  FIRM_STANDARD_DATA_TYPES (future strict promotion allowlist, not yet enforced).
- Number of Poles and Reinforcement Length promoted to RAW_REVIT_DATA_TYPES as confirmed
  Revit built-in types; their data-quality anomalies are separate concerns.
- AGENTS.md: synthetic sentinel testing rule added for unknown-data_type tests.
- docs/decisions/20260501_deprecation_batch_1.md created: Status: Proposed.
  Covers 37 records across three batches (Identity Data ×32, Novotny temp ×4,
  ParameterTest ×1). No --apply commands have been run.

Current DB state: 806 total, 806 raw, 0 deprecated, 0 proposed, 0 approved.

## Recent decisions

- Extraction uses SharedParameterElement instead of ParameterBindings.
- source_file is assigned during ingest, not extraction.
- pyRevit script uses REVIT_SSOT_REPO environment variable for repo path.
- Canonical Windows repo path is C:\Dev\revit-standards-ssot.
- Yes/No is the accepted raw Revit string; no normalization during ingest.
- The DB is the Curation Workbench. Two-tier validation: Tier 1 (tolerant ingest) and
  Tier 2 (strict promotion). Tiers must be kept separate in tooling.
- RAW_REVIT_DATA_TYPES classifies legitimate raw Revit-emitted type strings independently
  of whether individual records using those strings are bad data.
- FIRM_STANDARD_DATA_TYPES is the future strict promotion allowlist for standard_data_type.
  Not enforced during raw ingest.
- Unknown raw data_type tests must use synthetic sentinel values, not real Revit types.
  Rationale: RAW_REVIT_DATA_TYPES can grow at any time; real types make tests brittle.
- Decision packets under docs/decisions/ govern DB status mutations.
- Status: Proposed decision packets do not authorize DB mutation. Sage/Shawn must
  explicitly authorize each batch before --apply is run.
- First deprecation apply should use separate --apply calls per batch for clearer audit
  trail, not one combined operation.
- After any --apply run, the same decision packet must be updated to Status: Applied with
  the actual commands, timestamp, matched/applied counts, and verification results in the
  same commit.
- docs/reports/ is for analysis and audit reports (read-only after commit).
- docs/decisions/ is for durable governance decisions before and after DB mutation.

## Open questions

- Review docs/decisions/20260501_deprecation_batch_1.md with Q/Sage. Approve all three
  batches as proposed? Revise curation_note text?
- Confirm FIRM_STANDARD_DATA_TYPES vocabulary before designing promote.py.
- Decide when to expand bulk_curate.py beyond deprecation (--set-proposed, enrichment).
- Decide handling of group = "Text" anomalies (16 records), Phase / Number of Poles
  records (2 records with wrong data_type), hand-authored GUID clusters (23 records),
  Family type: <X> canonical naming, and duplicate-name canonical GUID choices.
- Tracer-bullet candidate set: confirmed by Sage as suitable for first proposed pass?
- Continue Q/Sage architecture alignment before status promotion or approval tooling.

## Progress checklist

- [x] Repo scaffold
- [x] Dev container
- [x] Python pipeline + tests (55/55 passing)
- [x] GitHub integration
- [x] Agent container alignment
- [x] pyRevit extraction
- [x] Laptop environment set up and validated
- [x] Revit LocalDB issue diagnosed and resolved
- [x] REVIT_SSOT_REPO corrected to canonical path
- [x] Successful raw export (20260430_220917.json, 806 parameters)
- [x] Raw export committed and pushed
- [x] First ingest run (806 inserted, 0 rejected)
- [x] Runtime DB path fix and test/runtime DB isolation guard
- [x] First ingest audit report (docs/reports/20260430_first_ingest_audit.md)
- [x] Curation preflight report (docs/reports/20260430_curation_preflight.md)
- [x] Curation Workbench model fields (curation_note, standard_data_type)
- [x] Bulk deprecation CLI (scripts/ingest/bulk_curate.py)
- [x] Curation workflow spec locked (docs/curation_workflow.md)
- [x] Two-tier data type constants (RAW_REVIT_DATA_TYPES / FIRM_STANDARD_DATA_TYPES)
- [x] First proposed deprecation decision packet (docs/decisions/20260501_deprecation_batch_1.md)
- [ ] Decision packet approval (Q/Sage sign-off on Batch 1)
- [ ] First bulk deprecation apply (Identity Data, Novotny temp, ParameterTest)
- [ ] Propose selection workflow (bulk_curate.py --set-proposed or equivalent)
- [ ] Enrichment workflow (standard_data_type population)
- [ ] FIRM_STANDARD_DATA_TYPES vocabulary finalized
- [ ] promote.py strict approval tool (proposed → approved)
- [ ] Review + approve tracer-bullet parameters
- [ ] First YAML output generated
