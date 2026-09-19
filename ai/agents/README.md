# Subagents — optional, and only when they pay for themselves

This folder is **empty by default, on purpose.** The template works fully without subagents; this
document exists so that adding them later is a decision rather than a reflex.

## What a subagent actually buys you

Exactly one thing that skills cannot provide: **a separate context window.** A subagent explores,
reads ten files, and returns a summary — the caller's context absorbs the summary, not the ten
files. Everything else people reach for subagents to get (a sequence of steps, layer-specific
conventions, a review checklist) is a skill, and a skill is cheaper.

So the question is never "should we have agents?" It's "is this task big enough that context
exhaustion is the binding constraint?"

| Situation | Use |
| --- | --- |
| Task spans layers but fits in one context | `deliver-feature` skill — no agent |
| Task needs a specific recipe (endpoint, consumer, migration) | The matching skill — no agent |
| A repeated checklist (review, security pass) | A skill or an `ai/prompts/` workflow — no agent |
| Cross-service work where exploring service A would flood the context you need for service B | **Subagent** — this is the real case |
| A long task where the agent starts forgetting earlier decisions | **Subagent**, to keep the plan in the caller and the digging in the callee |
| Publishing step needing a different toolset (MCP, CLI auth) | Optional subagent; the `create-merge-request` skill covers it without one |

For a single-module service, subagents are usually a net loss: each invocation is a fresh context
that re-reads the rule files and re-explores the code you already had loaded.

## The rule that keeps them from rotting

**Agents route. Skills rule.**

An agent file says *which* skill to use, in *what order*, and *when to hand back*. It must not
restate a coding convention, a layering rule, or a review checklist — those live in `ai/*.md` and
`ai/skills/` and are loaded by every adapter already.

This matters more than it sounds. The most common failure in agent-based setups is that four agent
files each carry their own copy of "controllers return `ResponseEntity`, use constructor injection,
entities use `@Getter`/`@Setter`." When the convention changes, three of the four are now lying, and
nothing in CI notices — an agent file is prose, not a checked reference. One authoritative file per
rule is the whole discipline of this template; an agent layer is the easiest place to lose it.

A good agent file is short. If yours is a page of rules, you've written a skill in the wrong folder.

## Shape of an agent, if you add one

```markdown
---
name: <role>
description: <when the caller should delegate here — one line>
mode: subagent          # or `primary` for the entry-point agent
---

You handle <narrow scope> for this repository.

Follow `AGENTS.md` and the skills below; they are authoritative — do not restate their rules here.

Use:
- `ai/skills/<skill>/` for <task>
- `ai/skills/<skill>/` for <task>

Return to the caller:
- what you changed
- what you verified, with exact commands
- what you did NOT do, and what the caller must reconcile
```

The "return to the caller" section is the part people skip and the part that makes delegation work.
A subagent that returns "done" has cost you a context window and given you nothing to reconcile
with.

The caller — not the subagent — is the one who writes the AI Run Report; see `ai/CAPACITY.md` →
"Subagent Handoff" for exactly how a subagent's result (and its budget) folds into that single
report.

## Placement, per tool

Agent definitions are **not** portable the way `AGENTS.md` and `SKILL.md` are — each tool has its
own location and frontmatter dialect. This is the main hidden cost of an agent layer in a multi-tool
repo, and the reason this template keeps its authoritative content in skills.

| Tool | Where agents live | Notes |
| --- | --- | --- |
| opencode | `.opencode/agents/*.md` | `mode: primary` / `mode: subagent`; set `default_agent` in `opencode.json` |
| Claude Code | `.claude/agents/*.md` | Similar frontmatter; supports per-agent tool restriction |
| Cursor / Copilot | — | No equivalent; these tools fall back to the skills, which is why the skills must stay complete |

Keep the authoritative workflow in `ai/skills/deliver-feature/` and let each tool's agent file be a
thin pointer to it. Then a repo with no agent support still delivers the same sequence.

## Adding an MCP server (the publishing case)

The one capability skills genuinely can't reach on their own is an external API — creating a merge
request, reading a ticket. That's an MCP server, and it's configured per tool, independent of
whether you use agents:

```jsonc
// opencode.json — sibling of "instructions" and "skills"
"mcp": {
  "<forge>": { "type": "remote", "url": "https://<host>/api/v4/mcp" }
}
```

Authentication is an environment variable, never a committed file. Document the required variables
in `docs/deployment/onboarding.md` so a new joiner sets them up once; `create-merge-request` handles
the case where they're missing by falling back to a ready-to-paste description rather than failing.

## If you decide to add them

Start with **one** primary agent that runs `deliver-feature`, and add a subagent only when you can
name the task where context ran out. Seven agents on day one is a configuration you will not be able
to debug — when output is wrong, you won't know which agent's instructions produced it.
