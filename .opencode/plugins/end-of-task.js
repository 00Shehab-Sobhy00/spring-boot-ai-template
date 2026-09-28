// opencode adapter for the end-of-task nudge. The logic lives in scripts/end-of-task-check.py;
// this file only runs it when a session goes idle and, if docs are missing, sends its message back
// into the session. The script stays quiet on a change set it already nudged, so this cannot loop.
export const EndOfTask = async ({ client, $, worktree }) => ({
  event: async ({ event }) => {
    if (event.type !== "session.idle") return
    const sessionID = event.properties?.sessionID
    if (!sessionID) return
    const py = process.platform === "win32" ? "python" : "python3"
    const run = await $`${py} scripts/end-of-task-check.py --format text`.cwd(worktree).nothrow().quiet()
    const text = run.stdout.toString().trim()
    if (run.exitCode !== 1 || !text) return
    await client.session.prompt({ path: { id: sessionID }, body: { parts: [{ type: "text", text }] } })
  },
})
