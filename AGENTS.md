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
