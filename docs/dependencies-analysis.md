# Dependencies Analysis — Audacity (Master Branch)

**Author:** Seyedeh Fatemeh Moravej | **Course:** Software Design and Architecture — PoliTo 2026  
**System:** Audacity `master` branch | **Branch:** `feature/sahar-dependencies-analysis`

---

## 1. Scope and Methodology

This document reports the dependency analysis performed on the active `master`
branch of Audacity for the Software Design and Architecture course project.
The analysis covers three dependency dimensions required by the course rubric:

1. Structural dependencies
2. Data-level dependencies
3. Behavioral and synchronization dependencies

### 1.1 Active Codebase Requirement

During the project the analysis was migrated from the static `Audacity-3.7.7`
release tag to the active `master` branch to satisfy the course requirement of
analyzing an actively updated software system. This pivot was coordinated with
the architecture team after identifying that a frozen release snapshot would not
fully satisfy the active-codebase criterion.

After switching to `master`, the static-analysis workflow was fully regenerated,
including the compilation database, Cppcheck results, inheritance extraction,
header coupling metrics, inter-library dependency graph, data-level coupling
evidence, and behavioral and synchronization dependency evidence.

### 1.2 Dependency Taxonomy

The analysis follows the dependency dimensions introduced in the course
material [01. Design Intro.pdf, WiringComponents.pdf].

**Structural dependencies** are code-level dependencies where a module must know
another module at compile time. They include inheritance, direct use of concrete
classes, header inclusion, and construction dependencies.

**Data-level dependencies** occur when one component depends on another
component's internal data model, or when multiple components depend on a shared
representation, persistent storage model, or global configuration state.
The coupling classes applied are taken from Yourdon and Constantine's taxonomy
[Structured Design, 1979]: Common Coupling (shared global state), Stamp Coupling
(shared composite data structures), and Schema Coupling (shared persistence
schema).

**Behavioral dependencies** occur when one component influences, schedules, or
dictates another component's execution path. This includes control-flow
dependency, callback dependency, lifecycle-order dependency, and timing-assumption
dependency.

**Synchronization dependencies** occur when one component must wait for or
coordinate with another through locks, atomics, waits, event queues, or
thread-related mechanisms. In this report, synchronization dependencies are
discussed together with behavioral dependencies because Audacity's runtime
behavior combines callback-driven execution, ordering assumptions, deferred
execution, and shared-state coordination.

### 1.3 Toolchain

| Tool | Purpose | Output location |
|---|---|---|
| CMake + Ninja | Generate compilation database | `compile_commands.json` |
| MSVC Build Tools | C/C++ build environment | — |
| Python scripts | Extract structural, data-level, and behavioral dependency evidence | `analysis/dependencies/` |
| `coupling_metrics.py` | Ca / Ce / I header coupling metrics | `analysis/dependencies/mt2-structural/` |
| `behavioral_coupling_analyzer.py` | Behavioral coupling audit | `analysis/dependencies/mt4-behavioral/` |
| Cppcheck | Static-analysis support | `analysis/dependencies/mt2-structural/` |
| Graphviz | Render dependency graph visualizations | `analysis/dependencies/mt2-structural/` |
| CMD `findstr` searches | Targeted source-code evidence extraction | `analysis/dependencies/` |

### 1.4 Methodological Notes

The analysis is interpreted as a design-level dependency assessment. Quantitative
results from the toolchain are used as supporting evidence, while the final
architectural interpretation is based on the role of the affected components in
Audacity's source structure. The goal is to identify architecturally relevant
coupling points and classify them according to the course taxonomy.

---

## 2. Structural Dependencies

### 2.1 Overview

Structural dependencies in the active Audacity `master` branch appear through
compile-time relationships: inheritance chains, header inclusion trees, and
cross-library include edges. The analysis is based on the compilation database
and source-level inspection of `au3/libraries/`, `au3/src/`, `au3/modules/`,
`au3/lib-src/`, and the top-level `src/` directory.

As defined in the course taxonomy [01. Design Intro.pdf], a structural
dependency binds modules at compile time. A change to a base class interface
forces recompilation of all dependent modules and all translation units that
transitively include the modified header. Inheritance is the strongest form
because the subclass is bound to its superclass at the binary level, sharing
not only the interface but the full memory layout.

### 2.2 Compilation Database Baseline

The compilation database contained **1,232 translation units**, distributed
as follows:

| Top-level directory | Translation units |
|---|---:|
| `libraries` | 426 |
| `src` | 375 |
| `lib-src` | 316 |
| `modules` | 83 |
| `tests` | 30 |
| `build-sda` | 1 |
| `win` | 1 |

