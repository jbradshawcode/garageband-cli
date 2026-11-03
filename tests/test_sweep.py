"""Sweep: invariants over every project found on this Mac.

Covers project shapes the committed fixtures lack (audio and drummer tracks,
older GarageBand versions). Reads, never copies:

- GarageBand's shipped templates, when GarageBand is installed. Skipped on CI.
- Your own projects, only when GB_TEST_PROJECTS is set to a colon-separated
  list of directories, e.g.
  GB_TEST_PROJECTS="$HOME/Documents/Songs/GarageBand:$HOME/Music/GarageBand"
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path

from gbcli.project import Project, info
from gbcli.tracks import tracks

TEMPLATES = Path(
    "/Applications/GarageBand.app/Contents/Resources/Project Templates/NewProject"
)


def sweep_projects() -> list[Path]:
    dirs = [TEMPLATES] + [
        Path(d).expanduser()
        for d in os.environ.get("GB_TEST_PROJECTS", "").split(":")
        if d
    ]
    return sorted(p for d in dirs for p in d.glob("*.band") if p.is_dir())


PROJECTS = sweep_projects()


@unittest.skipUnless(PROJECTS, "no GarageBand install or GB_TEST_PROJECTS")
class Sweep(unittest.TestCase):
    def test_every_project_reads_cleanly(self):
        for path in PROJECTS:
            with self.subTest(project=str(path)):
                project = Project.open(path)
                d = info(project)
                self.assertIsInstance(d["tempo_bpm"], (int, float))
                self.assertRegex(d["time_signature"], r"^\d+/\d+$")
                self.assertTrue(d["key"])
                self.assertTrue(d["saved_with"].startswith("GarageBand"))
                t = tracks(project)
                self.assertEqual(len(t["tracks"]), project.metadata()["NumberOfTracks"])
                self.assertEqual(t["gaps"], [])


if __name__ == "__main__":
    unittest.main()
