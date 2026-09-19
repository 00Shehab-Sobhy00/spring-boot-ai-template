# Prompt: Bug Investigation

Paste this (filling the placeholders) when you want a structured root-cause investigation instead of
a quick guess-and-patch.

---

Investigate this bug using the method below. Do not propose a fix until step 5.

**Bug report:**

- Observed behavior: `<what actually happens>`
- Expected behavior: `<what should happen>`
- Environment: `<local / staging / prod>` — remember local/staging differ from prod in proxies,
  mesh, and timeouts (`docs/deployment/networking.md`)
- Reproduction: `<steps or "unknown">`
- First seen / frequency: `<when, how often>`
- Relevant logs / stack trace: `<paste>`

**Method:**

1. **Read before theorizing.** Read the code path involved end to end (controller → service →
   repository/client), plus `ai/PROJECT_MEMORY.md` for known gotchas that might explain this.
2. **Form 2–3 concrete hypotheses**, ranked by likelihood, each with the specific evidence that
   would confirm or kill it.
3. **Gather evidence** — logs, a targeted test, or a live debug session via the `java-debug` skill.
   Prefer the cheapest evidence that discriminates between hypotheses.
4. **Confirm the root cause** — state it precisely: what happens, under which condition, and why the
   code allows it. "It's a race condition somewhere" is not a root cause.
5. **Propose the fix** — smallest change that fixes the root cause (not just the symptom),
   consistent with `ai/BACKEND_RULES.md`. Separate: required fix vs optional hardening.
6. **Regression protection** — a test that fails on the old code and passes on the fix, per
   `ai/TESTING.md`.
7. **Capture the learning** — if the root cause reveals a durable gotcha, propose an entry for
   `ai/PROJECT_MEMORY.md`.

Do not fix unrelated issues you notice along the way — list them under Notes instead
(`ai/AI_BEHAVIOR.md`, Scope Discipline).
