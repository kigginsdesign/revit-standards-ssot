# STATE.md

## Active focus

Transition from extraction implementation to first real ingest run.

## Last execution outcome

- pyRevit extraction successfully implemented and validated in Revit.
- SharedParameterElement-based extraction confirmed working (806 parameters exported).
- Dev container environment stabilized (Claude auth + Codex fallback working).
- All tests passing (27/27).

## Recent decisions

- Extraction uses SharedParameterElement instead of ParameterBindings.
- source_file is assigned during ingest, not extraction.
- pyRevit script uses REVIT_SSOT_REPO environment variable for repo path.
- pyRevit extension used as execution interface (button-based workflow).
- Codex validated as fallback executor to Claude Code.

## Open questions

- None for extraction phase.
- Next phase: ingest behavior on real data (validation edge cases, duplicates, schema surprises).

## Progress checklist

- [x] Repo scaffold
- [x] Dev container
- [x] Python pipeline + tests
- [x] GitHub integration
- [x] Agent container alignment
- [x] pyRevit extraction
- [ ] First ingest run
- [ ] Review + approve parameters
- [ ] YAML output
