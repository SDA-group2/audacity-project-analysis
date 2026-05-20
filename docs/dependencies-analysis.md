# Dependencies Analysis - Audacity (Master Branch)

## 1. Scope and Methodology

This document reports the dependency analysis performed on the active `master` branch of Audacity for the Software Design and Architecture course project.

The analysis focuses on three dependency dimensions:

1. Structural dependencies
2. Data-level dependencies
3. Behavioral and synchronization dependencies

This version documents the structural dependency evidence extracted from the active codebase.

### 1.1 Active Codebase Requirement

During the project, the analysis was migrated from the static `Audacity-3.7.7` release tag to the active `master` branch to satisfy the course requirement of analyzing an actively updated software system.

This pivot was coordinated with the architecture team after identifying that a frozen release snapshot would not fully satisfy the active-codebase criterion.

After switching to `master`, the static-analysis workflow was regenerated, including the compilation database, Cppcheck results, inheritance extraction, header coupling metrics, and inter-library dependency graph.

### 1.2 Toolchain

The analysis used:

| Tool | Purpose |
|---|---|
| CMake + Ninja | Generate compilation database |
| MSVC Build Tools | C/C++ build environment |
| Python scripts | Extract dependency evidence |
| Cppcheck | Static-analysis evidence |
| Doxygen | Structural exploration support |
| Graphviz | Dependency graph visualization |

## 2. Structural Dependencies

### 2.1 Overview

Structural dependencies in the active Audacity `master` branch mainly appear through compile-time relationships: inheritance chains, header inclusion dependencies, and cross-library include edges.

The analysis was based on the compilation database and source-level inspection of the `libraries/` and `src/` directories.

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

Because this analysis targets `master`, these numbers should be interpreted as a snapshot of an evolving codebase.

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

`WaveTrack` also inherits from `Observer::Publisher<WaveTrackMessage>`, while `SampleTrack` also inherits from `PlayableSequence`, and `WritableSampleTrack` also inherits from `RecordableSequence`.

### 2.4 Header Fan-in / Fan-out Metrics

| Header | Ca | Ce | I |
|---|---:|---:|---:|
| `libraries/lib-preferences/Prefs.h` | 166 | 10 | 0.057 |
| `libraries/lib-project/Project.h` | 156 | 6 | 0.037 |
| `libraries/lib-shuttlegui/ShuttleGui.h` | 151 | 10 | 0.062 |
| `libraries/lib-wave-track/WaveTrack.h` | 139 | 13 | 0.086 |
| `libraries/lib-track/Track.h` | 52 | 13 | 0.200 |
| `libraries/lib-audio-io/AudioIO.h` | 40 | 14 | 0.259 |

`WaveTrack.h` emerged as a major structural hotspot because it combines high fan-in with non-trivial fan-out.

### 2.5 Inter-library Structural Dependencies

The inter-library dependency extraction scanned 78 `lib-*` directories and detected 466 unique inter-library dependency edges.

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

### 2.6 Structural Risk Summary

| Finding | Evidence | Risk |
|---|---|---|
| Deep `Track -> WaveTrack` inheritance chain | 5 inheritance edges | High compile-time coupling |
| `WaveTrack.h` high fan-in | Ca = 139 | Many recompilation dependents |
| `WaveTrack.h` non-trivial fan-out | Ce = 13 | Sensitive to external header changes |
| Cross-library include edges | 466 unique inter-library edges | Boundary coupling across `lib-*` modules |
| `lib-builtin-effects -> lib-wave-track` | include_count = 40 | Effects strongly depend on wave-track abstractions |

Overall, the structural dependency analysis shows that the active Audacity `master` branch contains a deep audio-track inheritance hierarchy and strong inter-library compile-time coupling.

### 2.7 Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `analysis/dependencies/mt2-structural/compile-db-structure.md` | Compile database baseline |
| `analysis/dependencies/mt2-structural/inheritance-raw.txt` | Raw inheritance extraction |
| `analysis/dependencies/mt2-structural/track-inheritance-summary.md` | Verified Track-to-WaveTrack chain |
| `analysis/dependencies/mt2-structural/coupling-metrics.txt` | Header Ca/Ce/I coupling metrics |
| `analysis/dependencies/mt2-structural/inter-library-deps.txt` | Inter-library dependency edges |
| `analysis/dependencies/mt2-structural/inter-library-deps.dot` | Graphviz DOT graph |
| `analysis/dependencies/mt2-structural/inter-library-graph.svg` | Rendered inter-library graph |



## MT4 — Behavioral and Synchronization Dependencies

Behavioral and synchronization dependencies were analyzed to identify execution-order assumptions, callback-based control flow, blocking operations, and synchronization relations in Audacity. This dimension complements the structural and data-level analyses: structural dependencies describe compile-time relations, data-level dependencies describe coupling through shared project state, while behavioral dependencies describe how components depend on each other during execution.

The analysis was performed on the `au3/src` subtree of the Audacity source code. The first attempt on the full repository was interrupted because it included large external and generated subtrees. The final scan was restricted to the main Audacity source directory in order to focus on the application code relevant to the design analysis.

A lightweight Python static analyzer was implemented to search for behavioral and synchronization indicators in C/C++ files. The analyzer grouped matches into six categories: callback/event dispatch, state transitions, audio stream control, blocking or waiting operations, synchronization primitives, and threading constructs.

### MT4 results

| Category | Matches |
|---|---:|
| callbacks_events | 1012 |
| state_transitions | 410 |
| audio_stream_control | 172 |
| blocking_or_waiting | 35 |
| synchronization | 12 |
| threading | 5 |

The results show that Audacity’s behavioral dependency structure is dominated by callback/event-based execution. This is consistent with the nature of the system: Audacity is an interactive desktop audio editor where user actions, GUI events, playback/recording requests, and background operations trigger execution indirectly through framework events and callbacks.

The second largest category is state-transition dependency. This indicates that many Audacity operations depend on a correct ordering of lifecycle actions such as starting, stopping, pausing, committing, flushing, or closing resources. Such dependencies are architecturally relevant because an incorrect execution order may lead to inconsistent project state, invalid audio-stream state, or incorrect user-visible behavior.

The `audio_stream_control` category is also significant. It captures behavioral coupling around the audio engine and stream lifecycle. In Audacity, playback, recording, and monitoring are not isolated operations. They require a sequence of interactions between the GUI command layer, project-level audio management, the AudioIO subsystem, and the underlying audio stream implementation.

A simplified execution path is:

```text
User action
   -> GUI command / toolbar handler
   -> project-level command or audio manager
   -> AudioIO
   -> stream setup
   -> stream start / stop
   -> audio callback execution