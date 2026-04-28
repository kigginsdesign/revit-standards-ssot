# PROJECT_MEMORY.md — Canonical Project State

Last updated: 2026-04-27

---

## Mission

Build a read-only pipeline that extracts Revit shared parameter definitions from a live
Revit model via pyRevit, validates them, stores them in a local SQLite database, and
generates YAML outputs for approved parameters.

---

## MVP Definition (locked)

| Dimension        | Decision                                             |
|------------------|------------------------------------------------------|
| Scope            | Shared Parameters **only**                           |
| Volume           | 10–20 parameter tracer bullet                        |
| Pipeline mode    | Read-only (no Revit write-back)                      |
| Raw exports      | Immutable JSON under `exports/raw/`                  |
| Database         | SQLite (local)                                       |
| ORM              | SQLAlchemy                                           |
| Validation       | Pydantic                                             |
| Tests            | pytest                                               |
| YAML output      | Generated only for `status = approved` records       |
| Status values    | `raw`, `proposed`, `approved`, `deprecated`          |
| Primary key      | GUID (UUID string) — never Revit ElementId           |
| Revit version    | Revit 2026 + pyRevit (external, not containerized)   |

---

## What is NOT in MVP

- Project parameters
- Family parameters
- Revit write-back of any kind
- Remote/cloud database
- Web UI or API
- Multi-user workflows
- Any Revit element types other than shared parameters

---

## Key architectural decisions

**GUID as sole identifier**
Revit ElementIds are session-scoped and not stable across file versions. GUID is the
only field that identifies a shared parameter across Revit files and versions.

**Immutable raw exports**
`exports/raw/*.json` are written once by pyRevit and never modified. All downstream
processing reads from these files and writes to the database. This preserves an
audit trail.

**Extraction is external**
pyRevit cannot run inside a Docker container (requires Windows + Revit). The extraction
step is manual/external. The pipeline inside the container starts at ingest.

**YAML only for approved**
The YAML output is the "published standard." Only parameters explicitly approved
(`status = approved`) appear there. Raw and proposed records live in the DB only.

---

## Repository layout

```
.devcontainer/          Dev container config (Python 3.12 + uv)
docs/                   Architecture and design docs
data/schemas/           JSON schemas for raw export validation
db/                     SQLite database file (gitignored)
exports/raw/            Immutable pyRevit JSON exports (gitignored or tracked read-only)
scripts/pyrevit/        pyRevit extraction scripts (run inside Revit, not container)
scripts/ingest/         CLI wrappers for ingest pipeline
scripts/reports/        Report generation helpers
src/revit_standards_ssot/  Python package
tests/                  pytest suite
sessions/               Per-session work logs
```
