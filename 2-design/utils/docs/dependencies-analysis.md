# Dependencies Analysis — Audacity (Master Branch)

**Author:** Seyedeh Fatemeh Moravej | **Course:** Software Design and Architecture — PoliTo 2026
**System:** Audacity `master` branch | **Branch:** `feature/sahar-dependencies-analysis`

---

## 1. Scope and Methodology

This section analyzes dependency coupling in the active Audacity `master` branch
across three dimensions from the course taxonomy [01. Design Intro.pdf]:
structural, data-level, and behavioral and synchronization dependencies.

The analysis is grounded in a compilation database of **1,232 translation units**
generated via CMake. Evidence was extracted using `coupling_metrics.py`,
`behavioral_coupling_analyzer.py`, Cppcheck, and Graphviz. The codebase covers
`au3/libraries/`, `au3/src/`, `au3/modules/`, and top-level `src/`, confirming
that Audacity's compile-time skeleton is not concentrated only in `src/` but
distributed across modular internal libraries. Coupling classes follow Yourdon
and Constantine's taxonomy [Structured Design, 1979] throughout.

---

## 2. Structural Dependencies

Structural dependencies arise from compile-time relationships: inheritance,
header inclusion, and cross-library coupling. A change to a base class interface
forces recompilation of every dependent module and every translation unit that
transitively includes the modified header.

### 2.1 Track Inheritance Chain

The primary inheritance chain spans **4 inheritance edges** across three library boundaries:

```
Track [lib-track] → PlayableTrack → SampleTrack [lib-sample-track]
  → WritableSampleTrack → WaveTrack [lib-wave-track]
```

`WaveTrack` additionally inherits from `Observer::Publisher<WaveTrackMessage>`,
making it simultaneously a domain entity and an event publisher. `SampleTrack`
also inherits from `PlayableSequence` and `WritableSampleTrack` from
`RecordableSequence`, introducing multiple-inheritance coupling at intermediate
levels. Any modification to `Track`'s virtual method table forces every subclass
across four inheritance edges to provide an implementation before the project
recompiles — the Fragile Base Class problem [Gamma et al., Design Patterns],
directly instantiated in Audacity's audio model.

### 2.2 Header Coupling Metrics

Ca = afferent coupling (fan-in); Ce = efferent coupling (fan-out);
I = Ce / (Ca + Ce) instability index [Martin, Clean Architecture].

| Header | Ca | Ce | I | Risk |
|---|---:|---:|---:|---|
| `Prefs.h` | 166 | 10 | 0.057 | Maximally stable — mass recompile surface |
| `Project.h` | 156 | 6 | 0.037 | Maximally stable — central hub |
| `WaveTrack.h` | 139 | 13 | 0.086 | Bidirectional coupling hotspot |
| `Track.h` | 52 | 13 | 0.200 | Moderately stable base class |
| `AudioIO.h` | 40 | 14 | 0.259 | Engine-wide dependency |

`WaveTrack.h` is the most dangerous header: high fan-in (Ca = 139) combined
with non-trivial fan-out (Ce = 13) means it is both widely depended upon and
itself sensitive to external changes. `Prefs.h` and `Project.h` have the
highest raw fan-in values in the codebase, making changes to them the most
broadly disruptive even though their instability index is low. The Stable
Dependencies Principle [Martin] is broadly satisfied — higher-instability
modules depend on these low-I centers — but `WaveTrack.h` carries
disproportionate change-propagation risk on both coupling axes simultaneously.

### 2.3 Inter-Library Coupling

Scanning **78 `lib-*` directories** detected **466 unique inter-library
dependency edges**. The highest-weight edge is
`lib-builtin-effects → lib-wave-track` with 40 include edges: effects cannot
compile without knowing `WaveTrack`'s full interface. Audacity also exhibits
**framework coupling** to wxWidgets — `wxEvtHandler`, `wxString`, and
`wxFrame` appear inside nominally UI-agnostic libraries such as `lib-audio-io`
and `lib-effects`, inhibiting toolkit portability and directly enabling the
behavioral coupling described in Section 4.3.

