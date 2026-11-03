# gb: GarageBand project inspector

Read-only CLI for `.band` projects. Python 3.9+, standard library only.

- Hooks: `uv tool install pre-commit && pre-commit install` (dev-only: ruff, hygiene, a block on projects and audio outside `tests/fixtures/`). Run ruff through `pre-commit run --all-files`, which pins its version (plain `pre-commit run` checks only staged files).
- Test: `PYTHONPATH=src python3 -m unittest discover -s tests`. By default this runs the committed test projects in `tests/fixtures/` (ground truth in its README), plus a sweep over GarageBand's shipped templates, read in place when GarageBand is installed (skipped on CI; never commit them). Optional local sweep over the user's own projects: prefix the command with `GB_TEST_PROJECTS="$HOME/Documents/Songs/GarageBand:$HOME/Music/GarageBand"`.
- CI (`.github/workflows/ci.yml`) runs the tests on Python 3.9 and latest, and `pre-commit run --all-files`, on every PR and push to main.
- A PR is ready when CI is green and the review loop (`skill-utils:review-loop`) passes.
- Apple's system Python keeps bytecode in `~/Library/Caches/com.apple.python/<project path>/`, not `__pycache__`. An edit that keeps file size and lands in the same second as the last compile runs stale code: after quick revert-style edits, delete that folder.
- Read-only is the product's core promise: every file access goes through `project._read_bytes`, which opens in `rb` mode. The bundle-fingerprint test enforces this for every command in `cli.COMMANDS`.
- Before touching `ProjectData` parsing, read `docs/format.md`. Record every confirmed or overturned format finding there.

## Gap loop

A **gap** is anything `gb` gets wrong or can't show while we use it: a crash, wrong output, an unrecognised chunk or plugin, an unnamed parameter. Each gap goes through the loop:

1. File it: `gh issue create --label gap` with the command run, the project, expected vs actual output, and any bytes or offsets involved.
2. If the fix needs ground truth from the user in GarageBand (changing knobs and saving a copy), add the `needs-ground-truth` label, tell the user what session it needs, and stop there.
3. Otherwise start a background Agent with `isolation: "worktree"`, giving it the issue number and this brief: read the issue and `docs/format.md`; fix on branch `fix/<issue>-<slug>`; check the output against real projects (the optional local sweep and the fixtures); push; `gh pr create` with `Closes #<issue>` in the body; get the PR ready (CI green, review loop passes); report the PR URL.
4. When the agent reports a ready PR, merge it (squash) and post the PR link to the user. The user has authorised merging without asking.