This confirms that Audacity's compile-time structure is not concentrated only
in `src/`. A large part of the architectural skeleton is implemented inside
internal libraries under `libraries/`, which are the primary evidence targets
for structural analysis.

Because this analysis targets `master`, these numbers represent a snapshot of
an evolving codebase and may shift with active development.

### 2.3 Track Inheritance Chain

The primary inheritance chain from `Track` to `WaveTrack` was extracted via
targeted grep across header files and verified against the raw inheritance
extraction and the track-inheritance summary artifact.

The verified chain is:

```text
Track                     [libraries/lib-track/Track.h]
  └── PlayableTrack       [libraries/lib-track/Track.h]
        └── SampleTrack   [libraries/lib-sample-track/SampleTrack.h]
              └── WritableSampleTrack  [libraries/lib-sample-track/SampleTrack.h]
                    └── WaveTrack      [libraries/lib-wave-track/WaveTrack.h]
```

The measured inheritance depth from `Track` to `WaveTrack` is **4 inheritance
edges**, crossing three internal library boundaries:

```text
lib-track → lib-sample-track → lib-wave-track
```

`WaveTrack` additionally inherits from `Observer::Publisher<WaveTrackMessage>`,
making it simultaneously a domain entity and an event publisher.
`SampleTrack` also inherits from `PlayableSequence`, and `WritableSampleTrack`
from `RecordableSequence`, introducing multiple-inheritance coupling at the
intermediate levels.

**Structural coupling implication:** any modification to `Track`'s virtual
method table — for example adding a new pure virtual method — requires every
subclass across four inheritance levels to provide an implementation before the
project recompiles. This is the Fragile Base Class problem [Gamma et al.,
Design Patterns] directly instantiated in Audacity's audio model.

### 2.4 Header Fan-In / Fan-Out Coupling Metrics

Using `coupling_metrics.py` against the full source tree, the following coupling
profile was established for the six highest-impact headers.
Ca = afferent coupling (fan-in); Ce = efferent coupling (fan-out);
I = Ce / (Ca + Ce), the instability index [Martin, Clean Architecture].

| Header | Path | Ca | Ce | I | Classification |
|---|---|---:|---:|---:|---|
| `Prefs.h` | `lib-preferences/` | 166 | 10 | 0.057 | Maximally stable — change triggers mass recompile |
| `Project.h` | `lib-project/` | 156 | 6 | 0.037 | Maximally stable — central project hub |
| `ShuttleGui.h` | `lib-shuttlegui/` | 151 | 10 | 0.062 | Stable GUI coupling surface |
| `WaveTrack.h` | `lib-wave-track/` | 139 | 13 | 0.086 | Bidirectional coupling hotspot |
| `Track.h` | `lib-track/` | 52 | 13 | 0.200 | Moderately stable base class |
| `AudioIO.h` | `lib-audio-io/` | 40 | 14 | 0.259 | Engine-wide dependency |

High fan-in indicates that many files depend on the header. A change to that
header may trigger wide recompilation and affect many dependent components.
Non-trivial fan-out indicates that the header itself depends on several other
headers, increasing the probability of transitive compile-time coupling.

`WaveTrack.h` is the most architecturally significant hotspot because it
combines the highest fan-in in its category (Ca = 139) with non-trivial fan-out
(Ce = 13). Both axes are problematic simultaneously: many things depend on it,
and it itself depends on many things. `Prefs.h` and `Project.h` have lower
instability but the highest raw fan-in values in the codebase, making changes
to them the most broadly disruptive.

### 2.5 Stable Dependencies Principle Check

The Stable Dependencies Principle [Martin, Clean Architecture] states that
dependencies should point in the direction of stability: a module with high
instability should not be depended upon by a module with low instability.

The headers with low instability values — `Prefs.h` (I = 0.057), `Project.h`
(I = 0.037), `ShuttleGui.h` (I = 0.062), and `WaveTrack.h` (I = 0.086) —
behave as **architectural stability centers**. The SDP is broadly satisfied at
the header level because higher-instability modules depend on these stable
centers, not the reverse.

However, `WaveTrack.h` presents a partial SDP concern: it is stable (low I)
but is itself depended upon by `lib-builtin-effects` and `lib-audio-io`, both
of which carry their own coupling pressures. Changes to `WaveTrack.h` should
therefore be treated as architectural changes, because they propagate
structurally, data-level, and behaviorally across the system simultaneously.

