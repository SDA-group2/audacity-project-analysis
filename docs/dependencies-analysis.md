# Dependencies Analysis - Audacity (Master Branch)

## 1. Scope and Methodology

This document reports the dependency analysis performed on the active `master` branch of Audacity for the Software Design and Architecture course project.

The analysis focuses on three dependency dimensions required for the Dependencies section:

1. Structural dependencies
2. Data-level dependencies
3. Behavioral and synchronization dependencies

This version documents the dependency evidence extracted from the active codebase, covering structural, data-level, and behavioral/synchronization dependencies.

### 1.1 Active Codebase Requirement

During the project, the analysis was migrated from the static `Audacity-3.7.7` release tag to the active `master` branch to satisfy the course requirement of analyzing an actively updated software system.

This pivot was coordinated with the architecture team after identifying that a frozen release snapshot would not fully satisfy the active-codebase criterion.

After switching to `master`, the static-analysis workflow was regenerated, including the compilation database, Cppcheck results, inheritance extraction, header coupling metrics, inter-library dependency graph, data-level coupling evidence, and behavioral/synchronization dependency evidence.

### 1.2 Dependency Taxonomy

The dependency analysis follows the dependency dimensions introduced in the course material.

Structural dependencies are code-level dependencies where a module must know another module at compile time. They include inheritance, direct use of concrete classes, header inclusion, and construction dependencies.

Data-level dependencies occur when one component depends on another component's internal data model or when multiple components depend on the same schema, shared representation, persistent storage model, or global configuration state.

Behavioral dependencies occur when one component influences, schedules, or dictates another component's execution path. This includes control-flow dependency, callback dependency, transactional dependency, lifecycle-order dependency, and timing-assumption dependency.

Synchronization dependencies occur when one component must wait for another component or coordinate with it through locks, atomics, waits, event queues, or thread-related mechanisms. In this report, synchronization dependencies are discussed together with behavioral dependencies because Audacity's runtime behavior combines callback-driven execution, ordering assumptions, deferred execution, and shared-state coordination.

### 1.3 Toolchain

The analysis used:

| Tool | Purpose |
|---|---|
| CMake + Ninja | Generate compilation database |
| MSVC Build Tools | C/C++ build environment |
| Python scripts | Extract dependency evidence |
| Cppcheck | Static-analysis evidence |
| Doxygen | Structural exploration support |
| Graphviz | Dependency graph visualization |
| CMD `findstr` searches | Targeted source-code evidence extraction |

### 1.4 Methodological Notes

The analysis was based on source-code inspection, generated artifacts, and lightweight static-analysis scripts. The main goal was not to prove every dependency exhaustively, but to identify architecturally relevant coupling points and classify them according to the course taxonomy.

The analysis is therefore interpreted as a design-level dependency assessment: quantitative results are used as supporting evidence, while the final architectural interpretation is based on the role of the affected components in Audacity's source structure.

---

## 2. Structural Dependencies

### 2.1 Overview

Structural dependencies in the active Audacity `master` branch mainly appear through compile-time relationships: inheritance chains, header inclusion dependencies, and cross-library include edges.

The analysis was based on the compilation database and source-level inspection of the main Audacity source areas, including `au3/libraries/`, `au3/src/`, `au3/modules/`, `au3/lib-src/`, and the top-level `src/` directory where applicable.

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

High fan-in indicates that many files depend on the header. Therefore, a change to this header may trigger wide recompilation and may affect many dependent components. Non-trivial fan-out indicates that the header itself also depends on several other headers, increasing the probability of transitive compile-time coupling.

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

The most relevant structural dependency is the dependency from `lib-builtin-effects` to `lib-wave-track`. This suggests that built-in effects are strongly coupled to the wave-track abstraction, which is expected in an audio editor but still architecturally significant because effects depend on the internal representation of editable audio tracks.

### 2.6 Structural Risk Summary

| Finding | Evidence | Risk |
|---|---|---|
| Deep `Track -> WaveTrack` inheritance chain | 5 inheritance edges | High compile-time coupling |
| `WaveTrack.h` high fan-in | Ca = 139 | Many recompilation dependents |
| `WaveTrack.h` non-trivial fan-out | Ce = 13 | Sensitive to external header changes |
| Cross-library include edges | 466 unique inter-library edges | Boundary coupling across `lib-*` modules |
| `lib-builtin-effects -> lib-wave-track` | include_count = 40 | Effects strongly depend on wave-track abstractions |

Overall, the structural dependency analysis shows that the active Audacity `master` branch contains a deep audio-track inheritance hierarchy and strong inter-library compile-time coupling. This coupling is partly intentional because audio editing requires shared abstractions for tracks, samples, and effects, but it also increases the cost of changing core audio-track classes.

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

---

## 3. Data-Level Dependencies

### 3.1 Overview

Data-level dependencies were analyzed to identify coupling through shared project state, shared data structures, persistent storage, and global configuration.

