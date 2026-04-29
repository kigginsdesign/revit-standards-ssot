# Revit Standards SSOT

Single source of truth for Revit shared parameter definitions.

## What this is

A read-only pipeline that extracts shared parameter data from Revit via pyRevit,
validates and stores it in a local SQLite database, and generates YAML outputs for
approved parameters only.

**MVP scope: Shared Parameters only.**

## Architecture overview

```
Revit + pyRevit  →  exports/raw/*.json  →  ingest  →  SQLite DB  →  YAML / CSV
 (external)           (immutable)          (Python)   (SQLAlchemy)   (approved only)
```

Raw JSON exports under `exports/raw/` are immutable evidence. No pipeline script
modifies them in place.

## Quick start (dev container)

Prerequisites: Docker + VS Code with Dev Containers extension.

1. Open this repo in VS Code.
2. When prompted, click **Reopen in Container** (or run `Dev Containers: Reopen in Container`).
3. The container installs Python 3.12 and `uv`. Post-create runs `uv sync`.
4. Run tests:

```bash
uv run pytest
```

## Quick start (local, no container)

Requires Python 3.11+ and `uv`.

```bash
uv sync
uv run pytest
```

## pyRevit extraction

pyRevit scripts live in `scripts/pyrevit/`. They must be run inside Revit on a Windows
machine with pyRevit installed. They cannot run inside the dev container.

The extraction script must be exposed through a pyRevit extension button workflow, with
`REVIT_SSOT_REPO` set to the repository root. Extraction uses Revit's
`SharedParameterElement` API via `FilteredElementCollector`, not `ParameterBindings`, and
writes raw JSON evidence to the repo `exports/raw/` directory.

See `scripts/pyrevit/README.md` for instructions.

## Status values

| Status     | Meaning                                         |
|------------|------------------------------------------------|
| raw        | Imported from Revit, not yet reviewed           |
| proposed   | Under review                                    |
| approved   | Canonical — included in YAML output             |
| deprecated | Retired — excluded from YAML output             |

## Key rules

- GUID is the sole stable identifier. Never use Revit ElementId as a persistent key.
- Only records with `status = approved` appear in generated YAML.
- `exports/raw/` is read-only. Do not modify files there.

## Development Environments

This project uses a dual-environment model:

### 1. Dev Container (Primary)

All development work is done inside the VS Code Dev Container.

Includes:
- Python runtime
- uv-managed environment
- pytest
- SQLAlchemy / Pydantic pipeline

Run:

```bash
uv run pytest
```

### 2. Windows Host (Revit Only)

Used only for:

- Revit 2026
- pyRevit extraction scripts

The extraction step outputs JSON into:

```
exports/raw/
```

which is then consumed by the container pipeline.