### 2.6 Inter-Library Structural Dependencies

The inter-library dependency extraction scanned **78 `lib-*` directories** and
detected **466 unique inter-library dependency edges**.

Top dependency edges by include count:

| Source library | Target library | Include count |
|---|---|---:|
| `lib-builtin-effects` | `lib-effects` | 53 |
| `lib-builtin-effects` | `lib-wave-track` | 40 |
| `lib-cloud-audiocom` | `lib-network-manager` | 33 |
| `lib-builtin-effects` | `lib-command-parameters` | 25 |
| `lib-cloud-audiocom` | `lib-string-utils` | 22 |
| `lib-wave-track` | `lib-math` | 13 |

The rendered inter-library graph is available at
`analysis/dependencies/mt2-structural/inter-library-graph.svg`.

The most architecturally significant edge is `lib-builtin-effects → lib-wave-track`
with 40 include edges. Built-in audio effects are structurally coupled to the
internal representation of editable audio tracks. Effects cannot be compiled
without knowing `WaveTrack`'s full interface, which means a change to
`WaveTrack.h` forces recompilation of the entire effects library.

**External framework coupling:** Audacity has a structural dependency on the
wxWidgets framework that goes beyond ordinary library usage. Framework types
including `wxFrame`, `wxWindow`, `wxEvtHandler`, and `wxString` appear across
the `src/` layer and inside several `lib-*` libraries that should be
UI-agnostic, including `lib-audio-io` and `lib-effects`. This is framework
coupling: the application is architecturally embedded within wxWidgets, not
merely a client of it. The deferred execution mechanisms discussed in Section 4
are possible only because components already inherit from `wxEvtHandler`.

### 2.7 Structural Risk Summary

| Finding | Evidence | Risk |
|---|---|---|
| Deep `Track → WaveTrack` inheritance chain | 4 edges across 3 `lib-*` boundaries | High — Fragile Base Class |
| `WaveTrack.h` high fan-in | Ca = 139 | High — mass recompile surface |
| `WaveTrack.h` non-trivial fan-out | Ce = 13 | Medium — sensitive to external header changes |
| `Prefs.h` / `Project.h` stability centers | Ca = 166 / 156, I ≈ 0.04 | High change cost — treat as architectural changes |
| Inter-library coupling | 466 unique edges across 78 `lib-*` dirs | Medium — expected but must be managed |
| `lib-builtin-effects → lib-wave-track` | 40 include edges | Medium — effects tightly bound to track internals |
| wxWidgets framework coupling | Framework types inside `lib-audio-io`, `lib-effects` | Medium — inhibits UI-toolkit portability |

### 2.8 Evidence Artifacts

| Artifact | Purpose |
|---|---|
| `analysis/dependencies/mt2-structural/compile-db-structure.md` | Compilation database baseline |
| `analysis/dependencies/mt2-structural/inheritance-raw.txt` | Raw inheritance grep output |
| `analysis/dependencies/mt2-structural/track-inheritance-summary.md` | Verified `Track → WaveTrack` chain |
| `analysis/dependencies/mt2-structural/coupling-metrics.txt` | Header Ca / Ce / I table (top 30) |
| `analysis/dependencies/mt2-structural/inter-library-deps.txt` | Inter-library dependency edges |
| `analysis/dependencies/mt2-structural/inter-library-deps.dot` | Graphviz DOT source |
| `analysis/dependencies/mt2-structural/inter-library-graph.svg` | Rendered inter-library graph |

---

## 3. Data-Level Dependencies

### 3.1 Overview

Data-level dependencies were analyzed to identify coupling through shared
project state, shared data structures, persistent storage schemas, and global
configuration state. Unlike structural dependencies, data-level dependencies
are not only about which header includes which other header. They concern the
shared data representations that multiple subsystems must understand consistently
at runtime.

Following Yourdon and Constantine's coupling taxonomy [01. Design Intro.pdf],
four distinct data-coupling patterns were identified:

| Pattern | Mechanism | Coupling class | Risk |
|---|---|---|---|
| `gPrefs` global registry | `extern wxFileConfig* gPrefs` — untyped global pointer | Common Coupling | High |
| `AudacityProject` state hub | `ClientData::Site<AudacityProject>` service locator | Common + Stamp Coupling | High |
| `TrackList` shared model | `std::shared_ptr<Track>` + `Publisher<TrackListEvent>` | Stamp Coupling | Medium–High |
| AUP3 SQLite persistence | `ProjectFileIO` + `SampleBlock` schema contract | Schema Coupling | Medium |

