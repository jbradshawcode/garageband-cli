"""`gb` command-line entry point."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Callable

from .project import Project, ProjectError, info
from .tracks import tracks


def _num(v: Any) -> str:
    return f"{v:g}" if isinstance(v, (int, float)) else str(v)


def _print_info(d: dict[str, Any]) -> None:
    rows = [
        ("Name", d["name"]),
        ("Path", d["path"]),
        ("Saved with", d["saved_with"]),
        ("Tempo", f"{_num(d['tempo_bpm'])} BPM" if d["tempo_bpm"] is not None else None),
        ("Time signature", d["time_signature"]),
        ("Key", d["key"]),
        ("Sample rate", f"{d['sample_rate']} Hz" if d["sample_rate"] else None),
        ("Tracks", d["track_count"]),
    ]
    if len(d["alternatives"]) > 1:
        alts = ", ".join(f"{a}: {n or '?'}" for a, n in d["alternatives"].items())
        rows.append(("Alternatives", f"{alts} (showing {d['alternative']})"))
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        print(f"{label:<{width}}  {value if value is not None else '-'}")

    for label, files in d["media"].items():
        if files:
            print(f"\n{label.replace('_', ' ').capitalize()} ({len(files)}):")
            for f in files:
                print(f"  {f}")


def _print_tracks(d: dict[str, Any]) -> None:
    if not d["tracks"]:
        print("No tracks.")
    for t in d["tracks"]:
        print(f"{t['number']:>3}  {t['name'] or '?'}")


COMMANDS: dict[str, tuple[str, Callable[[Project], Any], Callable[[Any], None]]] = {
    "info": ("Song metadata: tempo, key, signature, media files", info, _print_info),
    "tracks": ("Tracks in display order", tracks, _print_tracks),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gb", description="Read-only inspector for GarageBand projects."
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name, (help_text, _, _) in COMMANDS.items():
        p = sub.add_parser(name, help=help_text, description=help_text)
        p.add_argument("project", help="path to a .band project")
        p.add_argument("--alt", type=int, default=0, metavar="N",
                       help="project alternative to read (default 0)")
        p.add_argument("--json", action="store_true", help="output JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _, compute, render = COMMANDS[args.command]
    try:
        result = compute(Project.open(args.project, args.alt))
    except (ProjectError, OSError) as e:
        print(f"gb: {e}", file=sys.stderr)
        return 1
    try:
        for gap in result.get("gaps", []):
            print(f"gb: gap: {gap}", file=sys.stderr)
        if args.json:
            json.dump(result, sys.stdout, indent=2, default=str)
            print()
        else:
            render(result)
        sys.stdout.flush()
    except BrokenPipeError:  # e.g. piped into `head`; exit quietly
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0


if __name__ == "__main__":
    sys.exit(main())
