# Write a New Skill

## Before You Write Anything

**Only write a skill for a task you have actually done at least twice.** A skill invented from
imagination encodes guesses; a skill extracted from real work encodes decisions. If the task hasn't
come up twice yet, put a note in `ai/PROJECT_MEMORY.md` and wait.

Then check the three ways this might already be covered:

- Is there an existing skill that should be *extended* rather than duplicated? (Adding a section
  beats a near-identical sibling.)
- Is this a *pattern* question ("why do we do it this way") rather than a *recipe* question ("how do
  I do it here")? Patterns go in `ai/patterns/`.
- Is this a whole analytical workflow (a full security pass, a root-cause hunt) rather than a build
  task? Those go in `ai/prompts/`.

## Steps

1. **Create the folder**: `ai/skills/<kebab-case-name>/SKILL.md`. The folder name is the skill name
   and becomes the slash command (`/create-rest-api`). Name it `<verb>-<noun>` — `add-webhook`,
   `optimize-query`, `review-migration`.

2. **Write the frontmatter — keep it under ~100 tokens.** This is the only part loaded in every
   session, forever, whether or not the skill runs. Its single job is to answer *"is this skill
   relevant to what the user just asked?"*

   ```yaml
   ---
   name: add-webhook
   description: >
     Add an outbound webhook with signing, retries, and delivery logging,
     following this repo's integration conventions.
     Use when exposing events to an external system via HTTP callback.
   metadata:
     when_to_use: ["add a webhook", "notify an external system", "callback URL"]
   ---
   ```

   Rules for the description:
   - Say **what it does** and **when it applies**. Nothing about *how*.
   - Include the words a person would actually type. `metadata.when_to_use` exists to catch informal
     phrasings the description misses (`metadata` is the spec-sanctioned place for custom keys; a
     bare top-level `when_to_use` is rejected by strict loaders).
   - Do not list the implementation steps — that's the body, and the body is free until triggered.
   - Do not pad with "following best practices" or "in a production-ready way" — those words match
     everything, so they help the model match nothing.
   - **`when_to_use` must be a valid YAML list — wrap it in `[...]`.** `when_to_use: "a", "b", "c"`
     is *not* valid YAML (it parses as a scalar followed by a stray comma) and will fail to load.
     Always write `when_to_use: ["a", "b", "c"]`.
   - Before saving, sanity-check the frontmatter parses:
     `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"` should run
     with no error.

3. **Write the body.** Length is not a constraint here (it loads conditionally), but it should be
   scannable. Use the house structure every skill in this repo follows:

   ```markdown
   # <Imperative Title>

   One line naming the authoritative files this skill applies, e.g.
   "Follows `ai/ARCHITECTURE.md` (layering) and `ai/patterns/rest-api.md`."

   ## Steps
   1. ... 8. ...

   ## Don't
   - The 3-4 mistakes actually made on this task

   ## Related
   `path/one` · `path/two` · `path/three`
   ```

4. **Link, never restate.** If a rule already lives in `ai/BACKEND_RULES.md`, cite the path — do not
   copy the text in. Copies cost tokens twice when both files load, and they drift the moment one is
   edited. Every path you cite must exist; CI fails the build on a broken reference from
   `AGENTS.md`.

5. **Make each step decidable.** "Handle errors properly" is not a step. "Map downstream 5xx to our
   502 with `origin: EXTERNAL` per `docs/api/error-catalog.md`" is. If a step can't be checked as
   done-or-not-done, rewrite it.

6. **Write the `Don't` section from real mistakes**, not from imagination. The best source is your
   own code reviews — anything you've had to say twice belongs here.

7. **Register it** in the Skills Map section of `AGENTS.md` (one line), and cross-link it from any
   related pattern or skill's `Related` line. A skill nothing points to is discoverable only by
   luck.

8. **Test the trigger.** Open a fresh session, phrase the request the way a teammate would, and
   confirm the right skill loads. If it doesn't fire, the description is the problem — not the body.
   Widen `when_to_use` with the phrasing that failed.

## Don't

- Don't write ten skills in one sitting — they'll all encode the same guess about how work is done
  here
- Don't put "how" in the description to make the skill "more discoverable" — it inflates the
  permanent floor and makes matching *worse*, because vague overlapping descriptions compete with
  each other
- Don't create a skill that only restates a rule file; link to the rule file instead
- Don't leave the skill unregistered in `AGENTS.md`

## Related

`AGENTS.md` (Skills Map) · `ai/patterns/` (for "why" content) · `ai/prompts/` (for full workflows) ·
`ai/PROJECT_MEMORY.md` (for knowledge not yet worth a skill)