### 3.2 Common Coupling: The `gPrefs` Global Registry

**Definition applied [01. Design Intro.pdf]:** Common Coupling occurs when two
or more modules share access to the same global data area. Neither module is
aware of the other, yet a write by one affects the read state of all others.

`gPrefs` is declared in `libraries/lib-preferences/Prefs.h` as:

```cpp
extern wxFileConfig* gPrefs;
```

This is a raw global pointer to a `wxFileConfig` file registry, initialized
once during application startup in `Prefs.cpp` and accessed without dependency
injection or synchronization contracts across the codebase.

Components in `lib-audio-io`, `lib-wave-track`, `lib-effects`,
`lib-builtin-effects`, and the legacy `src/` layer all access `gPrefs` directly.
Any component calling `gPrefs->Write("/key", val)` silently modifies the
observable state of every other component reading the same key path, without a
method call, a published event, or a type-safe contract. The coupling surface
is the entire untyped key-value namespace of the configuration file.

This is textbook Common Coupling at Yourdon and Constantine level 2. It is also
an aggravating factor for initialization-order dependencies: `AudioIO.cpp` reads
`gPrefs` during startup to determine buffer sizes and latency thresholds, which
means the audio engine's runtime behavior is determined by global state written
at an earlier, unspecified point in the startup sequence. This is revisited in
Section 4.5.

### 3.3 Common and Stamp Coupling: The `AudacityProject` Service Locator

**Definition applied [WiringComponents.pdf]:** A service locator is a
centralized registry that couples all consumers to a shared hub object.
Components retrieving collaborator objects from the hub are transitively coupled
to every other component registered in the same hub.

`AudacityProject` (declared in `libraries/lib-project/Project.h`) inherits from
`ClientData::Site<AudacityProject>`, a C++ template defined in
`libraries/lib-utility/ClientData.h`. This template implements a runtime service
locator: any component can register an opaque state attachment and retrieve it
later via a type-keyed `::Get(project)` call:

```cpp
// Registration (in component .cpp files):
static AudacityProject::AttachedObjects::RegisteredFactory factory { ... };

// Retrieval (anywhere in the codebase):
auto& myData = MyComponent::Get(project);
```

Components confirmed to attach shared state through this mechanism include
`TrackPanel`, `ProjectHistory` (undo stack), `AudioIO` session data,
`ProjectFileIO` (database connection handle), and selection state managers.
The `AllProjects` global registry also makes the set of open project objects
globally accessible, further widening the coupling surface.

This pattern is both Common Coupling (the project object functions as a global
registry) and Stamp Coupling (components share composite state objects attached
to it). A change to the `AudacityProject` hub's attachment interface propagates
to every component registered through it simultaneously.

### 3.4 Stamp Coupling: The `TrackList` Shared Data Model

**Definition applied [01. Design Intro.pdf]:** Stamp Coupling occurs when
modules share a composite data structure and use only parts of it. The coupling
surface is the full structure, not the portion actually used.

`TrackList` (declared in `libraries/lib-track/TrackList.h`) is the shared
mutable container for all audio, label, and time tracks in an open project.
It serves two roles simultaneously: a shared data store and an event bus.

**Ownership model:** `TrackList` holds tracks via `std::shared_ptr<Track>`,
enabling shared ownership across subsystems. Multiple components — the GUI,
editing commands, effects, playback preparation, and serialization — may hold
live references to the same `Track` object concurrently.

**Observer contract:** `TrackList` extends `Publisher<TrackListEvent>`. The
`TrackListEvent` data structure is the event schema and the stamp-coupling
surface. Every component calling `.Subscribe(...)` on `TrackList` is bound to
this schema: a change to `TrackListEvent`'s fields forces simultaneous updates
across all subscriber components.

The track model is therefore both structurally significant (4-level inheritance
chain, Section 2.3) and data-level significant (shared mutable container accessed
by GUI, editing, effects, playback, and persistence simultaneously). This dual
role makes it a cross-dimensional coupling hotspot, analyzed in Section 5.

### 3.5 Schema Coupling: The AUP3 SQLite Persistence Layer

**Definition applied [WiringComponents.pdf]:** Schema Dependency occurs when
multiple components are coupled through a shared data format or storage schema.
A schema change forces coordinated modification across all consumers, regardless
of whether they communicate directly.

Since Audacity 3.0, the project format is an SQLite database (`.aup3`). The
schema — defined in `src/ProjectFileIO.h` and `src/ProjectFileIO.cpp` —
constitutes a shared persistence contract. Tables including `sampleblocks`,
`tags`, and `autosave` are consumed by multiple components: `WaveTrack`,
`Sequence`, `ProjectFileIO`, and `ProjectManager` are all coupled through the
same table definitions.

