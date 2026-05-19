# Dependencies Analysis - Audacity 3.7.7

## 1. Scope and Methodology

This document reports the dependency analysis performed on Audacity 3.7.7 for the Software Design and Architecture course project.

The analysis focuses on three dependency dimensions:

1. Structural dependencies
2. Data-level dependencies
3. Behavioral and synchronization dependencies

This first version documents the structural dependency evidence extracted during MT2.

## 2. Structural Dependencies

### 2.1 Overview

Structural dependencies in Audacity 3.7.7 appear mainly through compile-time relationships: inheritance chains, header inclusion dependencies, and cross-library include edges.

The structural analysis was based on the compilation database generated in MT1 and on source-level inspection of the `libraries/` and `src/` directories.

### 2.2 Compile Database Baseline

The compilation database contained 1232 translation units.

| Top-level directory | Translation units |
|---|---:|
| `libraries` | 426 |
| `src` | 375 |
| `lib-src` | 316 |
| `modules` | 83 |
| `tests` | 30 |
| `build-sda` | 1 |
| `win` | 1 |

This confirms that Audacity's compile-time structure is not concentrated only in `src/`. A large part of the architectural skeleton is implemented inside internal libraries under `libraries/`.

### 2.3 Track Inheritance Chain

The primary inheritance chain from `Track` to `WaveTrack` is:

```text
Track
  -> AudioTrack
  -> PlayableTrack
  -> SampleTrack
  -> WritableSampleTrack
  -> WaveTrack
```

The measured inheritance depth from `Track` to `WaveTrack` is 5 inheritance edges.

This chain crosses several internal libraries:

```text
lib-track
  -> lib-playable-track
  -> lib-sample-track
  -> lib-wave-track
```

This is a strong structural dependency because each subclass is statically bound to the memory layout and virtual interface of its base classes.

`WaveTrack` also inherits from `Observer::Publisher<WaveTrackMessage>`, while `SampleTrack` also inherits from `PlayableSequence`, and `WritableSampleTrack` also inherits from `RecordableSequence`. These additional inheritance relationships increase the compile-time coupling surface of the concrete `WaveTrack` class.

### 2.4 Header Fan-in / Fan-out Metrics

The header coupling metrics were computed using the script `scripts/coupling_metrics.py`.

| Header | Ca | Ce | I |
|---|---:|---:|---:|
| `libraries/lib-preferences/Prefs.h` | 166 | 10 | 0.057 |
| `libraries/lib-project/Project.h` | 156 | 6 | 0.037 |
| `libraries/lib-shuttlegui/ShuttleGui.h` | 151 | 10 | 0.062 |
| `libraries/lib-wave-track/WaveTrack.h` | 139 | 13 | 0.086 |
| `libraries/lib-track/Track.h` | 52 | 13 | 0.200 |
| `libraries/lib-audio-io/AudioIO.h` | 40 | 14 | 0.259 |

`WaveTrack.h` is the most relevant structural hotspot for this analysis. It has high fan-in, meaning many files depend on it, while also having non-trivial fan-out, meaning it depends on several other headers.

`Track.h` has lower fan-in than `WaveTrack.h` in the direct include metric, but it remains architecturally critical because it is the root of the audio-track inheritance hierarchy. Therefore, a change to `Track` can propagate through the inheritance chain even when the direct include count is not the highest in the system.

### 2.5 Inter-library Structural Dependencies

The inter-library dependency extraction scanned 78 `lib-*` directories and detected 466 unique inter-library dependency edges.

The strongest measured edges were:

| Source library | Target library | Include count |
|---|---|---:|
| `lib-builtin-effects` | `lib-effects` | 53 |
| `lib-builtin-effects` | `lib-wave-track` | 40 |
| `lib-cloud-audiocom` | `lib-network-manager` | 33 |
| `lib-builtin-effects` | `lib-command-parameters` | 25 |
| `lib-cloud-audiocom` | `lib-string-utils` | 22 |
| `lib-wave-track` | `lib-math` | 13 |

The generated graph is available at:

```text
analysis/dependencies/mt2-structural/inter-library-graph.svg
```

The inter-library graph confirms that Audacity's architectural structure is not only a set of isolated `lib-*` modules. Several libraries depend on each other through header inclusion, which creates compile-time coupling across module boundaries.

### 2.6 Structural Risk Summary

| Finding | Evidence | Risk |
|---|---|---|
| Deep `Track -> WaveTrack` inheritance chain | 5 inheritance edges | High compile-time coupling |
| `WaveTrack.h` high fan-in | Ca = 139 | Many recompilation dependents |
| `WaveTrack.h` non-trivial fan-out | Ce = 13 | Sensitive to external header changes |
| Cross-library include edges | 466 unique inter-library edges | Boundary coupling across `lib-*` modules |
| `lib-builtin-effects -> lib-wave-track` | include_count = 40 | Effects strongly depend on wave-track abstractions |

Overall, the structural dependency analysis shows that Audacity's audio model is centered around a deep inheritance hierarchy and widely included headers. `WaveTrack.h` is the main hotspot because it combines inheritance coupling, high fan-in, and cross-library usage.

### 2.7 Evidence Artifacts

The structural dependency evidence is stored in the following files:

| Artifact | Purpose |
|---|---|
| `analysis/dependencies/mt2-structural/compile-db-structure.md` | Compile database baseline |
| `analysis/dependencies/mt2-structural/inheritance-raw.txt` | Raw inheritance extraction |
| `analysis/dependencies/mt2-structural/track-inheritance-summary.md` | Verified Track-to-WaveTrack chain |
| `analysis/dependencies/mt2-structural/coupling-metrics.txt` | Header Ca/Ce/I coupling metrics |
| `analysis/dependencies/mt2-structural/inter-library-deps.txt` | Inter-library dependency edges |
| `analysis/dependencies/mt2-structural/inter-library-deps.dot` | Graphviz DOT graph |
| `analysis/dependencies/mt2-structural/inter-library-graph.svg` | Rendered inter-library graph |
