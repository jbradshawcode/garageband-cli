Read-only command-line inspector (`gb`) for GarageBand projects.

**Project**: a `.band` bundle (a folder that macOS shows as one file).
_Avoid_: song file, band file

**Alternative**: one saved variant of a project, stored under `Alternatives/NNN/`. Most projects have only `000`.
_Avoid_: variant, version

**Metadata**: song-level facts in an alternative's `MetaData.plist`: tempo, key, time signature, sample rate, media file lists.

**ProjectData**: the binary file in each alternative holding tracks, channel strips and plugins. Uses Logic Pro's undocumented format.

**Chunk**: one record in ProjectData: a 36-byte header (reversed four-letter tag, payload size) followed by its payload. ProjectData is a flat sequence of chunks.
_Avoid_: block, record, atom

**Plugin slot**: a chunk (tag `AuCU`) holding one entry in a channel strip: a patch name, an instrument, or an effect plugin's saved state.

**Track**: one row in GarageBand's track list, in display order. Excludes the Master Track.

**Environment object**: a chunk (tag `Envi`) for one named mixer object: a track's channel, a bus, an aux return, Master, Click. Tracks get their names from these.
_Avoid_: channel (until the track-to-channel-strip link is decoded)

**Gap**: anything `gb` gets wrong or can't show, found while using it. Reported on stderr as `gb: gap: ...` and filed as a GitHub issue labelled `gap`.

**Ready**: a PR that has passed the ready checklist in CLAUDE.md and may be merged without asking.
_Avoid_: done, mergeable, approved
