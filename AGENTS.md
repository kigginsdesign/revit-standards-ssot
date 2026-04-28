# AGENTS.md — Hard Rules for Coding Agents

This file contains non-negotiable constraints for any AI coding agent (Claude, Cursor,
Copilot, etc.) working in this repository.

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
