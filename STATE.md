# STATE.md

## Active focus

Complete Step 2 of MVP:
- Implement pyRevit shared parameter extraction
- Generate first real JSON payload

## Last execution outcome

- Dev Container operational
- All tests passing (19/19)
- GitHub repo live and synced
- Claude Code (Max) running inside container

## Recent decisions

- Enforced container-first execution model
- Eliminated reliance on Windows `.venv`
- Locked agent behavior to repo-based SSOT only
- Confirmed dual-environment architecture (Revit vs pipeline)

## Open questions

- Final field schema for extraction (confirm alignment with architecture.md)
- Whether to track raw JSON exports in Git or ignore them
- Exact pyRevit API surface for extracting shared parameters cleanly

## Progress checklist

- [x] Repo scaffold
- [x] Dev container
- [x] Python pipeline + tests
- [x] GitHub integration
- [x] Agent container alignment
- [ ] pyRevit extraction
- [ ] First ingest run
- [ ] Review + approve parameters
- [ ] YAML output
