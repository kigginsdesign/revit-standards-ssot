## Purpose

Implement and validate pyRevit shared parameter extraction and establish the correct Revit <-> container boundary.

## Decisions

- Use SharedParameterElement instead of ParameterBindings for extraction
- Keep extraction "dumb" (no source_file), assign metadata during ingest
- Use environment variable (REVIT_SSOT_REPO) to resolve repo path from pyRevit
- Execute pyRevit via extension button (not ad hoc script execution)
- Accept dual-agent setup (Claude + Codex fallback)

## What we did

- Fixed dev container auth (Claude Code + Codex)
- Installed Codex as fallback executor
- Implemented pyRevit extraction script
- Built pyRevit extension button for execution
- Diagnosed "0 parameters" issue -> identified binding vs definition gap
- Switched extraction method to SharedParameterElement
- Validated extraction in Revit (806 parameters exported)
- Fixed repo path issue via environment variable
- Confirmed pipeline boundary: Revit (manual) -> container (automated)

## Outstanding items

- First ingest run on real extracted JSON
- Review validation behavior against real-world parameter data
- Generate first review CSV
- Approve parameters and produce first YAML output

## Meta-observations

- Revit API edge cases surfaced early and validated architecture choice
- Environment boundary (Revit vs container) is now clearly enforced
- Agent tooling (Claude vs Codex) introduces operational variability but is manageable with strict gates
- Early enforcement of SSOT and immutability principles prevented downstream ambiguity
