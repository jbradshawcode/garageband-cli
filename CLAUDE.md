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
3. Otherwise start a background Agent with `isolation: "worktree"`, giving it the issue number and this brief: read the issue and `docs/format.md`; fix on branch `fix/<issue>-<slug>`; when the test suite passes, push and open a draft PR with `Closes #<issue>`; work through the ready checklist below, committing and pushing after every fix; report the PR URL, your worktree path, the checklist outcome, every review finding you answered instead of fixing, and anything that needs the user.
4. When the agent reports:
   - If it needs the user (ground truth, review cap), tell the user and leave the PR as a draft.
   - Otherwise run the test suite yourself inside the agent's worktree. If it fails, `gh pr ready --undo <n>` and hand the failure back to an agent.
   - If it passes, `git worktree remove <path>`, then merge as below.

## Ready to merge

Every PR opens as a draft (`gh pr create --draft`) and becomes **ready** (`gh pr ready <n>`) when this checklist holds on its final pushed commit:

1. The full test suite passes. Re-check after every push.
2. The PR description carries the `skill-utils:test-writing` verdict line for every added test, copied from the chat.
3. Changed output was checked against real projects; re-check after every push. New `ProjectData` decoding is confirmed against ground truth the user supplied (a screenshot, a diff session). If it needs fresh ground truth, label the PR `needs-ground-truth`, leave it as a draft and report it. Never open or drive GarageBand yourself: it can autosave the user's projects.
4. `/code-review high <n>` has run. Fix each finding, or answer it on the PR with the reason it stands, and push. Repeat until a run raises nothing you would fix, at most 3 runs per PR in total. If fixable findings remain after the third, the PR stays a draft for the user.

To merge a ready PR: squash-merge (`gh pr merge --squash --delete-branch`) without asking, as the user has authorised. Post the PR link to the user, listing any findings that were answered instead of fixed.