Audacity maintains an explicit `ProjectFormatVersion` constant in the source.
Any increment to this version signals a schema change that all consumers must
handle simultaneously — a formal acknowledgment of schema coupling at the
architectural level.

### 3.6 Data-Level Dependency Summary

| Pattern | Coupling class | Architectural risk |
|---|---|---|
| `gPrefs` global registry | Common Coupling | Untyped, unsynchronized global state spans the entire library layer |
| `AudacityProject` service locator | Common + Stamp Coupling | Star-topology hub — change propagates to all attached components |
| `TrackList` shared model | Stamp Coupling | Shared mutable container with embedded event schema contract |
| AUP3 SQLite schema | Schema Coupling | Schema change requires coordinated update across all consumers |

**Aggregate finding:** Audacity's data-level coupling is dominated by a
centralized hub-and-spoke topology. The majority of inter-component data sharing
flows through `AudacityProject` (hub) or `gPrefs` (global) rather than through
explicit, typed message-passing interfaces. This pattern maximizes coupling
breadth: a change to either hub's data contract propagates to the full set of
attached consumers simultaneously.

---

## 4. Behavioral and Synchronization Dependencies

### 4.1 Overview

Behavioral and synchronization dependencies were analyzed to identify runtime
coupling in Audacity. This dimension focuses on execution order, callback
propagation, deferred execution, thread coordination, and timing assumptions.
Unlike structural dependencies, these are not visible in include graphs or
inheritance hierarchies.

Audacity operates across four concurrent execution contexts:

| Thread | Scheduling priority | Real-time safe | Owner |
|---|---|---|---|
| Main / UI Thread | Normal OS | No | wxWidgets event loop |
| `AudioThread` (buffer-fill) | Elevated | Partial | `AudioIO` |
| PortAudio Callback | Hardware IRQ / RT | Mandatory | OS audio subsystem |
| Background Save | Normal OS | No | `ProjectFileIO` |

The analysis identified five runtime coupling surfaces, documented in
`analysis/dependencies/mt4-behavioral/mt4-summary.md`.

### 4.2 Timing Assumption Dependency: The Real-Time Audio Engine

**Definition applied [01. Design Intro.pdf]:** A Timing Assumption Dependency
exists when component A's correct behavior implicitly assumes that component B
will respond within a bounded time window, with no compile-time or
interface-level mechanism to enforce that contract.

The PortAudio callback is invoked by the OS audio subsystem at hardware interrupt
priority with a hard deadline equal to the audio buffer period — typically 5 to
20 milliseconds at standard sample rates. Every instruction executed inside the
callback carries this implicit real-time constraint: overrunning the buffer
period produces an audible dropout in the audio stream.

The behavioral dependency chain is:

```text
User action
  → GUI command
  → project / audio command layer
  → AudioIO::StartStream()
  → PortAudio stream open and start
  → real-time audio callback (per buffer period)
  → AudioIO::StopStream() / AbortStream()
  → stream close
```

This dependency is behavioral because correctness of the user-visible action
depends on the execution sequence inside the audio subsystem. It is also a
timing-assumption dependency because the callback must complete within a
hardware-enforced deadline that no C++ type or interface can express.

**Lock-free transport:** `RingBuffer` is the lock-free circular buffer providing
the only architecturally safe data transport path between the audio callback
thread and the UI thread. Its presence in `lib-audio-io` is itself architectural
evidence of the timing constraint: the design acknowledges that standard
shared-memory access patterns cannot cross this thread boundary safely.

**Cross-thread state access:** `AudioIOBase.h` holds `mOwningProject` as a
`std::weak_ptr<AudacityProject>`, a pointer that crosses the audio thread
boundary. The audio engine accesses project-level shared state from within the
audio context. This is the data-level hub coupling identified in Section 3.3
surfacing as a behavioral risk: the `AudacityProject` dependency becomes a
timing hazard when accessed from a real-time thread.

### 4.3 Synchronization Dependency: Primitive Strategy in `lib-audio-io`

**Definition applied [01. Design Intro.pdf]:** A Synchronization Dependency
exists when one thread's progress is blocked pending another thread reaching a
specific execution point.

