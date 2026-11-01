"""Track list, decoded from Trak and Envi chunks. See docs/format.md."""

from __future__ import annotations

import struct
from typing import Any

from .chunks import iter_chunks
from .project import Project

TRACK_LIST_ID = 0x04  # the Trak list that holds the visible tracks, in order
MASTER_TRACK_TYPE = 3  # Trak payload byte 0 for the Master Track entry
ENVI_NAME_OFFSET = 158  # u16 length, then UTF-8 name


def _envi_name(payload: bytes) -> str | None:
    if len(payload) < ENVI_NAME_OFFSET + 2:
        return None
    (n,) = struct.unpack_from("<H", payload, ENVI_NAME_OFFSET)
    raw = payload[ENVI_NAME_OFFSET + 2:ENVI_NAME_OFFSET + 2 + n]
    return raw.decode("utf-8", "replace") if n and len(raw) == n else None


def tracks(project: Project) -> dict[str, Any]:
    names: dict[int, str | None] = {}
    entries: list[tuple[int, int, int]] = []  # (index, type, envi object id)
    for c in iter_chunks(project.project_data()):
        if c.tag == "Envi":
            name = _envi_name(c.payload)
            if name is not None or c.id not in names:
                names[c.id] = name
        elif c.tag == "Trak" and c.id == TRACK_LIST_ID and len(c.payload) >= 12:
            (obj,) = struct.unpack_from("<I", c.payload, 8)
            entries.append((c.index, c.payload[0], obj))

    result: list[dict[str, Any]] = []
    gaps: list[str] = []
    for _, kind, obj in sorted(entries):
        if kind == MASTER_TRACK_TYPE:
            continue
        name = names.get(obj)
        if name is None:
            gaps.append(f"track {len(result) + 1}: no name found (Envi object {obj:#x})")
        result.append({"number": len(result) + 1, "name": name, "object_id": obj})
    return {"tracks": result, "gaps": gaps}