In Audacity, the main data-level dependencies are concentrated around the project state, the track model, shared audio data representation, preferences, and persistence mechanisms.

Unlike structural dependencies, data-level dependencies are not only about which header includes another header. They concern the shared data representations that multiple subsystems must understand consistently.

### 3.2 Shared Project State

Audacity uses a shared project context as a coordination point between several subsystems. Editing, playback, effect processing, history management, and UI updates all depend on project-level state.

This is a data-level dependency because components do not always communicate only through explicit function calls. Instead, they may access or update shared project-level objects.

Architecturally, this means that the project context behaves as a central state coordination point. This is useful because it provides a common representation of the current project, but it also increases hidden coupling: a change to project state representation can propagate to editing commands, UI refresh logic, playback preparation, and persistence.

### 3.3 Shared Track Model

The track model is another major data-level dependency. Components such as the GUI, editing commands, effects, playback preparation, and serialization logic depend on shared track structures.

The most important shared structures are:

```text
Track
TrackList
WaveTrack
AudioTrack
SampleTrack
WritableSampleTrack
```

This creates coupling because a change to the track model may affect editing behavior, rendering, playback, effects, and project persistence.

The track model is therefore both structurally and data-level significant. It is structural because track classes are connected by inheritance and header dependencies; it is data-level because the same track representation is shared across many runtime features.

### 3.4 Shared Audio Data and Persistence Representation

Audacity also contains data-level dependencies around persistence. Project data and audio data must be stored, loaded, and kept consistent across editing operations.

The persistence representation acts as a boundary between in-memory project objects and stored project files. This dependency is significant because persistence changes may affect project loading, saving, recovery, audio block access, and compatibility with existing project files.

In an audio editor, shared persistence is especially important because large audio data cannot be treated as a simple local variable. Multiple subsystems must agree on how audio data is represented, accessed, transformed, and saved.

### 3.5 Shared Preferences and Configuration

Shared preferences are another source of data-level coupling. Preferences and project settings influence GUI behavior, audio device configuration, quality settings, playback/recording parameters, and effect defaults.

This is a data-level dependency because components depend on common configuration state rather than only on explicit parameters passed through local interfaces.

Configuration state is architecturally relevant because it can change runtime behavior without changing source-code dependencies. For example, a component may appear independent in an include graph but still be coupled to another subsystem through shared preferences or project settings.

### 3.6 Data-Level Dependency Summary

| Finding | Shared artifact | Dependency type | Architectural risk |
|---|---|---|---|
| Project-level state coupling | Project context / project services | Shared state | Hidden coupling between subsystems |
| Track model coupling | `TrackList`, `WaveTrack`, track hierarchy | Shared data structure | Changes affect editing, playback, effects, and persistence |
| Persistence coupling | Project file / SQLite-backed representation | Shared schema / data store | Changes may affect compatibility and recovery |
| Preferences coupling | Global/project preferences | Shared configuration | Runtime behavior depends on common mutable settings |

Overall, Audacity's data-level dependencies are centered on shared project state, shared track structures, persistence representation, and configuration state. These dependencies are expected in an audio editor, but they increase maintenance complexity because multiple subsystems depend on the same conceptual data model.


---

## 4. Behavioral and Synchronization Dependencies

### 4.1 Overview

Behavioral and synchronization dependencies were analyzed to identify runtime coupling in Audacity. This dimension focuses on execution order, callback propagation, deferred execution, thread coordination, and timing assumptions. Unlike structural dependencies, these dependencies are not always visible from include graphs or inheritance hierarchies.

The analysis focused on five runtime coupling surfaces:

1. The real-time audio engine
2. Synchronization primitives
3. Observer-based notification
4. Deferred UI execution
5. Initialization-order dependencies

### 4.2 Method

The analysis was performed using targeted source-code searches over the active `master` branch. Evidence was collected for audio stream lifecycle calls, synchronization primitives, observer publication/subscription, UI event queuing, and initialization/registry setup.

The generated evidence files are stored in:

```text
analysis/dependencies/mt4-behavioral/
```

The main generated evidence files are:

| File | Purpose |
|---|---|
| `audio-stream-evidence.txt` | Evidence for AudioIO, PortAudio stream lifecycle, and real-time callback behavior |
| `synchronization-evidence.txt` | Evidence for mutexes, atomics, waits, and synchronization primitives |
| `observer-evidence.txt` | Evidence for `Observer::Publisher`, `Publish`, and `Subscribe` behavior |
| `ui-event-evidence.txt` | Evidence for `BasicUI::CallAfter`, wxWidgets event queue, and deferred UI execution |
| `initialization-evidence.txt` | Evidence for `ProjectManager`, registries, module/plugin initialization, and startup ordering |
| `mt4-summary.md` | Summary of behavioral and synchronization dependency evidence |

### 4.3 Real-Time Audio Engine Dependency

