# STATE.md

## Active focus

First real ingest run from the committed raw export (exports/raw/20260430_220917.json).

## Last execution outcome

- Laptop environment set up and validated (C:\Dev\revit-standards-ssot, Dev Container rebuilt).
- Revit 2026 model-open failure diagnosed and resolved: missing SQL Server LocalDB runtimes after local SQL cleanup. SQL Server 2025 LocalDB installed first, then SQL Server 2019 LocalDB installed to restore compatibility for existing Autodesk/Advance Steel LocalDB instances.
- pyRevit reattached and extraction rerun successfully: 806 SharedParameterElement items exported.
- Raw export 20260430_220917.json force-added (git add -f) and pushed to repo.
- Laptop Dev Container rebuilt post-reboot; all 27 tests passing.

## Recent decisions

- Extraction uses SharedParameterElement instead of ParameterBindings.
- source_file is assigned during ingest, not extraction.
- pyRevit script uses REVIT_SSOT_REPO environment variable for repo path.
- pyRevit extension used as execution interface (button-based workflow).
- Codex validated as fallback executor to Claude Code.
- Canonical Windows repo path is C:\Dev\revit-standards-ssot (standardized from prior naming).
- REVIT_SSOT_REPO must point exactly to the repo root (C:\Dev\revit-standards-ssot), not a similarly named folder.
- Raw exports under exports/raw/ may be git-ignored; use git add -f <file> to force-add specific immutable exports before committing.

## Open questions

- Ingest behavior against real data: validation edge cases, duplicate GUID handling, unexpected field values.
- What does the first review CSV look like? Which fields need curation before approval?
- Are all 806 exported parameters expected, or will some fail Pydantic validation?

## Progress checklist

- [x] Repo scaffold
- [x] Dev container
- [x] Python pipeline + tests
- [x] GitHub integration
- [x] Agent container alignment
- [x] pyRevit extraction
- [x] Laptop environment set up and validated
- [x] Revit LocalDB issue diagnosed and resolved
- [x] REVIT_SSOT_REPO corrected to canonical path
- [x] Successful raw export (20260430_220917.json, 806 parameters)
- [x] Raw export committed and pushed
- [ ] First ingest run
- [ ] Review + approve parameters
- [ ] YAML output
