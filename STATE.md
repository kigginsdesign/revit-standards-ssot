# STATE.md

## Active focus

Curation Tooling — implementing the Curation Workbench model fields and bulk deprecation
CLI before any status promotion work begins.

## Last execution outcome

- First real ingest run completed: 806 inserted, 0 updated, 0 rejected
  (source: exports/raw/20260430_220917.json, runtime DB: /workspace/db/standards.db)
- Runtime DB path bug fixed (parents[3] → parents[2] in db.py). Previous ingests wrote to
  /db/standards.db (filesystem root). All subsequent work uses /workspace/db/standards.db.
- Test/runtime DB isolation confirmed: all tests use in-memory SQLite; conftest.py guard
  added.
- KNOWN_DATA_TYPES warning diagnostics added: 19 distinct unknown types emit WARNING-level
  log entries with counts and sample names; Yes/No aligned with raw Revit string.
- Data audit report committed: docs/reports/20260430_first_ingest_audit.md
- Curation preflight report committed: docs/reports/20260430_curation_preflight.md
- Q reviewed project state and recommended formalizing the Curation Workbench layer before
  status promotion work begins.
- Curation Workbench model fields (curation_note, standard_data_type) and bulk deprecation
  CLI (scripts/ingest/bulk_curate.py) implemented.

## Recent decisions

- Extraction uses SharedParameterElement instead of ParameterBindings.
- source_file is assigned during ingest, not extraction.
- pyRevit script uses REVIT_SSOT_REPO environment variable for repo path.
- pyRevit extension used as execution interface (button-based workflow).
- Canonical Windows repo path is C:\Dev\revit-standards-ssot.
- Raw exports under exports/raw/ may be git-ignored; use git add -f to force-add.
- KNOWN_DATA_TYPES: Yes/No is the accepted raw Revit value; no normalization.
- Unknown data_type values generate warning-level diagnostics but are accepted at ingest.
- The SQLite DB is the Curation Workbench. Raw ingest preserves Revit reality; approved
  records require stricter validation. Two-tier validation model formalized.
- curation_note required by bulk curation CLI when changing status to deprecated.
- standard_data_type is an optional firm-approved type mapping; never replaces data_type.

## Open questions

- Identity Data cluster (32 records named "Identity Data"): deprecate, rename, or investigate origin?
- Hand-authored GUID patterns (23 records across patterns A/B/C): are they stable and
  intentional? Is the ...0002 gap intentional?
- Duplicate-name canonical GUID selection: Copyright ×4, Panel Width ×4, etc.
- Family type: <X> canonical naming: is the Revit-emitted "Family type: Casework" form
  canonical, or is "FamilyType" expected?
- Tracer-bullet candidate set: confirmed by Sage as suitable for first proposed/approved pass?
- KNOWN_DATA_TYPES expansion: 13 confirmed Revit built-in types ready to add per preflight
  report Section E — awaiting Sage approval.

## Progress checklist

- [x] Repo scaffold
- [x] Dev container
- [x] Python pipeline + tests (32/32 passing)
- [x] GitHub integration
- [x] Agent container alignment
- [x] pyRevit extraction
- [x] Laptop environment set up and validated
- [x] Revit LocalDB issue diagnosed and resolved
- [x] REVIT_SSOT_REPO corrected to canonical path
- [x] Successful raw export (20260430_220917.json, 806 parameters)
- [x] Raw export committed and pushed
- [x] First ingest run (806 inserted, 0 rejected)
- [x] Runtime DB path bug fixed and test isolation confirmed
- [x] KNOWN_DATA_TYPES warning diagnostics
- [x] Data audit report
- [x] Curation preflight report
- [x] Curation Workbench model fields (curation_note, standard_data_type)
- [x] Bulk deprecation CLI (scripts/ingest/bulk_curate.py)
- [ ] Curation preflight anomalies resolved (Identity Data, hand-authored GUIDs, duplicates)
- [ ] Tracer-bullet parameter set approved
- [ ] KNOWN_DATA_TYPES expansion approved and applied
- [ ] First YAML output generated
