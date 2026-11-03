"""Tests against the committed test projects in tests/fixtures/.

Expected values come from GarageBand itself; see tests/fixtures/README.md.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import unittest
from pathlib import Path

from gbcli.cli import COMMANDS, main
from gbcli.project import Project, info
from gbcli.tracks import tracks

FIXTURES = Path(__file__).parent / "fixtures"
EQ_PAIR = [FIXTURES / "fixture-eq-before.band", FIXTURES / "fixture-eq-after.band"]


def bundle_fingerprint(bundle: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(bundle.rglob("*")):
        st = f.lstat()
        h.update(f"{f.relative_to(bundle)}|{st.st_size}|{st.st_mtime_ns}".encode())
        if f.is_file():
            h.update(f.read_bytes())
    return h.hexdigest()


class Fixtures(unittest.TestCase):
    def test_info_matches_garageband(self):
        for path in EQ_PAIR:
            with self.subTest(project=path.name):
                d = info(Project.open(path))
                expected = {
                    "name": path.stem,
                    "saved_with": "GarageBand 10.4.12 (6182)",
                    "tempo_bpm": 97,
                    "time_signature": "3/4",
                    "key": "D minor",
                    "sample_rate": 44100,
                    "track_count": 2,
                }
                self.assertEqual({k: d[k] for k in expected}, expected)

    def test_tracks_match_garageband(self):
        for path in EQ_PAIR:
            with self.subTest(project=path.name):
                d = tracks(Project.open(path))
                self.assertEqual([t["name"] for t in d["tracks"]], ["Synth", "Bass"])
                self.assertEqual(d["gaps"], [])

    def test_every_command_leaves_bundle_untouched(self):
        bundle = EQ_PAIR[0]
        before = bundle_fingerprint(bundle)
        for command in COMMANDS:
            for extra in ([], ["--json"]):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(main([command, str(bundle), *extra]), 0)
        self.assertEqual(bundle_fingerprint(bundle), before)


if __name__ == "__main__":
    unittest.main()
