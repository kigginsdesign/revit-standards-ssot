<!-- sessions/2026-05-01_sage_curation_workbench_governance.md -->

# Purpose

Move the Revit Standards SSOT project from first real ingest discovery into a formal Curation Workbench architecture and governance workflow before any DB status mutations.

# Decisions

- Paused feature execution when the workflow began exposing spec ambiguity rather than simple implementation bugs.
- Consulted Q for architecture direction before proceeding with status promotion or curation applies.
- Adopted the Curation Workbench model: SQLite DB is the reconciliation layer between raw Revit evidence and curated firm standards.
- Formalized two validation tiers:
  - Tier 1 Evidence: tolerant raw ingest that preserves Revit-emitted values.
  - Tier 2 Standard: strict future approval gates for firm-standard output.
- Added `curation_note` and `standard_data_type` as curation-layer fields.
- Confirmed `data_type` remains immutable raw Revit evidence.
- Split overloaded `KNOWN_DATA_TYPES` into:
  - `RAW_REVIT_DATA_TYPES` for raw-ingest warning diagnostics.
  - `FIRM_STANDARD_DATA_TYPES` for future strict approval validation.
- Clarified that `RAW_REVIT_DATA_TYPES` classifies legitimate raw Revit type strings independent of record-level quality.
- Added a testing rule requiring synthetic sentinel values for unknown data type warning/rejection tests.
- Created a governance path using `docs/decisions/` before DB mutations.
- Agreed that the first deprecation apply, when authorized, should be run as separate apply calls per batch for clearer audit history.
- Agreed that applied decision packets should be updated from `Status: Proposed` to `Status: Applied` with timestamp, commands, counts, and verification results.

# What we did

- Reviewed Max's first real ingest report:
  - 806 raw records.
  - 806 inserted on clean ingest after DB path correction.
  - 0 updated.
  - 0 rejected.
- Identified and corrected a runtime DB path bug:
  - Incorrect path had previously sent runtime DB activity to `/db/standards.db`.
  - Correct runtime DB path is `/workspace/db/standards.db`.
  - Added test/runtime DB isolation guard.
- Added warning-level raw `data_type` diagnostics while preserving raw ingest behavior.
- Aligned `Yes/No` as the raw Revit-emitted value.
- Created first ingest audit report.
- Created curation preflight report.
- Paused before status promotion because the preflight showed larger source hygiene and governance questions:
  - 23 hand-authored-looking GUIDs.
  - 32 records named `Identity Data`.
  - 16 records with `group = "Text"`.
  - duplicate/conflicting names.
  - Phase records with `data_type = Number of Poles`.
  - Family type variants.
  - blank/NULL descriptions.
- Consulted Q and received the directive to formalize the Curation Workbench.
- Implemented Curation Workbench architecture:
  - `curation_note`
  - `standard_data_type`
  - initial `bulk_curate.py`
  - documentation updates to project memory and architecture docs.
- Locked the formal curation lifecycle in `docs/curation_workflow.md`:
  - Raw Ingest
  - Preflight Audit
  - Decision Packet
  - Bulk Deprecation
  - Propose Selection
  - Enrichment
  - Strict Promotion
  - YAML Export
- Replaced `KNOWN_DATA_TYPES` with two explicit constants:
  - `RAW_REVIT_DATA_TYPES`
  - `FIRM_STANDARD_DATA_TYPES`
- Added confirmed raw Revit built-in types including `Number of Poles` and `Reinforcement Length`.
- Added AGENTS.md test rule requiring synthetic unknown-type sentinels.
- Created `docs/decisions/20260501_deprecation_batch_1.md` with `Status: Proposed`.
- Confirmed no final DB curation applies were run.
- Confirmed latest reported tests were passing: 55 passed.

# Outstanding items

- Continue next session with Q on project architecture before authorizing Max to mutate DB state.
- Review `docs/decisions/20260501_deprecation_batch_1.md`.
- Decide whether to approve the three proposed deprecation batches:
  - 32 `Identity Data` records.
  - 4 Novotny temp records.
  - 1 `ParameterTest`.
- Confirm or revise exact `curation_note` text for each batch.
- If approved, instruct Max to run three separate `bulk_curate.py --apply` calls and update the decision packet to `Status: Applied`.
- Finalize or refine `FIRM_STANDARD_DATA_TYPES` before designing `promote.py`.
- Decide when to expand `bulk_curate.py` beyond deprecation to proposed-selection and enrichment.
- Resolve remaining curation questions:
  - `group = "Text"` anomaly records.
  - Phase / Number of Poles records.
  - hand-authored GUID clusters.
  - Family type variants.
  - duplicate-name canonical GUID choices.
- Do not write `promote.py` until strict approval rules are agreed.
- Do not generate YAML until approved records exist.

# Meta-observations

- The project reached the "Data Gravity" milestone: real Revit data is messy enough that architecture must distinguish raw evidence from curated truth.
- The most important workflow improvement was pausing Max execution when issues became architectural rather than tactical.
- Q was useful as a strategist to stop piecemeal implementation and lock the Curation Workbench spec.
- Max performed well once tasks were constrained to documentation, constants, and governance artifacts.
- Future Max tasks should be smaller and gated by decision packets when DB mutation is involved.
- Tests using real Revit types as proxies for unknown values are brittle; synthetic sentinel values are now the preferred testing convention.
