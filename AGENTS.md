# AGENTS.md — Hard Rules for Coding Agents

This file contains non-negotiable constraints for any AI coding agent (Claude, Cursor,
Copilot, etc.) working in this repository.

> **See also:** This project uses a multi-agent workflow.
> See `ORCHESTRATION.md` for agent coordination and `STATE.md` for current dynamic state.

---

## Scope

**MVP is Shared Parameters only.** Do not expand scope to other Revit element types,
family parameters, or project parameters without explicit user approval.

---

## Identifiers

- **GUID is the sole stable identifier** for shared parameters.
- **Never use Revit ElementId** as a persistent key. ElementIds are session-scoped and
  change across Revit versions/files.
- GUIDs must be stored and validated as proper UUID strings (e.g., `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).

---

## Status lifecycle

Allowed values: `raw` → `proposed` → `approved` | `deprecated`

- Do not invent new status values.
- YAML output is generated **only** for records where `status = approved`.
- `deprecated` records are retained in the database but excluded from all outputs.

---

## Data immutability

- Files under `exports/raw/` are **immutable evidence**. No script may modify, rename,
  delete, or overwrite them.
- Ingest scripts copy/parse data out of raw exports; they do not write back into them.

---

## Pipeline direction

The pipeline is **read-only from Revit**. No script in this repo writes data back to
Revit or modifies Revit files. Write-back is out of scope for MVP.

---

## Database

- SQLite for MVP. Use SQLAlchemy ORM — no raw SQL strings in application code.
- Do not switch database backends without updating this file and `PROJECT_MEMORY.md`.

---

## Validation

- All ingest data must pass Pydantic validation before touching the database.
- Required fields: `guid`, `name`, `data_type`. Records missing these must be rejected
  and logged, not silently dropped or inserted with null values.
- **Never reject raw ingest records** based on validation rules meant for approved records.
  Missing descriptions, non-standard data_type values, duplicate names, and source-authoring
  anomalies are all accepted at Tier 1 (ingest). They are review findings, not ingest failures.

---

## Curation rules

- Do **not** promote records to `approved` or delete raw records without explicit curation
  rules and a recorded decision packet.
- `status = deprecated` changes via the bulk curation CLI **must** supply a non-blank
  `curation_note`. The CLI enforces this; agents must not bypass it.
- Bulk curation tools must use SQLAlchemy ORM-based filtering or explicit structured filter
  parameters. **Never use raw SQL criteria strings** in application or tool code.
- The `standard_data_type` field is for firm-approved type mapping during curation only.
  It does **not** replace `data_type`. Raw `data_type` is always preserved as imported.

---

## Testing

- Do **not** write unit tests for pyRevit extraction (Revit API code, scripts in
  `scripts/pyrevit/`). That code runs outside the container and cannot be tested here.
- **Do** write pytest tests for:
  1. Pydantic model validation (accepts valid, rejects invalid)
  2. SQLAlchemy insert / update / query round-trips
  3. YAML export (only approved records appear)

---

## Dev container

- The dev container must not depend on any Revit or pyRevit libraries.
- Python version: 3.11 or 3.12.
- Package manager: `uv`.

---

## General coding rules

- No `pandas` dependency unless a specific task genuinely requires it.
- No ad-hoc scripts that reach into `exports/raw/` and mutate files.
- Do not add scope, abstractions, or features beyond what the current task requires.
- Keep generated YAML deterministic: sort keys alphabetically, sort records by GUID.
- When in doubt, ask before expanding scope.

---

## Execution report format

Every Max session must close with a report using exactly these four sections. No other format is acceptable.

**Git status**
Output of git status and the commit hash and message of the last commit. If nothing
was committed this session, say so explicitly.

**What changed**
Files modified, created, or deleted. Tests added and their pass/fail status. Commit hash if applicable.

**What surprised**
Anything unexpected during execution — edge cases, schema issues, failed assumptions, constraint violations.

**What's blocked or deferred**
Work that could not be completed this session. Explicit reason for each item.

**Questions for Sage**
Tactical decisions or ambiguities that need Sage's input before the next session. If none, write "None."

If a section has nothing to report, write "None." Do not omit sections.

---

## Execution environment rules

- All Python pipeline operations MUST run inside the Dev Container (`/workspace`).
- Do NOT run pipeline code from Windows paths (e.g., `C:\Dev\...`).
- The only allowed Windows execution is pyRevit extraction.
- pyRevit scripts are authored in-repo but executed manually in Revit on Windows.
- Agents must not attempt to execute or validate pyRevit scripts inside the dev container.
- Validation of pyRevit behavior requires user execution and feedback.
- **Agents must not attempt to diagnose or repair Windows/Revit host runtime dependencies
  from inside the container.** Windows-only dependencies — Revit, pyRevit, Autodesk
  add-ins, SQLLocalDB — are user-executed host concerns, not container concerns.
- For pyRevit/Revit failures, agents may inspect repo code and ask the user for Revit
  journal output, but must not assume that any repo code runs during model open unless
  startup hooks or event handlers are explicitly present in the repo.
- If the user reports a Revit model-open failure, the first diagnostic step is the Revit
  journal file on the Windows host — not the container pipeline or repo code.

---

## Agent runtime location requirement

Before executing any task, agents MUST confirm:

- `pwd` returns `/workspace`
- Python version matches container environment
- Tests pass via `uv run pytest`

If these conditions are not met, STOP and correct environment before proceeding.

---

## Agent Memory Policy

Agents must NOT rely on external or hidden memory systems
(e.g., Claude project memory, IDE extensions, or local caches)
as a source of truth.

All persistent knowledge must be written to:
- PROJECT_MEMORY.md
- /docs/
- /sessions/

The Git repository is the only authoritative memory.
