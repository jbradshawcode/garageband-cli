# GarageBand project format notes

Reverse-engineered; nothing here is documented by Apple. Each claim notes how it was verified. Update this file whenever a finding is confirmed or overturned.

## Bundle layout

```
X.band/
  Resources/ProjectInformation.plist   LastSavedFrom, VariantNames {"0": name}
  Alternatives/000/MetaData.plist      tempo, key, signature, sample rate, media lists
  Alternatives/000/ProjectData         binary: tracks, channel strips, plugins
  Media/Audio Files/, Media/Impulse Responses/, ...
```

MetaData keys vary by GarageBand version (`AlchemyFiles`, `VideoFiles`, `QuicksamplerFiles` are sometimes absent): read every key with a default. `NumberOfTracks` does not match the count of `Trak` chunks (3 vs 17 in one project); treat it as unreliable.
_Verified: all 32 local projects, GarageBand 10.1.2 to 10.4.12._

## ProjectData container

- 24-byte file header: magic `23 47 c0 ab`, ..., u64 LE payload size at offset 16.
- From offset 0x18: a flat sequence of chunks until end of file.
- Chunk header, 36 bytes (offsets relative to chunk start):
  - `+0x00` 4-byte tag, stored reversed (`karT` on disk = `Trak`).
  - `+0x1c` u64 LE payload size.
  - Payload follows at `+0x24`.

_Verified: a sequential walk ends exactly at EOF on 3 projects (10.1.2, 10.3.4, 10.4.12)._

Tags seen (reversed to read order): `Song`, `MSeq`, `EvSq`, `TxSt`, `Styl`, `Trak`, `AuCO`, `AuCU`, `AuCn`, `Envi`, `Hypr`, `AuFl`, `AuRg`, `SngO`, `CorM`, `InSt`, `Layr`, `ScSt`, `Vide`, `UndM`, `TxSq`, `GenM`.

## Plugin slots (`AuCU`)

- Header `+0x0a` u32: channel ID. Header `+0x0e` u32: slot index within the channel.
- A slot payload holds a patch name, an instrument, an effect's state, or an NSKeyedArchiver bplist (Smart Controls mappings).
- Slot index does not identify the slot's type: the same plugin appears at different indices on different channels.

_Verified by inspection on one project; not yet decoded in code._

## Built-in plugin state

All built-in plugins seen share one envelope inside the payload:

```
... plugin name (ASCII, NUL-padded) ...
"GAME" u32 plugin_id ...                 at payload offset 132 in all samples
"GAMETSPP" u32 plugin_id ... float32[]   parameter values
```

Plugin IDs seen: Channel EQ `0xEC`, Compressor `0x9A`, Noise Gate `0xB3`, Echo `0x93`, Chorus `0x91`, Pedalboard `0x111`, Space Designer `0xE7`.

Parameter names are not stored in the project. Candidate names exist in `GarageBand.app/Contents/Frameworks/MADSP.framework/Versions/A/MADSP` (`strings`), but mixed with internal variants, so string order does not give the parameter index. Confirming a name means a diff session: the user changes known knobs in GarageBand, saves a copy, and we match the changed floats.

_Verified by inspection on one project; values not yet confirmed against the UI._
