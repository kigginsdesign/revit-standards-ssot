# ORCHESTRATION.md — Multi-Agent Coordination

This file describes how the AI agents working on this project coordinate.
It's the constitution for who does what, how they hand off, and where shared state lives.

Read this at session start, alongside PROJECT_MEMORY.md and STATE.md.

---

## The cast

### Q — architect
- **Surface:** Gemini chat (Gem: "Revit Standards SSOT")
- **Role:** System design and architecture consulting.
- **Mandate:**
  - Reasons about high-level structure, technology choices, integration patterns
  - Surfaces architectural risks and tradeoffs
  - Audits decisions before they get implemented
- **Does not:**
  - Write code
  - Make tactical implementation decisions (those are Sage's domain)
  - Update STATE.md or commit to the repo

Q's role is intentionally sparse. Q gets consulted at strategy moments and
during architecture audits. During steady-state execution, Q is dormant.

### Sage — tactical lead
- **Surface:** ChatGPT chat (Project: "Revit Standards SSOT")
- **Role:** Brainstorming, planning, task specification, audit of Max's work.
- **Mandate:**
  - Receives architectural decisions from Q (via the user) and translates them into actionable plans
  - Produces task specs for Max
  - Audits Max's execution outcomes
  - Surfaces tactical questions back to the user
- **Does not:**
  - Write code (only specifies it)
  - Make architectural decisions (escalates to Q)
  - Update STATE.md or commit to the repo (the user does this for Sage's contributions)

### Max — executor
- **Surface:** Claude Code, running inside the dev container in this repo
- **Role:** Execution. Touches files, runs code, runs tests, commits.
- **Mandate:**
  - Receives task specs from Sage (via the user) and executes them
  - Reports execution outcomes via STATE.md updates and session logs
  - Respects every rule in AGENTS.md
- **Does not:**
  - Make architectural decisions (escalates back to the user)
  - Expand scope beyond the current task
  - Skip tests, linting, or commit hygiene

### The human — orchestrator and audience
The user routes between agents, holds final-call authority, and is the
audience for brainstorming and reporting. The user is **not** a message bus —
agents should not assume the user will manually relay state between them.
Shared state goes through STATE.md and the repo.

---

## Where state lives

| File | Role | Update cadence |
|---|---|---|
| `PROJECT_MEMORY.md` | Project constants — Mission, MVP, architectural decisions, repo layout | Rarely (when scope/architecture changes) |
| `AGENTS.md` | Hard codebase rules — non-negotiable constraints for any AI agent in this repo | Rarely (when rules change) |
| `ORCHESTRATION.md` | This file — agent roles, handoff formats, session lifecycle | Rarely (when orchestration model changes) |
| `STATE.md` | Dynamic state — active focus, last execution outcome, open questions, recent decisions, progress | Every session close |
| `sessions/YYYY-MM-DD_<agent>_<topic>.md` | Per-session logs from each agent's perspective | Each substantive session creates one |

---

## Session lifecycle

### Q's sessions (architecture / strategy)
- **Read at start:** PROJECT_MEMORY.md, ORCHESTRATION.md, STATE.md. AGENTS.md if relevant to the architectural question.
- **Update at close:** Produce a session log block for `sessions/YYYY-MM-DD_q_<topic>.md` (the user creates the file). Update STATE.md "Open questions — architectural" section.

### Sage's sessions (tactical / brainstorm)
- **Read at start:** PROJECT_MEMORY.md, ORCHESTRATION.md, STATE.md, most recent session log. AGENTS.md when planning Max's work.
- **Update at close:** Produce a session log block for `sessions/YYYY-MM-DD_sage_<topic>.md` (the user creates the file). Update STATE.md "Active execution focus" and "Open questions — tactical".

### Max's sessions (execution)
- **Read at start:** AGENTS.md (auto-loaded by Claude Code), STATE.md, most recent session log. PROJECT_MEMORY.md as needed.
- **Update at close:**
  1. Create `sessions/YYYY-MM-DD_max_<topic>.md` with execution log.
  2. Update STATE.md: "Last execution outcome", "Recent decisions" (if any), checked items in "Progress".
  3. Commit changes (code + session log + STATE.md update) with a clear message.

---

## Handoff formats

### Q → Sage (architectural briefing)
When Q has produced architectural guidance for Sage to act on, Q outputs in two parts:

> **Commentary (for the user only):**
> Reasoning, alternatives considered, things uncertain, side notes.
>
> **Briefing for Sage:**
> Self-contained block. No "I" or "we discussed" references. Includes: the architectural decision, the rationale, the constraints, and any open questions Sage should hold while planning.

The user copies the briefing block (only) into the Sage session.

### Sage → Max (task spec)
When Sage has a task ready for Max, output:

> **Commentary (for the user only):**
> Why this approach, alternatives, tradeoffs.
>
> **Task spec for Max:**
> - **Goal:** what success looks like
> - **Files in play:** specific paths Max should read or modify
> - **Constraints:** rules from AGENTS.md or PROJECT_MEMORY.md that apply
> - **Acceptance criteria:** how to know the task is done (tests pass, specific outputs, etc.)
> - **Out of scope:** what NOT to do as part of this task
> - **Open questions:** anything Max should escalate back

The user copies the task spec block (only) into the Max session.

### Max → Sage (execution report)
At the end of an execution session, Max produces:

> **Execution report:**
> - **What was done:** files changed, tests added/passing, commits made
> - **What surprised:** anything unexpected during execution
> - **What's still open:** outstanding work, deferred items
> - **Questions for Sage:** any tactical decisions that need Sage's input next session

This goes into the session log file. The user references it when starting the next Sage session.