Audacity's audio engine introduces a strong behavioral dependency between user actions and lower-level audio stream execution. Playback and recording commands depend on an ordered stream lifecycle: stream configuration, stream opening, stream start, callback execution, stream stop or abort, and stream close.

This can be summarized as:

```text
User action
  -> GUI command
  -> project/audio command layer
  -> AudioIO
  -> PortAudio stream lifecycle
  -> real-time audio callback
```

This is a behavioral dependency because the correctness of the user-visible action depends on the execution sequence inside the audio subsystem. It is also a timing-assumption dependency because the audio callback must execute within real-time constraints.

The architectural risk is that audio-related behavior cannot be understood only by reading the GUI command. The developer must also understand the lower-level stream lifecycle and callback execution path.

### 4.4 Synchronization Dependency

The synchronization evidence shows that Audacity coordinates shared runtime state using synchronization primitives such as mutexes, locks, atomics, waits, or condition variables. These constructs indicate that some execution paths are not independent: one path may wait for another, or multiple paths may require controlled access to the same state.

This is architecturally important because synchronization dependencies are often hidden from static module diagrams. Two components may appear structurally separate but still be coupled by shared locks, atomic flags, or waiting conditions.

In the context of an audio editor, synchronization is especially critical because real-time audio execution must coordinate with UI actions, project state updates, and background operations without blocking the time-sensitive audio path unnecessarily.

### 4.5 Observer-Based Behavioral Dependency

Audacity also uses observer-style notification through publisher/subscriber mechanisms. This creates behavioral dependency because one component can publish a state change and cause other components to react without directly invoking them through an explicit call chain.

This improves structural decoupling because publishers do not need to know all concrete receivers. However, it introduces runtime obscurity: to understand the consequence of a published event, a developer must identify all subscribers and their reactions.

Therefore, observer-based communication trades compile-time coupling for behavioral coupling.

### 4.6 Deferred UI Execution and Event Queue Dependency

Deferred UI execution is another major behavioral coupling point. Calls such as `BasicUI::CallAfter(...)` and wxWidgets event mechanisms schedule work to be executed later on the UI/event thread.

This creates temporal coupling because the requesting component assumes that the deferred operation will run later in a valid UI state. The call site and the execution site are separated in time, which makes the runtime control flow harder to reconstruct from direct call graphs.

This dependency is especially relevant in GUI applications because the event loop becomes a central behavioral coordinator.

### 4.7 Initialization-Order Dependency

Initialization-order dependencies were analyzed around project management, registries, module managers, plugin managers, and startup code. These dependencies occur when one subsystem assumes that another subsystem has already been initialized or registered.

This is a behavioral dependency because correctness depends on startup order. It is also a maintainability risk because adding or moving initialization logic can introduce failures that are not visible as compile-time errors.

### 4.8 Behavioral and Synchronization Dependency Summary

| ID | Dependency surface | Evidence target | Dependency type | Architectural risk |
|---|---|---|---|---|
| B1 | Real-time audio engine | AudioIO / PortAudio stream lifecycle | Behavioral + timing | Playback/recording depends on ordered real-time execution |
| B2 | Audio synchronization | Mutexes, atomics, waits | Synchronization | Hidden runtime coupling through shared state |
| B3 | Observer propagation | Observer publish/subscribe | Behavioral | Indirect propagation obscures call graph |
| B4 | Deferred UI execution | BasicUI::CallAfter / wx events | Behavioral + temporal | Work is scheduled later on the UI thread |
| B5 | Initialization order | ProjectManager / registries / managers | Behavioral | Correctness depends on initialization order |

Overall, MT4 shows that Audacity's dependencies are not only compile-time or data-level dependencies. A significant part of the system's coupling is behavioral: user actions, audio callbacks, observer notifications, UI event queues, and initialization sequences create runtime dependencies that developers must understand when modifying the system.

---

## 5. Overall Dependency Summary

The dependency analysis shows that Audacity's architecture contains significant coupling at three levels.

First, structural dependencies are visible in the inheritance hierarchy, header fan-in/fan-out metrics, and inter-library include graph. The most important structural hotspot is the audio track hierarchy, especially the path from `Track` to `WaveTrack`, and the coupling between built-in effects and wave-track abstractions.

Second, data-level dependencies are concentrated around shared project state, the common track model, persistence representation, and shared preferences. These dependencies are expected in a complex audio editor, but they create hidden coupling because multiple subsystems depend on the same conceptual data structures.

Third, behavioral and synchronization dependencies appear in runtime execution paths. The most important examples are the ordered audio-stream lifecycle, real-time callback execution, synchronization around shared runtime state, observer-based propagation, deferred UI execution, and initialization-order assumptions.

Together, these findings show that Audacity's dependency structure is not only a matter of includes and inheritance. The system also relies on shared state and runtime coordination mechanisms that must be considered when assessing maintainability, modifiability, and architectural risk.