The synchronization strategy in `lib-audio-io` is deliberately asymmetric.
The audio engine relies primarily on `std::atomic` flag-based signalling for
cross-thread communication — a lock-free approach that avoids blocking in the
callback context. Standard `std::mutex` and `wxMutex` constructs are used for
non-real-time coordination, but any such lock reachable from the PortAudio
callback context is a priority inversion risk: if the lock-owning thread is
blocked on a slow operation, the callback misses its hardware deadline.

This asymmetry — atomics for the RT path, mutexes for the non-RT path — is an
architectural decision that must be maintained as an invariant. Introducing a
blocking lock into code reachable from the callback, even indirectly, violates
the timing assumption dependency documented in Section 4.2.

### 4.4 Asynchronous Event Coupling: Observer and Publisher Propagation

**Definition applied [WiringComponents.pdf]:** Asynchronous event coupling
occurs when a publisher fires an event and the subscriber executes in a deferred
or non-deterministic context. The coupling surface is the event schema: a change
to the event data structure forces simultaneous updates in all subscribers.

Audacity uses `Observer::Publisher<T>` (declared in
`libraries/lib-utility/Observer.h`) throughout the codebase. Confirmed event
schemas include `Publisher<WaveTrackMessage>` (inherited by `WaveTrack` in
`lib-wave-track`) and `Publisher<TrackListEvent>` (inherited by `TrackList` in
`lib-track`). Each event type constitutes a separate stamp-coupling surface:
all subscribers are bound to the data fields of the published message type.

Every `Observer::Subscription` is an RAII handle. When the subscriber object
is destroyed, the handle destructs and the subscription is cancelled. This
creates an implicit temporal ordering constraint: a subscriber must outlive its
subscription handle, or risk receiving events on a dangling reference. The
correctness of the entire event system depends on object lifetime ordering that
the compiler cannot enforce.

The Observer pattern trades compile-time coupling for behavioral coupling.
Publishers do not need to know all concrete receivers, which reduces structural
coupling. However, to understand the full consequence of a `Publish()` call, a
developer must enumerate all live subscribers at that point in execution — an
analysis that cannot be done statically.

### 4.5 Temporal Coupling: The `CallAfter` Deferred Execution Topology

**Definition applied [01. Design Intro.pdf]:** Temporal Coupling occurs when
correct behavior depends not on what another component does, but on when it
does it — mediated through scheduling, event queues, or deferred callbacks
rather than synchronous call chains.

`BasicUI::CallAfter(fn)` (declared in `libraries/lib-basic-ui/BasicUI.h`) posts
a lambda `fn` to the main UI thread's event queue and returns immediately.
The caller makes no guarantees about when `fn` executes, in what order relative
to other posted lambdas, or whether the UI thread is alive and draining its
queue at any given moment.

`CallAfter` is used throughout the codebase, including inside `lib-audio-io`,
where the audio engine posts state updates to the UI thread. These instances are
the most architecturally significant: the audio engine implicitly assumes that
the UI event loop is alive and will drain its queue within a time window that
does not affect audio stream state. Nothing in the type system enforces this
contract. The call site and the execution site are separated in time, and
completion is unobservable to the caller.

This temporal coupling is structurally enabled by wxWidgets framework coupling:
`CallAfter` is available only because the component already inherits from
`wxEvtHandler`, linking the behavioral coupling directly to the structural
dependency identified in Section 2.6.

### 4.6 Initialization-Order Dependency: Temporal Ordering Coupling

**Definition applied [01. Design Intro.pdf]:** Temporal Ordering Coupling exists
when component A's initialization implicitly assumes that component B has already
completed its own initialization. The dependency is enforced only by programmer
convention, not by the type system.

The following initialization-order dependency chain was confirmed through
source-level inspection of `src/AudacityApp.cpp`, `Prefs.cpp`, and
`src/ProjectManager.cpp`:

```text
Step 1 — Prefs.cpp constructs gPrefs (wxFileConfig*)
  ↓  must complete before
Step 2 — AudioIO::Init() reads gPrefs for buffer size and latency settings
  ↓  must complete before
Step 3 — ProjectManager::OpenProject() calls AudioIO::Get() for stream options
  ↓  must complete before
Step 4 — TrackList population triggers TrackListEvent publications
  ↓  must complete before
Step 5 — UI panels subscribe to TrackListEvent notifications
```

This is a five-step implicit initialization protocol enforced only by
programmer convention. Null-guard patterns such as `if (!gPrefs)` and
`if (!gAudioIO)` scattered across the codebase are runtime acknowledgments
of these ordering dependencies: they confirm that the compiler provides no
protection against incorrect initialization order.

