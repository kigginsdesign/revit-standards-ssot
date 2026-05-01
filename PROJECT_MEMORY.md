# PROJECT_MEMORY.md — Canonical Project State

Last updated: 2026-05-01 (session closeout)

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

**Extraction via SharedParameterElement**
Shared parameters are extracted using Revit's SharedParameterElement via
FilteredElementCollector rather than ParameterBindings. This ensures reliable detection
of parameters actually present in the model.

**Environment-variable-based repo resolution**
pyRevit scripts resolve the repository root using a REVIT_SSOT_REPO environment
variable. This avoids hardcoded paths and supports separation between pyRevit extension
location and repo SSOT.

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
docs/                   Architecture, workflow, and governance docs
docs/reports/           Analysis and audit reports (read-only after commit)
docs/decisions/         Durable governance decision packets
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

---

## Curation Workbench

The SQLite database is the **Curation Workbench** — the locked core architecture for
reconciling raw Revit evidence with firm standards.

**Formal lifecycle (8 stages):**
Raw Ingest → Preflight Audit → Decision Packet → Bulk Deprecation →
Propose Selection → Enrichment → Strict Promotion → YAML Export

For the full spec, see `docs/curation_workflow.md`.

**Two-tier validation model:**
- **Tier 1 — Evidence (ingest):** Tolerant. Accepts all records passing basic format
  validation. Unknown data_type values warned, not rejected. Source anomalies are review
  findings, not failures.
- **Tier 2 — Standard (promotion):** Strict. Future `promote.py` enforces
  `FIRM_STANDARD_DATA_TYPES`, mandatory `curation_note`, no duplicate approved names.

**Two-tier data type vocabulary:**
- `data_type` — immutable raw Revit evidence set during ingest. Never modified.
- `standard_data_type` — optional curated firm-standard mapping set during enrichment.
  Never replaces `data_type`.
- `RAW_REVIT_DATA_TYPES` — known raw Revit strings; used only for warning diagnostics
  during ingest. Not an approval allowlist.
- `FIRM_STANDARD_DATA_TYPES` — strict allowlist for `standard_data_type` during strict
  promotion. Not enforced until `promote.py` exists.

**Tool boundaries:**
- `bulk_curate.py` — messy curation. Deprecation only. Dry-run by default.
  Requires `--curation-note` on every `--apply`. No promotion to `approved`.
- `promote.py` — future strict approval gating. `proposed → approved` only.

**Governance artifact locations:**
- `docs/reports/` — analysis, audit findings, preflight summaries. Read-only after commit.
- `docs/decisions/` — durable governance decisions. Decision packets live here.

**Decision packet rules:**
- Decision packets with `Status: Proposed` do **not** authorize DB mutation.
  Explicit Sage/Shawn sign-off is required for each batch before `--apply` is run.
- After any `--apply` run, the same decision packet must be updated to `Status: Applied`
  with actual commands, timestamp, matched/applied counts, and verification results,
  committed in the same transaction.
- Source-file correction in Revit or shared-parameter `.txt` files is out of scope for MVP.
  For MVP, unwanted records are curated in the DB with `status = deprecated` + `curation_note`.

---

## Current status

- [x] Repo initialized and connected to GitHub
- [x] Dev container successfully built and validated (desktop and laptop)
- [x] Python pipeline fully operational inside container (55/55 tests passing)
- [x] Claude Code (Max) running inside Dev Container
- [x] First real pyRevit extraction run (806 parameters, 20260430_220917.json committed/pushed)
- [x] First real ingest run against real data (806 inserted, 0 rejected)
- [x] Runtime DB path bug fixed; test/runtime isolation guard added
- [x] RAW_REVIT_DATA_TYPES warning diagnostics; KNOWN_DATA_TYPES split
- [x] Data audit and curation preflight reports completed
- [x] Curation Workbench architecture locked (model fields, workflow spec, constants)
- [x] Bulk deprecation CLI (bulk_curate.py) implemented
- [x] First proposed deprecation decision packet (docs/decisions/20260501_deprecation_batch_1.md)
- [ ] Decision packet approval and first bulk deprecation apply
- [ ] Propose selection and enrichment workflows
- [ ] FIRM_STANDARD_DATA_TYPES vocabulary finalized
- [ ] promote.py strict approval tool
- [ ] Tracer-bullet parameter set approved
- [ ] First YAML output generated

---

## Environment model (locked)

- Windows host is used ONLY for:
  - Revit 2026
  - pyRevit execution

- Dev Container is used for:
  - All Python pipeline work
  - Testing (pytest)
  - Database interaction
  - YAML / CSV generation
  - Coding agent execution

- Local `.venv` on Windows is deprecated and should not be used going forward.

### Windows host operational notes

**Canonical repo path:** `C:\Dev\revit-standards-ssot`
This is the standardized path on all Windows machines. `REVIT_SSOT_REPO` must be set to
exactly this directory (the repo root), not a similarly named or parent folder.

**Revit/pyRevit failures are outside the container boundary.**
Agents may inspect repo code and ask the user for Revit journal output to assist
diagnosis, but must not assume repo Python code executes during Revit model open.
Startup hooks and event handlers are the only repo code that runs at model open.

**SQL Server LocalDB dependency for Revit 2026 steel connections.**
Revit 2026 Advance Steel / SteelConnections2026 workflows depend on SQL Server LocalDB.
After any Windows SQL cleanup, both SQL Server 2019 LocalDB and a newer LocalDB runtime
(2025 or later) may be required — the 2019 runtime is needed for compatibility with
existing Autodesk/Advance Steel LocalDB instances (MSSQL15E.LOCALDB). A Revit
model-open failure showing SQLLocalDB / SteelConnections2026 in the journal is a Windows
host issue, not a repo or container issue.
