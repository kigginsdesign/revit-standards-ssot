# STATE.md — Current Project State

Last updated: 2026-04-27

This file is the dynamic ledger. It changes every session.
For project constants, see PROJECT_MEMORY.md. For agent coordination, see ORCHESTRATION.md.

---

## Active execution focus

What Max is currently working on, or the next thing queued for Max.

*None yet — pre-execution phase. Repo skeleton and governance docs are in place; awaiting first real pyRevit extraction run to provide ingest test data.*

---

## Last execution outcome

Most recent Max session: what changed, what surprised, what's still open.

*None yet.*

---

## Open questions — architectural (Q's queue)

- How will approved YAML be consumed downstream? (Dynamo scripts, shared parameter files, etc.)
- Should `exports/raw/` be git-tracked or gitignored? (Likely gitignored for large repos — confirm before first real ingest.)
- Will we need a review UI for proposed→approved workflow, or is DB + CSV sufficient for MVP?

---

## Open questions — tactical (Sage's queue)

*None yet.*

---

## Recent decisions

Rolling log, most recent first. Architecturally significant decisions get promoted to PROJECT_MEMORY.md "Key architectural decisions"; tactical decisions stay here.

*None yet logged in this format.*

---

## Progress

Checklist of MVP milestones.

- [x] Repo skeleton created
- [x] Markdown governance docs written (PROJECT_MEMORY, AGENTS, README)
- [x] ORCHESTRATION.md and STATE.md created
- [x] Dev container configured
- [x] Python package scaffolded (models, db, ingest, export stubs)
- [x] pytest stubs written
- [ ] First real pyRevit extraction run
- [ ] First real ingest run against real data
- [ ] Parameter records reviewed and approved
- [ ] First YAML output generated