`UndoManager`, attached to `AudacityProject` via `ClientData::Site<>`,
adds a further behavioral coupling dimension: every command in the system must
produce a reversible state snapshot, and the timing of snapshot capture must be
coordinated with audio playback state. This forces all commands to share a
temporal state serialization protocol, making `UndoManager` a behavioral
coupling amplifier that is invisible in the structural include graph.

### 4.7 Behavioral and Synchronization Dependency Summary

| ID | Dependency surface | Type | Architectural risk |
|---|---|---|---|
| B1 | PortAudio RT callback | Timing Assumption | Hard real-time deadline; dropout on overrun |
| B2 | `mOwningProject` cross-thread access | Data + Behavioral | Hub coupling becomes timing hazard in RT context |
| B3 | Atomic vs mutex strategy in `lib-audio-io` | Synchronization | Invariant must be maintained; any lock in RT path is priority inversion |
| B4 | `Publisher<WaveTrackMessage>`, `Publisher<TrackListEvent>` | Async Event | Event schema changes require simultaneous subscriber updates |
| B5 | `Observer::Subscription` RAII lifetime | Temporal Ordering | Subscriber lifetime must exceed subscription handle lifetime |
| B6 | `BasicUI::CallAfter` in `lib-audio-io` | Temporal | Audio engine assumes UI event loop is live and responsive |
| B7 | `gPrefs → AudioIO → ProjectManager` chain | Temporal Ordering | Five-step init protocol enforced only by convention |

---

## 5. Cross-Dimensional Coupling Hotspot Analysis

The previous sections analyzed structural, data-level, and behavioral
dependencies separately. However, the highest architectural risk is not produced
by a component that is coupled in only one dimension. The most critical risk
appears when the same component is simultaneously a structural hotspot, a
data-level shared-state element, and a behavioral runtime coordination point.

The following table identifies components that appear as high-risk nodes across
all three dependency dimensions:

| Component | Structural risk | Data-level risk | Behavioral risk | Overall |
|---|---|---|---|---|
| `WaveTrack` | 4-level inheritance chain; `WaveTrack.h` Ca = 139, Ce = 13; anchor of `lib-builtin-effects` coupling (40 edges) | Shared audio-track representation used by editing, effects, playback, and persistence; held via `shared_ptr` in `TrackList` | Processed by PortAudio callback thread; inherits `Publisher<WaveTrackMessage>`; state changes propagate to UI and audio threads concurrently | **Critical** |
| `AudacityProject` / `Project.h` | Ca = 156, I = 0.037; structural hub referenced across all `lib-*` layers | Central service locator for all attached components via `ClientData::Site<>`; `AllProjects` global registry | Head of the five-step initialization-order chain; project lifecycle controls audio start and stop and undo sequencing | **High** |
| `AudioIO` / `AudioIO.h` | Ca = 40, Ce = 14, I = 0.259; depends on Track hierarchy, `WaveTrack`, and `SampleBlock` | Reads `gPrefs` during initialization; holds `mOwningProject` as a `weak_ptr` crossing the thread boundary | Owns PortAudio stream lifecycle, atomic state flags, `CallAfter` emission, and timing assumption dependency | **High** |
| `TrackList` | Central container of the track hierarchy; `Publisher<TrackListEvent>` declared in `lib-track` | Shared mutable model accessed by GUI, editing, effects, playback, and serialization; `shared_ptr<Track>` ownership | Async event bus for the entire track model; subscription RAII lifetime ordering constraint | **Medium–High** |
| `Prefs.h` / `gPrefs` | Ca = 166, I = 0.057; most-included header in the codebase | Common Coupling across all library layers; untyped key-value namespace | Read by `AudioIO` during RT-sensitive initialization; couples startup order to configuration availability | **Medium–High** |

This synthesis shows that Audacity's architectural risk is concentrated in a
small number of components. These components are not problematic merely because
they have many includes or many callers. They are risky because they combine
compile-time coupling, shared data representation, and runtime coordination
responsibilities simultaneously. A change to any of these components propagates
across all three dependency dimensions at once.

---

## 6. Overall Dependency Summary and Conclusions

### 6.1 Summary of Findings

The dependency analysis shows that Audacity's architecture contains significant
coupling at three levels.

**Structural dependencies** are visible in the inheritance hierarchy (4 levels
from `Track` to `WaveTrack` across 3 library boundaries), in header fan-in and
fan-out metrics (Ca = 139 for `WaveTrack.h`, Ca = 166 for `Prefs.h`), and in
the inter-library include graph (466 unique edges across 78 `lib-*` directories).
The most important structural hotspot is the audio track hierarchy and the
coupling between `lib-builtin-effects` and `lib-wave-track`.

