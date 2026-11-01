# gb: GarageBand project inspector

Read-only CLI for `.band` projects. Python 3.9+, standard library only.

- Test: `PYTHONPATH=src python3 -m unittest discover -s tests`. Tests run against the real projects on this Mac (`~/Documents/Songs/GarageBand`, `~/Music/GarageBand`).
- Load the `skill-utils:test-writing` skill before adding or editing any test, and follow it. The plugin is declared in `.claude/settings.json`.
- Apple's system Python keeps bytecode in `~/Library/Caches/com.apple.python/<project path>/`, not `__pycache__`. An edit that keeps file size and lands in the same second as the last compile runs stale code: after quick revert-style edits, delete that folder.
- Read-only is the product's core promise: every file access goes through `project._read_bytes`, which opens in `rb` mode. The bundle-fingerprint test enforces this for every command in `cli.COMMANDS`.
- Before touching `ProjectData` parsing, read `docs/format.md`. Record every confirmed or overturned format finding there.

## Gap loop

A **gap** is anything `gb` gets wrong or can't show while we use it: a crash, wrong output, an unrecognised chunk or plugin, an unnamed parameter. Each gap goes through the loop:

1. File it: `gh issue create --label gap` with the command run, the project, expected vs actual output, and any bytes or offsets involved.
2. If the fix needs ground truth from the user in GarageBand (changing knobs and saving a copy), add the `needs-ground-truth` label, tell the user what session it needs, and stop there.
3. Otherwise start a background Agent with `isolation: "worktree"`, giving it the issue number and this brief: read the issue and `docs/format.md`; fix on branch `fix/<issue>-<slug>`; `gh pr create` with `Closes #<issue>` in the body; work through the ready-to-merge checklist below; report the PR URL and the checklist outcome.
4. When the agent reports, confirm each checklist item was met, then merge and post the PR link to the user.

## Ready to merge

A PR is **ready** when every item holds, in this order, for every PR including the gap loop's:

1. The full test suite passes.
2. Every added or changed test was written with `skill-utils:test-writing`.
3. Changed output was checked against real projects; for new `ProjectData` decoding, against GarageBand itself where possible.
4. `/code-review` has run on the PR, and each finding is fixed or answered on the PR with the reason it stands. Re-run after fixes until a review reports no new findings; after any fix, re-check items 1 to 3.

Then squash-merge without asking (the user has authorised this) and post the PR link to the user.
