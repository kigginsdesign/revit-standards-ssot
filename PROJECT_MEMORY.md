# PROJECT_MEMORY.md — Canonical Project State

Last updated: 2026-04-28

---

## Mission

Build a read-only pipeline that extracts Revit shared parameter definitions from a live
Revit model via pyRevit, validates them, stores them in a local SQLite database, and
generates YAML outputs for approved parameters.

---

## MVP Definition (locked)

| Dimension        | Decision                                             |
|------------------|------------------------------------------------------|
| Scope            | Shared Parameters only                               |
| Volume           | 10–20 parameter tracer bullet                        |
| Pipeline mode    | Read-only (no Revit write-back)                      |
| Raw exports      | Immutable JSON under exports/raw/                    |
| Database         | SQLite (local)                                       |
| ORM              | SQLAlchemy                                           |
| Validation       | Pydantic                                             |
| Tests            | pytest                                               |
| YAML output      | Generated only for status = approved records         |
| Status values    | raw, proposed, approved, deprecated                  |
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
exports/raw/*.json are written once by pyRevit and never modified. All downstream
processing reads from these files and writes to the database.

**Extraction is external**
pyRevit cannot run inside a Docker container (requires Windows + Revit). The extraction
step is manual/external. The pipeline inside the container starts at ingest.

**YAML only for approved**
The YAML output is the published standard. Only parameters explicitly approved
(status = approved) appear there.

---

## Agent workflow

Three agents. Human orchestrates manually.

**Q** — strategist. Gemini Gem with GitHub repo RAG. Reviews PROJECT_MEMORY, AGENTS,
STATE at session start. Outputs clean copyable notes on what he would change in Sage's
instructions to Max. Consulted for architectural decisions — schema changes, new
dependencies, pipeline direction changes. Not involved in routine execution cycles.

**Sage** — consultant. ChatGPT project. Reads PROJECT_MEMORY, AGENTS, STATE, and last
session log at session start. Produces task instructions for Max as a clean copyable
block, commentary after. Runs closeout at session end (see docs/sage-project-instructions.md).

**Max** — executor. Claude Code in VSC. Reads AGENTS.md as hard rules. Takes plain text
instructions. Produces execution reports in the four-section format defined in AGENTS.md.

---

## Repository layout

.devcontainer/          Dev container config (Python 3.12 + uv)
docs/                   Architecture docs and agent instruction copies
data/schemas/           JSON schemas for raw export validation
db/                     SQLite database file (gitignored)
exports/raw/            Immutable pyRevit JSON exports
scripts/pyrevit/        pyRevit extraction scripts (run inside Revit, not container)
scripts/ingest/         CLI wrappers for ingest pipeline
scripts/reports/        Report generation helpers
src/revit_standards_ssot/  Python package
sessions/               Sage session logs (YYYY-MM-DD_sage_<topic>.md)
tests/                  pytest suite
user-notes/             Scratch notes, not version-controlled artifacts
