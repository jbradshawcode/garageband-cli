"""Split ProjectData into chunks. Layout notes: docs/format.md."""

from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Iterator

from .project import ProjectError

FILE_HEADER_SIZE = 0x18
CHUNK_HEADER_SIZE = 0x24
FILE_MAGIC = b"\x23\x47\xc0\xab"


@dataclass(frozen=True)
class Chunk:
    offset: int
    tag: str  # in reading order, e.g. "Trak" (stored reversed on disk)
    id: int  # header +0x0a: object ID (Envi) or list ID (Trak)
    sub_id: int  # header +0x0e: e.g. channel ID (AuCU)
    index: int  # header +0x12: position within its list / slot index
    payload: bytes


def iter_chunks(data: bytes) -> Iterator[Chunk]:
    if data[:4] != FILE_MAGIC:
        raise ProjectError("ProjectData has an unknown file header")
    offset = FILE_HEADER_SIZE
    while offset + CHUNK_HEADER_SIZE <= len(data):
        tag = data[offset:offset + 4][::-1].decode("latin-1")
        chunk_id, sub_id, index = struct.unpack_from("<III", data, offset + 0x0a)
        (size,) = struct.unpack_from("<Q", data, offset + 0x1c)
        start = offset + CHUNK_HEADER_SIZE
        if not (tag.isascii() and tag.isalnum()) or start + size > len(data):
            raise ProjectError(f"ProjectData chunk at {offset:#x} is malformed")
        yield Chunk(offset, tag, chunk_id, sub_id, index, data[start:start + size])
        offset = start + size
    if offset != len(data):
        raise ProjectError(f"ProjectData has {len(data) - offset} trailing bytes")