---

## 3. Data-Level Dependencies

Data-level dependencies couple components through shared state, shared data
structures, or a common persistence schema rather than through explicit interfaces.
Four coupling patterns were identified following Yourdon and Constantine's
taxonomy.

### 3.1 Common Coupling — `gPrefs` Global Registry

`gPrefs` is declared in `lib-preferences/Prefs.h` as `extern wxFileConfig* gPrefs`.
It is accessed without dependency injection or synchronization across
`lib-audio-io`, `lib-wave-track`, `lib-effects`, `lib-builtin-effects`, and the
legacy `src/` layer. Any component writing a key silently affects every reader
of that key — Common Coupling at Yourdon and Constantine level 2. `AudioIO.cpp`
reads `gPrefs` during initialization for buffer sizes and latency thresholds,
creating an initialization-order dependency revisited in Section 4.5.

### 3.2 Stamp Coupling — `AudacityProject` Service Locator

`AudacityProject` inherits from `ClientData::Site<AudacityProject>`
(`lib-utility/ClientData.h`), a runtime service locator: any component
registers an opaque state attachment and retrieves it via a type-keyed
`::Get(project)` call. Components including `TrackPanel`, `ProjectHistory`,
`AudioIO`, and `ProjectFileIO` all share state through this hub. This is
both Common Coupling (project as global registry) and Stamp Coupling
(composite state objects attached to it). A change to the hub's attachment
interface propagates to every registered component simultaneously.

### 3.3 Stamp Coupling — `TrackList` Shared Data Model

`TrackList` (`lib-track/TrackList.h`) holds tracks via `std::shared_ptr<Track>`,
granting shared ownership to the GUI, editing commands, effects, playback, and
serialization concurrently. It also extends `Publisher<TrackListEvent>`,
making `TrackListEvent` a stamp-coupling surface: all subscribers are bound to
its data fields, and a schema change forces simultaneous updates across every
subscriber.

### 3.4 Schema Coupling — AUP3 SQLite Persistence

Since Audacity 3.0, projects are stored as SQLite databases (`.aup3`). The
schema defined in `ProjectFileIO.cpp` — tables `sampleblocks`, `tags`, `autosave`
— is a shared persistence contract consumed by `WaveTrack`, `Sequence`,
`ProjectFileIO`, and `ProjectManager`. An explicit `ProjectFormatVersion`
constant acknowledges that schema changes require coordinated updates across all
consumers simultaneously.

---

## 4. Behavioral and Synchronization Dependencies

Behavioral dependencies are invisible to static analysis: they emerge at runtime
through execution order, thread coordination, and timing constraints.
Audacity operates across four concurrent contexts: Main UI Thread,
`AudioThread` (buffer-fill), PortAudio Callback (real-time audio callback
context), and Background Save Thread.

### 4.1 Timing Assumption — Real-Time Audio Engine

The PortAudio callback is invoked at hardware interrupt priority with a hard
deadline equal to the audio buffer period (typically 5–20 ms at standard sample
rates). The behavioral dependency chain is:

```
User action → GUI → AudioIO::StartStream()
  → PortAudio callback (per buffer period, RT deadline)
  → AudioIO::StopStream()
```

This is a Timing Assumption Dependency [01. Design Intro.pdf]: correct behavior
requires the callback to complete within a hardware-enforced window that no
C++ type or interface can express. `RingBuffer` in `lib-audio-io` is the
lock-free circular buffer providing the only architecturally safe data transport
path between the callback and the UI thread. `AudioIOBase.h` holds
`mOwningProject` as a `std::weak_ptr<AudacityProject>`, crossing the audio
thread boundary — the hub coupling from Section 3.2 becomes a timing hazard
in the real-time context.

### 4.2 Synchronization — Atomic vs Mutex Strategy

`lib-audio-io` relies primarily on `std::atomic` flags for cross-thread
communication — a lock-free strategy that preserves real-time safety. Standard
`std::mutex` constructs are used only on non-RT coordination paths. Any mutex
reachable from the PortAudio callback risks priority inversion: if the owning
thread blocks on a slow operation, the callback misses its deadline and an
audible dropout occurs. This asymmetry is an architectural invariant that must
be maintained as the codebase evolves.

