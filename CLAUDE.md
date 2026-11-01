# gb: GarageBand project inspector

Read-only CLI for `.band` projects. Python 3.9+, standard library only.

- Test: `PYTHONPATH=src python3 -m unittest discover -s tests`. Tests run against the real projects on this Mac (`~/Documents/Songs/GarageBand`, `~/Music/GarageBand`).
- Apple's system Python keeps bytecode in `~/Library/Caches/com.apple.python/<project path>/`, not `__pycache__`. An edit that keeps file size and lands in the same second as the last compile runs stale code: after quick revert-style edits, delete that folder.
- Read-only is the product's core promise: every file access goes through `project._read_bytes`, which opens in `rb` mode. The bundle-fingerprint test enforces this for every command in `cli.COMMANDS`.
- Before touching `ProjectData` parsing, read `docs/format.md`. Record every confirmed or overturned format finding there.

## Gap loop

A **gap** is anything `gb` gets wrong or can't show while we use it: a crash, wrong output, an unrecognised chunk or plugin, an unnamed parameter. Each gap goes through the loop:

1. File it: `gh issue create --label gap` with the command run, the project, expected vs actual output, and any bytes or offsets involved.
2. If the fix needs ground truth from the user in GarageBand (changing knobs and saving a copy), add the `needs-ground-truth` label, tell the user what session it needs, and stop there.
3. Otherwise start a background Agent with `isolation: "worktree"`, giving it the issue number and this brief: read the issue and `docs/format.md`; fix on branch `fix/<issue>-<slug>`; tests pass; push; `gh pr create` with `Closes #<issue>` in the body; report the PR URL.
4. When the agent reports, review the PR: tests pass, and output checked against real projects. Then merge it (squash) and post the PR link to the user. The user has authorised merging without asking.

## Ready to merge

A PR is **ready** only after `/code-review` has run on it and every finding is either fixed or answered on the PR with the reason it stands, repeating until a review comes back with no findings. Tests must pass. Then squash-merge it without asking; this applies to the gap loop's fix agents too.
