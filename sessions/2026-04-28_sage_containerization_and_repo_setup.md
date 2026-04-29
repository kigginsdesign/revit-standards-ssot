# Session Log

## Purpose

Set up GitHub repo, dev container environment, and ensure coding agent (Max) operates inside a controlled, reproducible environment.

---

## Decisions

- SQLite remains local MVP database (no change)
- Dev Container is now the primary execution environment for all pipeline code
- Windows host is strictly limited to Revit + pyRevit execution
- `.venv` on Windows is deprecated and ignored going forward
- GitHub repo is the single source of truth (SSOT); no external agent memory allowed
- Claude Code (Max) must run inside container (`/workspace`) for all non-Revit work

---

## What we did

- Created and pushed GitHub repository (`revit-standards-ssot`)
- Fixed repo naming issue and synced local/remote
- Initialized git, committed full project scaffold
- Built and launched VS Code Dev Container
- Installed dependencies via `uv`
- Ran pytest suite inside container → 19/19 tests passing
- Installed Claude Code extension inside container
- Resolved authentication flow and confirmed Max is running in container context
- Identified and blocked unintended use of `.claude` memory system
- Established strict agent memory policy (repo-only persistence)

---

## Outstanding items

- Implement pyRevit extraction script (`extract_shared_params.py`)
- Finalize extraction schema alignment with architecture.md
- Execute first real extraction from Stogel model
- Run ingest pipeline on real data
- Generate first review CSV and YAML output
- Decide on Git tracking policy for `exports/raw/`

---

## Meta-observations

- Early detection of agent-side memory divergence prevented SSOT corruption
- Containerization significantly reduces environment ambiguity and drift
- TDD boundary (pipeline only, not Revit) is holding well
- System is now in a stable state where remaining risk is isolated to Revit extraction layer
- Workflow is successfully transitioning from exploratory to controlled system design
