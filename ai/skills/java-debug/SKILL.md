---
name: java-debug
description: >
  Investigate runtime behavior with a live debugger — breakpoints, stepping, inspecting variables,
  evaluating expressions — including the safety rules that stop a suspended process from hanging you.
  Use when debugging, tracing execution, or asking why code behaves unexpectedly at runtime.
metadata:
  when_to_use: ["debug", "breakpoint", "step through", "why is this null", "why does this crash", "trace execution", "inspect at runtime"]
---
<!-- evidence-token: SKJAVA-XZJVGV — cite in the AI Run Report -->

# Debugging a Running Application

This skill is **debugger-agnostic**. It describes the method and the safety rules; the specific
tool names come from whatever debug provider is connected in this environment.

## Preflight: What Can You Actually Do?

Check your available tools for debugger capabilities before planning anything. You are looking
for tools that let you: set breakpoints, start or attach a debug session, step, and read
variables. They may be named anything — `add_breakpoint`, `setBreakpoint`, `dap_set_breakpoints` —
and may carry the prefix of the MCP server that provides them.

Then pick your route:

| Situation | What to do |
| --- | --- |
| Debug tools are present | Read `references/tool-bindings.md` to map this skill's steps onto the actual tool names, then proceed with Route A. |
| No debug tools, but the project runs locally | Use **Route B: reproduce in a test**. Often faster than a live session anyway. |
| No debug tools and you can't run the project | Use **Route C: read and instrument**, and tell the user what a debug provider would add. |

Never block the whole task because a debugger isn't wired up. Routes B and C solve most bugs.

## SAFETY RULES — Read Before Any Live Session

These exist because a debugged process **stops responding entirely** while suspended on a
breakpoint. Every one was learned by someone hanging their own session.

**Rule 1 — Always use timeouts when talking to the debugged app.**
`curl --max-time 5`, or run the call in the background. Do this even if you just verified the app
was running: it can hit a breakpoint in the gap between your check and your request.

**Rule 2 — Check suspension status before any network call to the app.**
If the session is suspended, resume it first or accept that your request will block until
something releases it.

**Rule 3 — Verify position after every step.**
Never assume where execution landed. Stepping can jump to an unexpected line, a different file,
or into framework code.

**Rule 4 — Re-check status after resuming.**
The app may immediately hit another breakpoint. "I resumed it" is not the same as "it is running".

**Rule 5 — Expression evaluation executes real code.**
Evaluating an expression runs it inside the live process. Avoid anything that mutates state —
setters, methods with side effects, anything that could terminate the process — unless that is
precisely your intent.

**Rule 6 — Clean up.**
Remove the breakpoints you added and stop the session when done. Leftover breakpoints ambush the
next person, or the next session.

## Route A: Live Debug Session

### A1 — Bug at a known location

1. Read the source around the suspicious area first. Understand the code before suspending it.
2. Set a breakpoint at the line of interest. **Use a conditional breakpoint** if the bug only
   occurs for certain inputs — it saves dozens of resume cycles.
3. Start the debug session.
4. Trigger the bug — respecting Rule 1 if you trigger it over HTTP.
5. Confirm the breakpoint was hit and you are where you expected (Rule 3).
6. Inspect: start with plain variable names, then build up to expressions. Respect Rule 5.
7. Read the stack trace to understand how execution got here — often more informative than the
   local variables.
8. Decide: step further, move the breakpoint, or conclude.
9. Clean up (Rule 6).

### A2 — Understanding unfamiliar code

1. Find how the app starts (run configurations, main class, or the documented start command).
2. Breakpoint the entry points: controller methods, listeners, `main`.
3. Start the session and trigger the flow.
4. Read the full stack trace first — it maps the call chain in one shot.
5. Step *into* your own code, step *over* framework code, step *out* when you have seen enough.
6. Inspect arguments and return values at each interesting frame.
7. Verify position after each step (Rule 3).

## Route B: Reproduce in a Test (no debugger needed)

Often superior to a live session: repeatable, survives the session, and becomes the regression
test you needed anyway.

1. Write a focused test that reproduces the failure — see `ai/skills/create-integration-test/`.
2. Assert the wrong behavior explicitly, so the test currently fails for the right reason.
3. Narrow it: remove pieces until the smallest failing case remains.
4. Fix, confirm the test passes, and keep the test.

If the bug only reproduces against real infrastructure, Testcontainers usually gets you there.

## Route C: Read and Instrument

When you can neither debug nor easily reproduce:

1. Trace the code path by reading, from entry point to failure point. State your hypothesis.
2. Ask the user to add temporary logging at the two or three decision points that would
   discriminate between hypotheses — and to paste back what it prints.
3. Use existing evidence: application logs, stack traces, correlation ids, metrics.
4. Be explicit that you are reasoning from inference, not observation.

## Expression Evaluation Tips

- Evaluation generally works only while suspended.
- Most debuggers let you evaluate in a *caller's* frame, not just the current one — useful when
  the interesting state is one level up.
- Start simple. A failed complex expression tells you nothing about which part was wrong.
- Framework, native, and optimized frames often refuse evaluation. Move to a different frame.

## Error Recovery

| Symptom | Likely meaning | Action |
| --- | --- | --- |
| Session not found | No session running, or the name is wrong | List sessions; start a new one if needed |
| Not suspended | Breakpoint not hit yet, or already resumed | Wait for the trigger, or pause the session |
| Evaluation unavailable | Current frame does not support it | Try a different frame |
| Session died | The app crashed or was killed | Check the app/IDE logs, then start a fresh session |
| Your request hangs | You violated Rule 1 or 2 | The app is suspended; resume it |

## Multiple Sessions

If more than one debug session can be active, always name the session explicitly in tool calls.
Defaults pick "the first one", which is rarely the one you meant.

## Don't

- Don't start a live session when a failing test would answer the question faster
- Don't evaluate state-mutating expressions to "just check something"
- Don't assume the breakpoint was hit — verify
- Don't leave breakpoints or sessions behind
- Don't block the task because no debug MCP is connected — take Route B or C

## Related

`references/tool-bindings.md` (map these steps to your actual tools) ·
`ai/prompts/bug-investigation.md` (the wider root-cause method) ·
`ai/skills/create-integration-test/` (Route B) · `ai/PROJECT_MEMORY.md` (record what the bug taught
you)