### 4.3 Temporal Coupling — `CallAfter` Deferred Execution

`BasicUI::CallAfter(fn)` posts a lambda to the UI thread's event queue and
returns immediately, with no guarantee of when or whether `fn` executes.
Used inside `lib-audio-io` to post playback state updates to the UI thread,
it creates Temporal Coupling [01. Design Intro.pdf]: the audio engine
implicitly assumes the UI event loop is alive and will drain its queue within
a bounded time window. Nothing in the type system enforces this contract.
This coupling is structurally enabled by wxWidgets — `CallAfter` is available
only because components inherit from `wxEvtHandler`.

### 4.4 Asynchronous Event Coupling — Observer Propagation

`Observer::Publisher<T>` is used throughout the codebase. Confirmed event
schemas include `Publisher<WaveTrackMessage>` (inherited by `WaveTrack`) and
`Publisher<TrackListEvent>` (inherited by `TrackList`). Each schema is a
stamp-coupling surface: subscribers are bound to its fields, and a change
forces simultaneous updates across all subscribers. Every
`Observer::Subscription` is an RAII handle — subscribers must outlive their
handles, an ordering constraint the compiler cannot enforce.

### 4.5 Temporal Ordering — Initialization-Order Dependency

A five-step initialization protocol exists by programmer convention only:

```
① Prefs.cpp constructs gPrefs
② AudioIO::Init() reads gPrefs for buffer and latency settings
③ ProjectManager::OpenProject() calls AudioIO::Get() for stream options
④ TrackList population triggers TrackListEvent publications
⑤ UI panels subscribe to TrackListEvent notifications
```

Null-guard patterns (`if (!gPrefs)`, `if (!gAudioIO)`) scattered throughout
the codebase are runtime acknowledgments of these ordering dependencies,
confirming that the compiler provides no protection against incorrect
initialization sequencing.

---

## 5. Cross-Dimensional Coupling Hotspot Analysis

The highest architectural risk lies where the same component is simultaneously
a structural hotspot, a data-level shared-state element, and a behavioral
runtime coordination point. The following components appear as high-risk nodes
across all three dimensions:

| Component | Structural | Data-Level | Behavioral | Risk |
|---|---|---|---|---|
| `WaveTrack` | 4-level chain; Ca=139, Ce=13; 40 edges to `lib-builtin-effects` | `shared_ptr` in TrackList; `Publisher<WaveTrackMessage>` schema | RT callback access; concurrent UI and audio thread state changes | **Critical** |
| `AudacityProject` | Ca=156, I=0.037; hub across all `lib-*` layers | Service locator for all subsystems via `ClientData::Site<>` | Head of 5-step initialization chain | **High** |
| `AudioIO` | Ca=40, Ce=14, I=0.259 | Reads `gPrefs`; holds cross-thread `mOwningProject` | Owns RT callback, atomic flags, `CallAfter` emission | **High** |
| `Prefs.h` / `gPrefs` | Ca=166, I=0.057; most-included header | Common Coupling across the entire library layer | Read during RT-sensitive initialization | **Medium–High** |

These components are risky not because of any single coupling dimension, but
because a change propagates structurally, through shared data, and across
runtime execution boundaries simultaneously. Priority refactoring directions
are: replacing `gPrefs` with a typed `IPreferences` interface to break Common
Coupling; applying Interface Segregation to `WaveTrack` to reduce its
bidirectional coupling; and introducing an `IAudioEventDispatcher` abstraction
to replace direct `CallAfter` calls from `lib-audio-io`, making Temporal
Coupling explicit and testable.

---

*Evidence artifacts: `analysis/dependencies/mt2-structural/`
(coupling-metrics.txt, inter-library-graph.svg, inheritance-raw.txt)
and `analysis/dependencies/mt4-behavioral/`
(audio-stream-evidence.txt, synchronization-evidence.txt,
observer-evidence.txt, ui-event-evidence.txt, initialization-evidence.txt).*