# Test projects

Purpose-made GarageBand projects, committed so tests run anywhere (including CI). Nothing personal. Keep them byte-exact: never open and re-save them in GarageBand; make a new pair instead.

Each bundle had `Media/` stripped, and the root-level `projectData` file removed: it is byte-identical to the one in every GarageBand project template (Apple's file), and `gb` never reads it.

## `fixture-eq-before.band` / `fixture-eq-after.band`

A before/after pair for decoding Channel EQ (#3). Ground truth is from GarageBand screenshots taken when the projects were saved.

Both projects:

| | |
|---|---|
| Saved with | GarageBand 10.4.12 (6182) |
| Tempo | 97 BPM |
| Time signature | 3/4 |
| Key | D minor |
| Sample rate | 44100 Hz |
| Tracks | 1. Synth, 2. Bass (both software instruments) |

`before`: Channel EQ untouched on both tracks.

`after`: identical except Synth's Channel EQ:

| Band | On | Frequency | Gain | Slope / Q |
|---|---|---|---|---|
| Low Cut | on | 47.0 Hz | | 12 dB/Oct, Q 0.71 |
| Peak 2 | | 830 Hz | +7.3 dB | Q 1.70 |
| High Shelf | | 6200 Hz | −4.2 dB | Q 1.00 |
| High Cut | on | 20000 Hz | | 24 dB/Oct, Q 0.71 |
| Output gain | | | about +1.5 dB (not confirmed exactly) | |

Bands not listed were not recorded; assume nothing about them.
