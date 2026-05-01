# STATE.md

## Active focus

Spec Alignment — locking the curation workflow specification and splitting the data type
vocabulary constants (RAW_REVIT_DATA_TYPES / FIRM_STANDARD_DATA_TYPES) before any further
tool execution or DB mutations.

## Last execution outcome

- Curation Workbench model fields (`curation_note`, `standard_data_type`) and bulk
  deprecation CLI (`scripts/ingest/bulk_curate.py`) implemented and committed:
  63d7c07 Add curation workbench model fields and bulk deprecation CLI
- 51/51 tests passing at that commit.
- Clean ingest confirmed: 806 inserted, 0 updated, 0 rejected against
  exports/raw/20260430_220917.json. Runtime DB at /workspace/db/standards.db.
- Q reviewed the Curation Workbench architecture and directed that the workflow and
  two-tier vocabulary be locked before any further tool execution or DB mutations.
- Spec lock applied this session: curation_workflow.md created, RAW_REVIT_DATA_TYPES and
  FIRM_STANDARD_DATA_TYPES split from KNOWN_DATA_TYPES, architecture.md updated.

## Recent decisions

- Extraction uses SharedParameterElement instead of ParameterBindings.
- source_file is assigned during ingest, not extraction.
- pyRevit script uses REVIT_SSOT_REPO environment variable for repo path.
- Canonical Windows repo path is C:\Dev\revit-standards-ssot.
- Yes/No is the accepted raw Revit string; no normalization during ingest.
- Unknown data_type values generate RAW_REVIT_DATA_TYPES warning diagnostics; accepted.
- The DB is the Curation Workbench. Raw ingest is Tier 1 (tolerant). Promotion is Tier 2
  (strict). Tiers must be kept separate: bulk_curate.py handles messy curation;
  promote.py (future) handles strict promotion only.
- KNOWN_DATA_TYPES replaced by:
  - RAW_REVIT_DATA_TYPES: diagnostics only, includes 13 confirmed MEP/structural types.
  - FIRM_STANDARD_DATA_TYPES: strict promotion allowlist, not enforced until promote.py.
- Family type: <X> variants deferred from RAW_REVIT_DATA_TYPES (canonical naming unresolved).
- Number of Poles and Reinforcement Length deferred from RAW_REVIT_DATA_TYPES (anomalies
  pending resolution).
- Decision packets must live in docs/decisions/ and be committed before --apply runs.

## Open questions

- Final FIRM_STANDARD_DATA_TYPES vocabulary: what types does the firm actually publish?
- When to expand bulk_curate.py beyond deprecation (--set-proposed, --set-standard-data-type)?
- Decision packet format and location: first docs/decisions/ file content and structure.
- Identity Data cluster (32 records): deprecate, rename, or investigate origin?
- Hand-authored GUID patterns A/B/C (23 records): stable and intentional? Gap at ...0002?
- Duplicate-name canonical GUID selection: Copyright ×4, Panel Width ×4, etc.
- Family type: <X> canonical naming: Revit-emitted "Family type: Casework" vs "FamilyType"?
- Tracer-bullet candidate set: confirmed by Sage as suitable for first proposed pass?
- Phase ×2 with data_type = Number of Poles: source fix or DB curation?
- group = "Text" on 16 records: source fix or DB curation?
- Novotny temp parameter (4 records) and ParameterTest: deprecate on next authorized run?

## Progress checklist

- [x] Repo scaffold
- [x] Dev container
- [x] Python pipeline + tests (57/57 passing after spec lock)
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
- [x] RAW_REVIT_DATA_TYPES warning diagnostics (was KNOWN_DATA_TYPES)
- [x] Data audit report (docs/reports/20260430_first_ingest_audit.md)
- [x] Curation preflight report (docs/reports/20260430_curation_preflight.md)
- [x] Curation Workbench model fields (curation_note, standard_data_type)
- [x] Bulk deprecation CLI (scripts/ingest/bulk_curate.py)
- [x] Curation workflow spec locked (docs/curation_workflow.md)
- [x] Two-tier vocabulary constants split (RAW_REVIT_DATA_TYPES / FIRM_STANDARD_DATA_TYPES)
- [ ] First decision packet (docs/decisions/)
- [ ] Curation preflight anomalies resolved (Identity Data, hand-authored GUIDs, duplicates)
- [ ] bulk_curate.py --apply first authorized run (Identity Data / Novotny / ParameterTest)
- [ ] Tracer-bullet parameter set proposed
- [ ] FIRM_STANDARD_DATA_TYPES vocabulary finalized
- [ ] promote.py (strict proposed → approved gating)
- [ ] First YAML output generated
