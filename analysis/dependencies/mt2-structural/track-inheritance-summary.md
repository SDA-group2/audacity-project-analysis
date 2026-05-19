# MT2 — Track Inheritance Summary

## Purpose

This document summarizes the structural inheritance chain from `Track` to `WaveTrack` in Audacity 3.7.7.

The goal is to provide reproducible evidence for compile-time structural coupling caused by inheritance.

## Evidence Source

The inheritance evidence was extracted from Audacity 3.7.7 headers using:

- `scripts/extract_inheritance.py`
- direct PowerShell inspection of:
  - `libraries/lib-track/Track.h`
  - `libraries/lib-playable-track/PlayableTrack.h`
  - `libraries/lib-sample-track/SampleTrack.h`
  - `libraries/lib-wave-track/WaveTrack.h`

## Verified Primary Inheritance Chain

```text
Track
  └── AudioTrack
        └── PlayableTrack
              └── SampleTrack
                    └── WritableSampleTrack
                          └── WaveTrack
```

## Source Evidence

| Class | Direct base class | Source file | Evidence |
|---|---|---|---|
| `Track` | root abstract base | `libraries/lib-track/Track.h` | `class TRACK_API Track /* not final */` |
| `AudioTrack` | `Track` | `libraries/lib-playable-track/PlayableTrack.h` | `class PLAYABLE_TRACK_API AudioTrack /* not final */ : public Track` |
| `PlayableTrack` | `AudioTrack` | `libraries/lib-playable-track/PlayableTrack.h` | `class PLAYABLE_TRACK_API PlayableTrack /* not final */ : public AudioTrack` |
| `SampleTrack` | `PlayableTrack` | `libraries/lib-sample-track/SampleTrack.h` | `class SAMPLE_TRACK_API SampleTrack /* not final */ : public PlayableTrack` |
| `WritableSampleTrack` | `SampleTrack` | `libraries/lib-sample-track/SampleTrack.h` | `class SAMPLE_TRACK_API WritableSampleTrack /* not final */ : public SampleTrack` |
| `WaveTrack` | `WritableSampleTrack` | `libraries/lib-wave-track/WaveTrack.h` | `class WAVE_TRACK_API WaveTrack final : public WritableSampleTrack` |

## Additional Structural Dependencies

`WaveTrack` also inherits from:

```text
Observer::Publisher<WaveTrackMessage>
```

This means that `WaveTrack` is structurally coupled not only to the audio-track inheritance hierarchy, but also to the observer/event publication mechanism.

`SampleTrack` also inherits from `PlayableSequence`, and `WritableSampleTrack` also inherits from `RecordableSequence`. These side interfaces increase the compile-time coupling surface of the final concrete `WaveTrack` class.

## Measured Depth

The number of inheritance edges from `Track` to `WaveTrack` is:

```text
5
```

The path is:

```text
Track -> AudioTrack -> PlayableTrack -> SampleTrack -> WritableSampleTrack -> WaveTrack
```

## Raw Extraction Summary

The script-based extraction produced:

```text
Total public inheritance declarations found: 643
Track-related inheritance declarations found: 55
Pure virtual Track interface entries found: 10
```

## Architectural Interpretation

This inheritance chain is a strong structural dependency because each subclass is bound to the memory layout and virtual interface of its base classes at compile time.

A change in `Track` can propagate through `AudioTrack`, `PlayableTrack`, `SampleTrack`, `WritableSampleTrack`, and finally `WaveTrack`. This means the chain acts as a compile-time dependency path across multiple Audacity internal libraries:

```text
lib-track
  -> lib-playable-track
  -> lib-sample-track
  -> lib-wave-track
```

This is important for the dependency analysis because `WaveTrack` is one of the most central concrete audio data structures in Audacity. Its design combines deep inheritance with additional observer and sequence interfaces, making it a structural coupling hotspot.