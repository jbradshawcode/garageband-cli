"""Tests run against real GarageBand projects on this machine.

Set GB_TEST_PROJECTS to a colon-separated list of directories to search;
defaults to the usual GarageBand locations. Tests skip if none are found.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import os
import unittest
from pathlib import Path

from gbcli.cli import COMMANDS, main
from gbcli.project import Project, info
from gbcli.tracks import tracks

DEFAULT_DIRS = "~/Documents/Songs/GarageBand:~/Music/GarageBand"


def real_projects() -> list[Path]:
    dirs = os.environ.get("GB_TEST_PROJECTS", DEFAULT_DIRS).split(":")
    return sorted(
        p for d in dirs for p in Path(d).expanduser().glob("*.band") if p.is_dir()
    )


def bundle_fingerprint(bundle: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(bundle.rglob("*")):
        st = f.lstat()
        h.update(f"{f.relative_to(bundle)}|{st.st_size}|{st.st_mtime_ns}".encode())
        if f.is_file():
            h.update(f.read_bytes())
    return h.hexdigest()


PROJECTS = real_projects()


@unittest.skipUnless(PROJECTS, "no GarageBand projects found")
class RealProjects(unittest.TestCase):
    def test_info_reads_song_facts_from_every_project(self):
        for path in PROJECTS:
            with self.subTest(project=path.name):
                d = info(Project.open(path))
                self.assertIsInstance(d["tempo_bpm"], (int, float))
                self.assertRegex(d["time_signature"], r"^\d+/\d+$")
                self.assertTrue(d["key"])
                self.assertTrue(d["saved_with"].startswith("GarageBand"))

    def test_tracks_match_metadata_count_and_all_have_names(self):
        for path in PROJECTS:
            with self.subTest(project=path.name):
                project = Project.open(path)
                d = tracks(project)
                self.assertEqual(len(d["tracks"]), project.metadata()["NumberOfTracks"])
                self.assertEqual(d["gaps"], [])

    def test_every_command_leaves_bundle_untouched(self):
        bundle = min(
            PROJECTS,
            key=lambda p: sum(f.stat().st_size for f in p.rglob("*") if f.is_file()),
        )
        before = bundle_fingerprint(bundle)
        for command in COMMANDS:
            for extra in ([], ["--json"]):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([command, str(bundle), *extra]), 0)
        self.assertEqual(bundle_fingerprint(bundle), before)


if __name__ == "__main__":
    unittest.main()
