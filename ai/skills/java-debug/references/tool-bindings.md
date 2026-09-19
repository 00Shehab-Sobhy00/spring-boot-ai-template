# Debug Tool Bindings

> **This is the only vendor-specific file in this skill.** `SKILL.md` describes the method;
> this file maps that method onto whatever debug provider is actually connected.
> Swapping providers means editing this file only.
>
> Loaded on demand (level 3) — it costs nothing until a live debug session is actually happening.

## How to use this file

1. Look at your available tools and identify which provider below matches (or none).
2. Use that section's table to translate the steps in `SKILL.md` into real tool calls.
3. If your provider isn't listed, use the **Capability Contract** at the bottom to map it
   yourself — then add a section here so the next person doesn't repeat the work.

---

## Provider: IntelliJ via Amplicode Spring Agent Toolkit

Tools appear under an `intellij-debug` MCP server. Harnesses that flatten MCP tools into a single
list prefix them, e.g. `mcp__intellij-debug__add_breakpoint`.

**Setup:** requires the Amplicode IntelliJ plugin (IntelliJ IDEA Ultimate/Community or GigaIDE),
installed from the vendor marketplace, then "configure Spring Agent" from the plugin's welcome
screen, then an MCP-client restart. If a bundled `amplicode-install` skill is registered, invoke
it and let it walk the user through this.

### Session

| Capability | Tool | Parameters |
| --- | --- | --- |
| Initialize | `initialize` | `projectPath` (absolute path to project root) |
| List sessions | `list_debug_sessions` | — returns names + `isSuspended` |
| Stop session | `stop_debug_session` | `sessionName` |

### Run configurations

| Capability | Tool | Parameters |
| --- | --- | --- |
| List run configs | `list_run_configurations` | — |
| Start in debug mode | `debug_run_configuration` | `configurationName` (exact) |

**Breakpoints** (line numbers are **1-based**; paths absolute or project-relative)

| Capability | Tool | Parameters |
| --- | --- | --- |
| List | `list_breakpoints` | — |
| Add | `add_breakpoint` | `filePath`, `line`, `condition` (optional) |
| Remove | `remove_breakpoint` | `filePath`, `line` |
| Enable/disable | `toggle_breakpoint` | `filePath`, `line`, `enabled` (optional) |
| Set condition | `set_breakpoint_condition` | `filePath`, `line`, `condition` (empty string removes) |

**Execution control** — all take an optional `sessionName` (defaults to first active session)

`resume` · `pause` · `step_over` · `step_into` · `step_out`

### Inspection

| Capability | Tool | Parameters |
| --- | --- | --- |
| Where am I | `get_current_position` | `sessionName?` — returns file, line, isSuspended |
| Call chain | `get_stack_trace` | `sessionName?` — frames with file, line, description |
| Threads | `list_threads` | `sessionName?` |
| Evaluate | `evaluate_expression` | `expression`, `sessionName?`, `frameIndex?` (0-based, default 0) |

### Known limitations of this provider

- **No console output.** stdout/stderr of the debugged app is not exposed. Work around it by
  reading log files directly, evaluating expressions to check state, or asking the user what the
  IDE console shows.
- **No breakpoint-hit events.** Nothing is pushed when a breakpoint is hit. After any action that
  might trigger one (resume, an HTTP call, starting the session), explicitly check
  `get_current_position` or `list_debug_sessions`. Do not poll on a timer — check after each
  relevant action.

---

## Provider: generic DAP-based server

Servers built on the Debug Adapter Protocol expose DAP-shaped operations. Names vary by
implementation; the shapes are consistent.

| Capability | Typical DAP operation |
| --- | --- |
| Attach / launch | `attach` / `launch` |
| Set breakpoints | `setBreakpoints` (takes an array per source file — replaces, not appends) |
| Continue | `continue` |
| Step | `next` (over), `stepIn`, `stepOut` |
| Stack | `stackTrace` |
| Variables | `scopes` then `variables` (two calls — scopes first) |
| Evaluate | `evaluate` (with `frameId` from `stackTrace`) |
| Threads | `threads` |

Two DAP-specific traps worth knowing:

- `setBreakpoints` sets the **complete list** for a file. Sending one breakpoint clears the
  others in that file.
- Variables come from `scopes` → `variables`, not a single call. Budget two round trips.

---

## Provider: none connected

There are no debug tools. Do not attempt Route A. Use Route B (reproduce in a test) or Route C
(read and instrument) from `SKILL.md`, and mention once — without nagging — that connecting a
debug MCP would allow live inspection.

---

## Capability Contract

If your provider isn't listed above, map it against these seven capabilities. Anything that
provides all seven can run Route A unchanged; a provider missing some can still run the parts
that don't need them.

| # | Capability | Needed for | If missing |
| --- | --- | --- | --- |
| 1 | Start or attach a debug session | Everything in Route A | Route A impossible — use B or C |
| 2 | Set a breakpoint at file+line | A1, A2 | Route A impossible |
| 3 | Conditional breakpoints | Efficient A1 | Workable, just far more resume cycles |
| 4 | Report current position + suspended state | Rules 2, 3, 4 | **Do not use Route A** — you cannot honor the safety rules blind |
| 5 | Step over / into / out | A1 step 8, A2 | Breakpoints-only debugging; set more of them instead |
| 6 | Read the stack trace | A1 step 7, A2 step 4 | Much weaker, still usable |
| 7 | Evaluate an expression in a frame | A1 step 6 | Fall back to reading variables, or to Route C logging |

**Capability 4 is the hard requirement.** Without a way to ask "am I suspended, and where?",
Rules 2–4 cannot be followed and a live session will eventually hang the agent. Prefer Route B.

## Adding a new provider

Add a section above with: how the tools are named/prefixed, a capability→tool table, the setup
steps, and any provider quirks (things it cannot do, or does surprisingly). Then note the
provider in `ai/PROJECT_MEMORY.md` under Environment Quirks so the team knows what is wired up.
