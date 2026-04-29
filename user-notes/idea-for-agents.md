You've named the right thing: the human role is ill-defined because you've collapsed two roles into one. There's "audience" (you receive brainstorming and reports, you push back and steer) and there's "courier" (you carry state from agent to agent). Audience is high-value — you should keep that. Courier is what's killing you.
The fix is that the repo becomes the message bus, and you become the audience instead of the wire. A few things stack on top of that:
1. The repo as shared substrate (the big move)
Once it's on private GitHub, Sage and Q both connect to it. ChatGPT supports GitHub as a data source for Plus/Pro accounts — Sage can read repo contents, browse files, and (with deep research / connectors) reason about diffs. Gemini's GitHub story is more uneven; the chat surface has had varying levels of repo integration depending on plan and rollout, so verify the current state for your account, but worst case the fallback is "Q reads a state file you maintain in the repo" rather than "you tell Q what's changed."
The architectural payoff: Sage and Q stop needing you to update them on what Max did. They look at the repo. You stop paying tokens to ferry state — you pay them to consult, which is what you actually want.
2. A state file in the repo
The repo by itself is a lot of context. Q doesn't want to read 40 files to find out what happened yesterday; Sage wants to know what's in flight, not browse the whole tree. Add a small file that lives in the repo and acts as the orchestration ledger — call it _orchestration/state.md or whatever fits. It captures:

Current architectural decisions (Q's domain)
Active execution focus (Sage's domain)
Last execution outcome from Max — what changed, what surprised, what's open
Cross-agent open questions

Max updates it as the last step of every Claude Code session (a closeout skill, basically the same pattern as learning-tracker.md). Q and Sage read it at the start of their sessions, before doing anything else. This file is the actual shared memory of the system; it's the bandwidth-control mechanism. Q doesn't need every move — Q needs this file plus the repo when relevant.
3. Q's output-format problem
The "here's what you should tell Sage" + commentary problem is a prompting issue, not a workflow issue. Q doesn't know who its audience is. Two ways to fix:
Option A — split outputs: tell Q every response has two parts, in this order:

Commentary (for the user only — reasoning, alternatives considered, things you're uncertain about)
Briefing for Sage (a self-contained block the user can paste verbatim — no meta-references to "I" or "we discussed")

With clear delimiters (markdown headings, fenced blocks). Then you copy the briefing block alone.
Option B — flip the default: Q's primary output is the clean briefing for Sage; commentary only if you ask. This works better if Q's commentary is mostly noise to you anyway.
Same pattern works the other direction — Sage producing task specs for Max should be in a delimited block, separate from any back-and-forth commentary with you.
4. Codify agent awareness
Each agent's system/project instructions should contain a paragraph naming the trio, the human's role, and where shared state lives. Something like, in Q's instructions:

You are Q, the architect. You consult on system design and overall strategy. Sage (ChatGPT) is the tactical lead who briefs Max (Claude Code) on execution. The user is the orchestrator and audience — they route requests, push back on your reasoning, and make final calls. They do not want to be a message bus between you and Sage. When relevant context exists in the repo at _orchestration/state.md, reference it rather than asking the user to summarize. When producing output destined for Sage, format it as a clean briefing block that the user can paste verbatim.

Parallel blocks in Sage's and Max's instructions. Cheap to write, immediate quality-of-life fix, prevents the "Q lecturing the user about what to tell Sage" failure mode because Q now knows the user is going to forward a delimited block, not the whole response.
5. Define your role explicitly
In the same instructions: name yourself the orchestrator. Say what you do (route, audience for brainstorming, audience for reports, final-call on architecture vs. execution). Say what you don't do (real-time message-passing). Once that's in the instructions, the agents stop optimizing for you-as-courier (which is what produces the "tell Sage this" wrapping) and start optimizing for you-as-audience (commentary directed at you, briefings clearly marked as forward-able).
6. Per-agent update cadence
Don't try to keep all three current continuously. The cadences should be different:

Q — refreshed at the start of strategy sessions only. Reads the state file + relevant slice of the repo. Doesn't need to know about Max's typo fixes.
Sage — refreshed at the start of brainstorm sessions. Reads state file + repo slice. Tighter feedback loop with Max via the state file.
Max — always current (he has the repo). Updates the state file at execution close. That's his contribution to keeping the others informed.

This is the lifecycle pattern you already use in this Project, applied to a multi-agent shape.
A note on Q's eventual fade
You're right that Q's role probably contracts as the system stabilizes. That's healthy — Q earns their keep during architecture work and audits, and steps out during steady-state execution. If you build the codification right (especially the state file), Q can stay dormant for stretches and come back without needing a full re-briefing — they read the state file, scan recent commits, and they're current. Versus the current setup where pulling Q back in after a gap means rebuilding their context manually.
Sequence I'd suggest
If you do these in priority order:

Get the repo on GitHub (you're already heading there).
Connect Sage to the repo via GitHub connector. Verify Q can do the same; if not, accept that Q reads via the state file you keep in the repo.
Write the state file format. Stub it now; it'll evolve.
Add codified-awareness blocks to all three agents' instructions, including the human role and the state-file convention.
Fix Q's output format with the two-part split.
Wire Max's closeout to update the state file (skill or just discipline).
Trial run on the next slice of work; adjust formats based on what's actually friction.

The reason to sequence it this way: 1–2 is the architectural change that makes the rest possible. 3–4 are the cheap codification wins that pay back immediately. 5–7 are quality-of-life improvements that you tune as you go.
You're not on too big a task. You're on a hard task and you've already done the architecturally hardest part (designing roles that don't overlap and assigning them to surfaces that fit). The "ok but not great" gap is mostly operational codification — handoff formats, shared state, role declarations — which is what every multi-agent system has to figure out. Once you have GitHub as the substrate, most of the remaining work gets easier because you've stopped being the wire.