**Data-level dependencies** are concentrated around four mechanisms: the `gPrefs`
Common Coupling global (accessed across multiple libraries without a typed
interface), the `AudacityProject` service locator hub (used by all major
subsystems), the `TrackList` Stamp Coupling model (shared mutable container with
embedded Observer contract), and the AUP3 SQLite Schema Coupling (shared
persistence tables consumed by audio, project, and history subsystems).

**Behavioral and synchronization dependencies** appear in runtime execution paths.
The most important are the real-time PortAudio callback with a hard timing
deadline, the atomic-vs-mutex synchronization strategy in `lib-audio-io`, the
`Publisher<WaveTrackMessage>` and `Publisher<TrackListEvent>` asynchronous event
schemas, the `CallAfter` deferred execution pattern bridging the audio engine to
the UI thread, and the five-step initialization-order chain from `gPrefs` through
`AudioIO` to `ProjectManager`.

Together, these findings confirm that Audacity's dependency structure is not only
a matter of includes and inheritance. The system relies on shared state and
runtime coordination mechanisms that must be considered when assessing
maintainability, modifiability, and architectural risk.

### 6.2 Cohesion as a Complementary Concern

This report focuses on coupling. Cohesion is the complementary design-quality
dimension and was not formally measured, but it is relevant to the findings.
The components identified as cross-dimensional coupling hotspots — particularly
`WaveTrack` — are also strong candidates for low cohesion: `WaveTrack` manages
audio sample representation, clip editing, track state, effect interaction, and
playback-related workflows within a single class boundary. A future analysis
applying LCOM (Lack of Cohesion in Methods) metrics to `WaveTrack` would likely
confirm that its high coupling is correlated with low internal cohesion — the
standard symptom of a God Class design smell [Riel, Object-Oriented Design
Heuristics, 1996].

### 6.3 Priority Refactoring Directions

Based on coupling severity observed across the three dependency dimensions, the
following refactoring directions would reduce architectural risk most effectively:

1. **Replace `gPrefs` Common Coupling with a typed dependency-injected
   interface.** Introducing an `IPreferences` interface and injecting it
   explicitly into components that require configuration state would replace
   untyped Common Coupling with Data Coupling at well-defined, testable
   boundaries, and would also eliminate the initialization-order constraint
   between `Prefs.cpp` and `AudioIO::Init()`.

2. **Apply Interface Segregation around the `WaveTrack` track model.** Separating
   the audio sample access interface (`ISampleProvider`) from the clip-management
   interface (`IClipEditor`) and from UI-facing track behavior would reduce
   `WaveTrack.h`'s efferent coupling without disturbing its existing fan-in
   relationships. This directly addresses the bidirectional coupling hotspot
   identified in Section 2.4.

3. **Introduce an explicit event-dispatcher abstraction between `lib-audio-io`
   and the UI thread.** A typed `IAudioEventDispatcher` interface replacing
   direct `CallAfter` calls from the audio engine would make the temporal coupling
   in Section 4.5 explicit, testable, and independent of the wxWidgets event
   model, reducing both behavioral coupling and wxWidgets framework coupling in
   `lib-audio-io` simultaneously.

---

## Appendix: Evidence Artifacts Index

| Artifact | Dependency dimension |
|---|---|
| `analysis/dependencies/mt2-structural/compile-db-structure.md` | Structural |
| `analysis/dependencies/mt2-structural/inheritance-raw.txt` | Structural |
| `analysis/dependencies/mt2-structural/track-inheritance-summary.md` | Structural |
| `analysis/dependencies/mt2-structural/coupling-metrics.txt` | Structural |
| `analysis/dependencies/mt2-structural/inter-library-deps.txt` | Structural |
| `analysis/dependencies/mt2-structural/inter-library-deps.dot` | Structural |
| `analysis/dependencies/mt2-structural/inter-library-graph.svg` | Structural |
| `analysis/dependencies/mt4-behavioral/audio-stream-evidence.txt` | Behavioral |
| `analysis/dependencies/mt4-behavioral/synchronization-evidence.txt` | Behavioral |
| `analysis/dependencies/mt4-behavioral/observer-evidence.txt` | Behavioral |
| `analysis/dependencies/mt4-behavioral/ui-event-evidence.txt` | Behavioral |
| `analysis/dependencies/mt4-behavioral/initialization-evidence.txt` | Behavioral |
| `analysis/dependencies/mt4-behavioral/mt4-summary.md` | Behavioral |