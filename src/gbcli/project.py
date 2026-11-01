"""Locate and read the files inside a GarageBand project bundle.

Every read in this package goes through `_read_bytes`, which opens files
read-only. Nothing here ever writes inside a bundle.
"""

from __future__ import annotations

import plistlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ProjectError(Exception):
    """The path is not a readable GarageBand project."""


def _read_bytes(path: Path) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read()
    except FileNotFoundError:
        raise ProjectError(f"missing {path.name} in project") from None
    except OSError as e:
        raise ProjectError(f"cannot read {path.name}: {e.strerror}") from None


def _read_plist(path: Path) -> dict[str, Any]:
    data = _read_bytes(path)
    try:
        return plistlib.loads(data)
    except Exception as e:  # plistlib raises several unrelated types on bad input
        raise ProjectError(f"unreadable {path.name}: {e}") from None


@dataclass(frozen=True)
class Project:
    path: Path
    alternative: int = 0

    @classmethod
    def open(cls, path: str | Path, alternative: int = 0) -> "Project":
        p = Path(path).expanduser().resolve()
        if not (p / "Alternatives").is_dir():
            raise ProjectError(f"not a GarageBand project: {p}")
        project = cls(p, alternative)
        if not project.alternative_dir.is_dir():
            available = ", ".join(str(a) for a in project.alternatives()) or "none"
            raise ProjectError(
                f"no alternative {alternative} (available: {available})"
            )
        return project

    @property
    def alternative_dir(self) -> Path:
        return self.path / "Alternatives" / f"{self.alternative:03d}"

    def alternatives(self) -> list[int]:
        return sorted(
            int(d.name)
            for d in (self.path / "Alternatives").iterdir()
            if d.is_dir() and d.name.isdigit()
        )

    def project_information(self) -> dict[str, Any]:
        return _read_plist(self.path / "Resources" / "ProjectInformation.plist")

    def metadata(self) -> dict[str, Any]:
        return _read_plist(self.alternative_dir / "MetaData.plist")

    def project_data(self) -> bytes:
        return _read_bytes(self.alternative_dir / "ProjectData")


def info(project: Project) -> dict[str, Any]:
    """Song-level facts from the project's plists."""
    pinfo = project.project_information()
    meta = project.metadata()
    variants = pinfo.get("VariantNames", {})
    key = " ".join(
        v for v in (meta.get("SongKey"), meta.get("SongGenderKey")) if v
    )
    num, den = meta.get("SongSignatureNumerator"), meta.get("SongSignatureDenominator")
    return {
        "name": variants.get(str(project.alternative), project.path.stem),
        "path": str(project.path),
        "saved_with": pinfo.get("LastSavedFrom"),
        "alternative": project.alternative,
        "alternatives": {
            a: variants.get(str(a)) for a in project.alternatives()
        },
        "tempo_bpm": meta.get("BeatsPerMinute"),
        "time_signature": f"{num}/{den}" if num and den else None,
        "key": key or None,
        "sample_rate": meta.get("SampleRate"),
        "track_count": meta.get("NumberOfTracks"),
        "media": {
            "audio_files": meta.get("AudioFiles", []),
            "unused_audio_files": meta.get("UnusedAudioFiles", []),
            "sampler_instruments": meta.get("SamplerInstrumentsFiles", []),
            "impulse_responses": meta.get("ImpulsResponsesFiles", []),
            "alchemy_files": meta.get("AlchemyFiles", []),
            "quicksampler_files": meta.get("QuicksamplerFiles", []),
            "ultrabeat_files": meta.get("UltrabeatFiles", []),
            "video_files": meta.get("VideoFiles", []),
        },
    }
