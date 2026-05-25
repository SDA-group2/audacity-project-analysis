# Pattern Analysis — Audacity

**Course:** Software Design and Architecture — PoliTo 2025/2026
**System:** Audacity `master` branch
**Section:** Software Design Report — Patterns

---

## 1. Introduction and Method

This section identifies and analyses design patterns found in the Audacity codebase through
systematic reverse-engineering of the source tree. Evidence was gathered by:

1. **Static grep analysis** — searching the full source tree (`au3/libraries/`, `au3/src/`,
   `au3/modules/`, `src/`) for canonical method names, class-naming conventions, and structural
   idioms associated with each pattern (`Publish`, `Subscribe`, `PushState`, `Undo`, `Factory`,
   `Policy`, `Inject`, etc.).
2. **Header-coupling metrics** — afferent/efferent coupling data from the dependency analysis
   (see the Dependencies section of this report), which reveals structural relationships that
   corroborate pattern boundaries.
3. **Inheritance analysis** — the extracted inheritance hierarchy (`extract_inheritance.py`,
   643 declarations) which surfaces Template Method and Abstract Factory hierarchies.
4. **Knowledge-dependency analysis** — co-change data from the Git history, which shows that
   certain file clusters evolve together and therefore likely share a common pattern.

Each pattern is described using the GoF canonical form (Gamma et al., *Design Patterns*, 1995)
adapted to the course template: **Intent → Participants and roles → Evidence from the codebase →
Why this pattern is used / what problem it solves → Alternative and trade-offs**.

The analysis identifies **five concrete pattern instances** that collectively account for the
most architecturally significant design decisions in the system.

---

## 2. Pattern 1 — Observer

### 2.1 Intent

Define a one-to-many dependency between objects so that when one object (the *Subject*) changes
state, all its dependents (*Observers*) are notified and updated automatically, without the
Subject knowing which concrete observers exist.

### 2.2 Participants and Roles in Audacity

| GoF Role | Audacity Class / Component | Location |
|---|---|---|
| **Subject (Abstract Publisher)** | `Observer::Publisher<Message>` | `au3/libraries/au3-utility/Observer.h` |
| **Concrete Subject** | `AudioIO`, `TrackList`, `UndoManager`, `WaveTrack`, `ProjectCloudExtension`, `OAuthService`, `LabelTrack`, `ProjectSnap`, `ProjectRate` | various `au3/libraries/` |
| **Observer (Subscription handle)** | `Observer::Subscription` | `au3/libraries/au3-utility/Observer.h` |
| **Concrete Observer** | `CommandManager`, `TrackPanel`, `Viewport`, `EffectUI`, `WaveBitmapCache`, `ProjectSelectionManager`, `SqliteSampleBlock` | various |
| **Message / Event** | `AudioIOEvent`, `TrackListEvent`, `UndoRedoMessage`, `WaveTrackMessage`, `CloudStatusChangedMessage`, `RealtimeEffectListMessage`, etc. | per-library headers |

### 2.3 Evidence from the Codebase

The core abstraction lives in `au3/libraries/au3-utility/Observer.h`:

```cpp
// Observer.h:169
CallbackReturn Publish(const Message& message);

// Observer.h:142
[[nodiscard]] Subscription Subscribe(Callback callback);
```

The `Subscription` object is an RAII handle: its destructor automatically unregisters the
callback, making subscription lifetime management explicit and safe.

Publishers are found pervasively across the codebase. Selected examples from
`evidence/publish_usage.txt` (191 lines of matches):

```cpp
// au3/libraries/au3-audio-io/AudioIO.cpp:1215
Publish({ pOwningProject.get(), AudioIOEvent::PLAYBACK, true });

// au3/libraries/au3-track/Track.cpp:488
Publish({ TrackListEvent::ADDITION, *node });

// au3/libraries/au3-project-history/UndoManager.cpp:119
pThis->Publish(message);   // UndoRedoMessage

// au3/libraries/au3-cloud-audiocom/sync/ProjectCloudExtension.cpp:89
Publish(message);   // CloudStatusChangedMessage

// au3/libraries/au3-realtime-effects/RealtimeEffectList.cpp:100
Publisher<RealtimeEffectListMessage>::Publish({ ... });
```

Subscribers from `evidence/subscribe_usage.txt` (55 lines of matches):

```cpp
// au3/libraries/au3-menus/CommandManager.cpp:125
mUndoSubscription{ UndoManager::Get(project)
    .Subscribe(*this, &CommandManager::OnUndoRedo) }

// au3/libraries/au3-viewport/Viewport.cpp:48
UndoManager::Get(project).Subscribe([this](UndoRedoMessage message){ ... });

// au3/src/effects/EffectUI.cpp:1056
mAudioIOSubscription = AudioIO::Get()->Subscribe([this](AudioIOEvent event){ ... });

// au3/libraries/au3-project-file-io/SqliteSampleBlock.cpp:185
mUndoSubscription = UndoManager::Get(project)
    .Subscribe([this](UndoRedoMessage message){ ... });
```

The dependency analysis additionally confirms this pattern at the metrics level:
`Observer.h` (Ca = 87, I = 0.044) is one of the most-included headers in the entire codebase,
reflecting how deeply the Observer mechanism is embedded across all architectural layers.

The behavioral dependency analysis records **1,012 matches** for `callbacks_events` across the
codebase — the dominant behavioral coupling category — which is entirely consistent with a
system whose inter-module communication is built on publish/subscribe.

### 2.4 Why This Pattern Is Used

Audacity's domain demands that many independent components stay in sync with the same changing
state: when playback starts, the UI toolbar, the waveform display, the compression meter panel,
and the effects panel must all respond; when a track is added or deleted, the persistence layer,
the cloud-sync module, the undo history, and the UI must all be notified. Without Observer, each
of these updates would require the changing component to hold a direct reference to every
subscriber — creating dense structural coupling that the architecture analysis shows is already
a risk (e.g., `WaveTrack.h` at Ca = 139). Observer removes those direct references and
replaces them with a single `Publish()` call, satisfying the **Modularity** and
**Maintainability** architectural characteristics documented in the Architecture report.

A secondary motivation is the real-time audio constraint. The PortAudio callback thread cannot
lock mutexes, but it can write to `std::atomic` flags and post lambda closures. The combination
of `BasicUI::CallAfter` (deferred execution on the UI event thread) and `Publish` on
non-RT paths allows safe cross-thread notification without introducing the mutex re-entrancy
risk described in the Dependency Analysis (Section 4.2).

### 2.5 Alternative and Trade-offs

| Alternative | Pros | Cons |
|---|---|---|
| **Direct method calls** (no Observer) | Zero overhead; compile-time type safety; easy to trace call sites | Tight coupling; Subject must know all observers; violates Open/Closed principle — adding a new subscriber requires changing the Subject |
| **Qt Signals & Slots** (already partially present for QML layer) | Integrated with Qt's event loop; thread-safe with `Qt::QueuedConnection`; familiar to Qt developers | Requires `QObject` inheritance, incompatible with the legacy non-Qt `au3/` layer; mixing two notification systems increases complexity |
| **Message bus / event bus** (single global dispatcher) | Complete decoupling — publishers and subscribers never reference each other | Single point of failure; harder to trace who handles what; global state introduces its own coupling |

Audacity's choice of a typed `Publisher<Message>` template is a good compromise: it provides
compile-time message typing (reducing the risk of dispatching to the wrong handler), works
across both the Qt and non-Qt layers, and keeps subscription lifetime visible through RAII.

---

## 3. Pattern 2 — Command

### 3.1 Intent

Encapsulate a request as an object, thereby allowing parameterization of clients with different
requests, queuing or logging of requests, and support for undoable operations.

### 3.2 Participants and Roles in Audacity

| GoF Role | Audacity Class | Location |
|---|---|---|
| **Invoker** | `Menus.cpp` / `MenuRegistry` | `au3/src/menus/`, `au3/libraries/au3-menus/` |
| **Command Dispatcher** | `CommandManager` | `au3/libraries/au3-menus/CommandManager.h` |
| **Command History (Caretaker)** | `UndoManager` | `au3/libraries/au3-project-history/UndoManager.h` |
| **Concrete Command (state snapshot)** | `UndoStackElem` | `au3/libraries/au3-project-history/UndoManager.cpp:16` |
| **Receiver** | `ProjectHistory`, audio-processing components | `au3/libraries/au3-project-history/ProjectHistory.h` |

### 3.3 Evidence from the Codebase

`UndoManager` manages a stack of reversible project states, exposed through the knowledge
dependency analysis as one of the top co-change files in the entire Git history (co-change
count of 120 with `CommandManager.h`). Key method signatures from
`au3/libraries/au3-project-history/UndoManager.cpp`:

```cpp
// UndoManager.cpp:237
void UndoManager::PushState(const TranslatableString& longDescription,
                             const TranslatableString& shortDescription, UndoPush flags);

// UndoManager.cpp:289
void UndoManager::Undo(const Consumer& consumer);

// UndoManager.cpp — RedoAvailable(), UndoAvailable()
bool UndoManager::UndoAvailable();
bool UndoManager::RedoAvailable();
```

`ProjectHistory` acts as the façade that coordinates `UndoManager` for the rest of the system:

```cpp
// ProjectHistory.cpp:67
PushState(desc, shortDesc, UndoPush::NONE);

// ProjectHistory.cpp:81
undoManager.PushState(desc, shortDesc, flags);
```

`CommandManager` subscribes to `UndoRedoMessage` events (via the Observer pattern above) to
keep menu item enablement (Undo/Redo greyed-out state) consistent with the stack:

```cpp
// CommandManager.cpp:125
mUndoSubscription{ UndoManager::Get(project)
    .Subscribe(*this, &CommandManager::OnUndoRedo) }

// CommandManager.cpp:1445
if (undoManager.UndoAvailable()) { ... Enable(wxT("Undo"), ...); }
```

The knowledge-dependency analysis shows `src/commands/CommandManager.cpp` co-changes with
`src/Menus.cpp` 96 times and with `src/Project.cpp` 176 times — confirming that user-facing
menu actions, command dispatch, and project state form a tightly co-evolving cluster,
consistent with a unified Command architecture.

### 3.4 Why This Pattern Is Used

An audio editor is a canonical application of the Command pattern precisely because users
expect **unlimited undo/redo**. Every destructive operation — trimming a clip, applying a
filter, changing gain — must be reversible without corrupting the project. Without Command, this
would require each editing function to manually snapshot and restore state, scattering undo
logic throughout the codebase. `UndoManager` centralises this concern: any component that
calls `ProjectHistory::PushState(...)` automatically participates in undo history, regardless
of which subsystem triggered the change.

The pattern also **decouples the UI from the execution context**: `CommandManager` routes menu
item IDs to handler functions without the menu knowing which audio subsystem will ultimately
be modified. This separation is reflected in the architectural characteristics analysis, which
identifies `Maintainability` and `Modifiability` as primary quality attributes — both of which
are directly supported by keeping execution logic out of the UI layer.

### 3.5 Alternative and Trade-offs

| Alternative | Pros | Cons |
|---|---|---|
| **Memento pattern** (snapshot whole project) | Simple to implement; no need to define individual command classes | Memory-intensive for large projects with many tracks; Audacity already uses SQLite-backed state snapshots in `sampleblocks` which makes full-project copies expensive |
| **Event sourcing** (store all mutations as events, replay to undo) | Fine-grained undo at any level; supports collaborative editing | Complex to implement; requires all state changes to be expressible as pure events; significant architectural upheaval |
| **No undo (direct mutation)** | Simplest code | Unacceptable for a professional audio editor; any mistake permanently destroys the user's work |

The current design using `UndoManager` + `ProjectHistory` is appropriate: it stores compact
project-state snapshots in the SQLite AUP3 database (leveraging existing persistence
infrastructure) and keeps the undo stack decoupled from individual editing functions.

---

## 4. Pattern 3 — Strategy

### 4.1 Intent

Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy
lets the algorithm vary independently from the clients that use it.

### 4.2 Participants and Roles in Audacity

| GoF Role | Audacity Class | Location |
|---|---|---|
| **Strategy (abstract)** | `PlaybackPolicy` | `au3/libraries/au3-audio-io/` |
| **Concrete Strategy A** | `DefaultPlaybackPolicy` | `src/au3audio/internal/defaultplaybackpolicy.h` |
| **Concrete Strategy B** | `ScrubbingPlaybackPolicy` | `au3/src/ScrubState.h:47` |
| **Context** | `Au3AudioEngine` / `AudioIO` | `src/au3audio/internal/au3audioengine.cpp` |
| **Client (factory lambda)** | `options.policyFactory` | `src/au3audio/internal/au3audioengine.cpp:32` |

### 4.3 Evidence from the Codebase

The abstract strategy interface `PlaybackPolicy` defines the algorithm hooks that the audio
engine calls on every buffer period. `DefaultPlaybackPolicy` overrides the full set:

```cpp
// src/au3audio/internal/defaultplaybackpolicy.h:14
class DefaultPlaybackPolicy final : public PlaybackPolicy, public NonInterferingBase {
    void Initialize(PlaybackSchedule&, double rate) override;
    Mixer::WarpOptions MixerWarpOptions(PlaybackSchedule&) override;
    BufferTimes SuggestedBufferTimes(PlaybackSchedule&) override;
    bool Done(PlaybackSchedule&, unsigned long) override;
    double OffsetSequenceTime(PlaybackSchedule&, double offset) override;
    PlaybackSlice GetPlaybackSlice(PlaybackSchedule&, size_t available) override;
    std::pair<double,double> AdvancedTrackTime(...) override;
    bool RepositionPlayback(...) override;
    bool Looping(const PlaybackSchedule&) const override;
};
```

The concrete strategy is injected at stream-start time via a factory lambda:

```cpp
// src/au3audio/internal/au3audioengine.cpp:32
options.policyFactory = [&project, trackEndTime, loopEndTime](
    const AudioIOStartStreamOptions& options) -> std::unique_ptr<PlaybackPolicy>
{
    return std::make_unique<DefaultPlaybackPolicy>(project,
        trackEndTime, loopEndTime, ...);
};
```

`ScrubbingPlaybackPolicy` in `au3/src/ScrubState.h:47` provides an entirely different
concrete strategy that handles the frame-by-frame repositioning required during scrubbing
(dragging the playhead) — a behaviour incompatible with the linear buffer-filling of
`DefaultPlaybackPolicy`.

The architecture notes independently identified this cluster:

> *"Presence of interchangeable policies: `PlaybackPolicy`, `DefaultPlaybackPolicy` …
> different playback behaviors are encapsulated in policy classes, the concrete policy is
> selected at runtime."*

### 4.4 Why This Pattern Is Used

Playback in a DAW is not a single algorithm. Audacity must support at least three qualitatively
different modes: **normal linear playback**, **looped playback** (where the playhead wraps
back to the loop start), and **scrubbing** (where the playhead tracks mouse position in
real time at variable speed). Each mode demands different decisions about when playback is
`Done`, how to compute the next `PlaybackSlice`, how to `AdvancedTrackTime`, and whether to
`RepositionPlayback` mid-buffer.

Without Strategy, `AudioIO` would contain a complex `if/else` or `switch` on playback mode
throughout its buffer-filling loop — a loop that runs in the hard real-time PortAudio callback
(5–20 ms deadline). Adding a new playback mode (e.g., a future metronome-locked mode) would
require modifying `AudioIO`, risking regressions in all other modes.

Strategy externalises these decisions into a dedicated class hierarchy, keeping `AudioIO`'s
callback path clean and satisfying the **Open/Closed Principle**: new playback modes can be
added as new `PlaybackPolicy` subclasses without touching the engine.

### 4.5 Alternative and Trade-offs

| Alternative | Pros | Cons |
|---|---|---|
| **Conditional logic in `AudioIO`** (switch on mode) | Simple; no extra classes; no virtual dispatch | Violates OCP; makes the RT callback harder to test; adding a mode requires modifying a safety-critical component |
| **Template Method** (one base class, subclasses override hooks) | Already close to what `PlaybackPolicy` is — the current design actually uses Template Method *inside* Strategy | No runtime switchability; the policy must be chosen at compile time per stream start |
| **Function pointer / `std::function` callbacks** | Lightweight; no class hierarchy | No state sharing between hooks; callback-per-hook approach fragments cohesion; harder to reason about as a unit |

The factory-lambda injection (`options.policyFactory`) is noteworthy: it delays construction of
the concrete strategy until stream-start, allowing the policy to capture project-specific state
(loop boundaries, start time) without those parameters being stored in `AudioIO` itself.

---

## 5. Pattern 4 — Abstract Factory (Plugin Provider System)

### 5.1 Intent

Provide an interface for creating families of related or dependent objects — here, audio effect
plugin instances — without specifying their concrete classes. Each plugin format (VST, LV2,
LADSPA, AudioUnit, Nyquist, Vamp) constitutes a distinct product family.

### 5.2 Participants and Roles in Audacity

| GoF Role | Audacity Class | Location |
|---|---|---|
| **Abstract Factory** | `PluginProvider` | `au3/libraries/au3-components/PluginProvider.h` |
| **Abstract Product** | `EffectInstanceFactory` / `ComponentInterface` | `au3/libraries/au3-components/EffectInterface.h:659` |
| **Concrete Factory — VST** | `VSTEffectsModule` | `au3/modules/effects/vst/` |
| **Concrete Factory — LV2** | `LV2EffectsModule` | `au3/libraries/au3-lv2/LoadLV2.cpp` |
| **Concrete Factory — LADSPA** | `LadspaEffectsModule` | `au3/libraries/au3-ladspa/` |
| **Concrete Factory — AudioUnit** | `AudioUnitEffectsModule` | `au3/libraries/au3-audio-unit/` |
| **Concrete Factory — Nyquist** | Nyquist module | `au3/modules/nyquist/` |
| **Concrete Product** | `EffectPlugin` (extends `EffectInstanceFactory`) | `au3/libraries/au3-effects/EffectPlugin.h:34` |
| **Client / Registry** | `PluginManager` | `au3/libraries/au3-module-manager/PluginManager.h` |

### 5.3 Evidence from the Codebase

`PluginProvider.h` declares the abstract factory interface. Every concrete plugin-format module
implements it:

```cpp
// au3/libraries/au3-components/PluginProvider.h:82
class COMPONENTS_API PluginProvider : public ComponentInterface {
    virtual void AutoRegisterPlugins(PluginManagerInterface&) = 0;
    virtual PluginPaths FindModulePaths(PluginManagerInterface&, ...) const = 0;
    virtual unsigned DiscoverPluginsAtPath(
        const PluginPath& path, TranslatableString& errMsg,
        const RegistrationCallback& callback) = 0;
    virtual bool CheckPluginExist(const PluginPath& path) const = 0;
    virtual std::unique_ptr<ComponentInterface>
        LoadPlugin(const PluginPath& path) = 0;   // <<< factory method
};
```

`EffectPlugin` is the abstract product:

```cpp
// au3/libraries/au3-effects/EffectPlugin.h:34
class EFFECTS_API EffectPlugin : public EffectInstanceFactory {
    // EffectInstanceFactory.h:661 — "Factory of instances of an effect"
};
```

The concrete factory for LADSPA, for example, calls its own internal `Factory::Call`:

```cpp
// au3/libraries/au3-ladspa/LadspaEffectsModule.cpp:298
auto result = Factory::Call(realPath, (int)index);
```

`PluginManager` acts as the client, using a `ConfigFactory` to decouple itself from the
concrete settings format:

```cpp
// au3/libraries/au3-module-manager/PluginManager.h:85
using ConfigFactory = std::function<
    std::unique_ptr<audacity::BasicSettings>(const FilePath& localFilename)>;
void Initialize(ConfigFactory);  // Dependency injection of the factory

// PluginManager.cpp:890
mSettings = sFactory(FileNames::PluginSettings());
```

Also, `WaveTrackFactory` is the product-level factory used throughout effect processing to
create new `WaveTrack` instances in a format-agnostic way:

```cpp
// au3/libraries/au3-effects/MixAndRender.cpp:103
auto mix = trackFactory->Create(mono ? 1 : 2, *first);

// au3/libraries/au3-audacity-application-logic/AudacityApplicationLogic.cpp:38
auto& trackFactory = WaveTrackFactory::Get(project);
```

The knowledge-dependency analysis provides strong corroborating evidence: the five plugin
backends (VST, LV2, LADSPA, AudioUnit, Nyquist) co-change together at rates of 103–141 commits
per pair, confirming they are maintained as a coordinated family under shared abstract
constraints — exactly the structural signature of Abstract Factory.

### 5.4 Why This Pattern Is Used

Supporting five incompatible plugin standards (VST3, LV2, LADSPA, AudioUnit, Nyquist) on three
operating systems is the core **Extensibility** challenge of Audacity. Each standard has its
own binary interface, discovery mechanism, parameter schema, and GUI protocol. Without an
abstract factory, `PluginManager` would need to `#include` and directly instantiate VST, LV2,
LADSPA, AudioUnit, and Nyquist types — creating compile-time dependencies on every plugin SDK
simultaneously and making it impossible to add a new format (e.g., CLAP, AAX) without
modifying the manager.

`PluginProvider` inverts this dependency: each format module registers itself, and
`PluginManager` interacts only with the `PluginProvider` interface. This directly realises the
**Dependency Inversion Principle**: high-level policy (`PluginManager`) depends on abstractions
(`PluginProvider`), not on concrete plugin SDKs.

The Architecture report identifies this as the primary mechanism enabling the
**Extensibility** characteristic: *"If Audacity needs to support a new type of plugin, it
should not be necessary to rewrite the whole application: it should be enough to add a new
module connected to the effects system."*

### 5.5 Alternative and Trade-offs

| Alternative | Pros | Cons |
|---|---|---|
| **Direct instantiation** (switch on format type) | Simple; no abstract factory overhead | Every new format requires changing `PluginManager`; cross-platform SDK includes pollute compilation; violates OCP |
| **Service Locator** (register format objects by string key) | Dynamic; format names are resolved at runtime | No compile-time interface contract; harder to detect missing implementations; obscures dependencies |
| **Prototype pattern** (clone a registered prototype per plugin) | Avoids subclass explosion | Plugins carry non-copyable system resources (DSP buffers, foreign-ABI handles) making deep-copy semantics hazardous |

---

## 6. Pattern 5 — Dependency Injection (Service Pattern)

### 6.1 Intent

Separate the construction of a component from its use of collaborating services by supplying
concrete implementations of service interfaces at assembly time, rather than having the
component construct or locate them. This is the inversion-of-control realisation of the
**Dependency Inversion Principle**.

### 6.2 Participants and Roles in Audacity

| GoF-adjacent Role | Audacity Class | Location |
|---|---|---|
| **Service Interface** | `IToastService`, `IRealtimeEffectService`, `IAu3AudioComService`, `ISpectrogramService` | `src/toast/itoastservice.h`, `src/effects/`, `src/au3cloud/` |
| **Concrete Service** | `ToastService`, `Au3AudioComService` | `src/toast/internal/`, `src/au3cloud/internal/` |
| **Stub / Test Double** | `Au3AudioComServiceStub` | `src/stubs/au3cloud/au3audiocomservicestub.h` |
| **IoC Container** | `muse::ioc()` / `globalIoc()` | Muse framework (`modularity/ioc.h`, included 129 + 118 times) |
| **Injection site (Global)** | `muse::GlobalInject<T>` | various view/model headers |
| **Injection site (Context-scoped)** | `muse::ContextInject<T>` | various view/model headers |
| **Registration** | `ioc()->registerExport<I>(module, impl)` | module registration files |

### 6.3 Evidence from the Codebase

The IoC container is the most-included internal framework header in the codebase (129
references to `modularity/ioc.h`, 118 to `framework/global/modularity/ioc.h`). Service
interfaces follow a consistent naming convention (`I` prefix):

```cpp
// src/toast/itoastservice.h:16
class IToastService : MODULE_GLOBAL_INTERFACE {
    INTERFACE_ID(IToastService)
    virtual ~IToastService() = default;
    // ...
};
```

Registration at module startup:

```cpp
// src/toast/toastmodule.cpp:37
globalIoc()->registerExport<IToastService>(mname, m_toastService);

// src/au3cloud/au3cloudmodule.cpp:72
ioc()->registerExport<au3cloud::IAu3AudioComService>(mname, m_audioComService);
```

Injection at the point of use via declarative member fields — no manual lookup required:

```cpp
// src/project/internal/projectactionscontroller.h:40
muse::GlobalInject<toast::IToastService> toastService;

// src/projectscene/view/trackspanel/realtimeeffectmenumodelbase.h:36
muse::ContextInject<effects::IRealtimeEffectService> realtimeEffectService{ this };

// src/projectscene/view/toolbars/projecttoolbarmodel.h:22
muse::ContextInject<au::au3cloud::IAu3AudioComService> au3CloudService { this };
```

The stub pattern is the direct payoff of DI: when cloud services are unavailable (offline
build, CI environment, unit test), the stub is registered instead of the real service:

```cpp
// src/stubs/au3cloud/au3audiocomservicestub.h:10
class Au3AudioComServiceStub : public IAu3AudioComService, public muse::Injectable { ... };

// src/stubs/au3cloud/au3cloudstubmodule.cpp:38
ioc()->registerExport<IAu3AudioComService>(mname, new Au3AudioComServiceStub(iocContext()));
```

This is a textbook realisation of the pattern: the consumer (`projectactionscontroller`) never
references `Au3AudioComService` (concrete) or `Au3AudioComServiceStub` — it calls only
`IAu3AudioComService` — and correctness is preserved regardless of which concrete class is
wired by the IoC container at startup.

### 6.4 Why This Pattern Is Used

The architecture analysis identifies Audacity as a **modular monolith** where modules must be
independently testable and optionally deployable. Several services are genuinely optional at
runtime: cloud sync may be unavailable, the spectrogram service may not be licensed on all
platforms, toast notifications may be suppressed in headless mode.

Without DI, every consumer would contain runtime `if (!cloudService) return;` guards and
direct includes of cloud SDK headers, coupling the entire UI layer to cloud availability.
With DI, the IoC container swaps the real implementation for a stub at registration time, and
the consuming code is identical regardless.

The Architecture report directly links this to the **Testability** characteristic:
*"The presence of interfaces, controllers, and separated modules also helps create more focused
tests, without having to start the whole application just to verify a single piece of logic."*
This is precisely what DI enables.

The distinction between `GlobalInject` (application-scoped singleton service) and
`ContextInject` (project-scoped service, re-injected per open project) is architecturally
significant: it mirrors the two-level project context identified in the dependency analysis
(`gPrefs` as global, `AudacityProject` as project-scoped).

### 6.5 Alternative and Trade-offs

| Alternative | Pros | Cons |
|---|---|---|
| **Service Locator** (`static GetInstance()`) | Simple; no framework needed | Global hidden dependency; hard to test; order-of-initialisation issues (the `gPrefs` anti-pattern documented in Dependencies §3.1 is exactly this) |
| **Direct `#include` and instantiation** | Zero framework overhead; straightforward | Tight coupling; impossible to swap for test doubles without modifying production code; the legacy `gPrefs` global demonstrates the maintenance cost of this approach |
| **Constructor injection** (pass services as constructor arguments) | Explicit; no framework required; well-understood | Verbose for classes with many dependencies; does not scale to deeply nested object graphs without a container |

The `muse::GlobalInject` / `muse::ContextInject` approach is a field-injection variant of DI —
the container resolves and assigns the service after construction. This avoids constructor
argument lists growing to dozens of parameters (a real risk given the number of services),
at the cost of making dependencies slightly less visible at the class interface level.

---

## 7. Summary

The table below presents all five patterns together, maps them to the architectural
characteristics documented in the Architecture report, and references the specific design
principles they realise.

| # | Pattern | Confidence | Primary Files | Architectural Characteristic | Design Principle |
|---|---|---|---|---|---|
| 1 | **Observer** | High | `au3-utility/Observer.h`, `AudioIO.cpp`, `UndoManager.cpp`, `TrackList` | Modularity, Maintainability, Performance | Open/Closed, Low coupling |
| 2 | **Command** | High | `UndoManager.cpp`, `ProjectHistory.cpp`, `CommandManager.cpp` | Reliability, Usability, Evolvability | Single Responsibility, Separation of concerns |
| 3 | **Strategy** | High | `defaultplaybackpolicy.h/cpp`, `ScrubState.h`, `au3audioengine.cpp` | Extensibility, Performance | Open/Closed, Dependency Inversion |
| 4 | **Abstract Factory** | High | `PluginProvider.h`, `EffectPlugin.h`, `PluginManager.h`, per-format modules | Extensibility, Portability, Interoperability | Dependency Inversion, Open/Closed |
| 5 | **Dependency Injection** | High | `ioc.h`, `IToastService.h`, `IAu3AudioComService.h`, stub modules | Testability, Modifiability, Modularity | Dependency Inversion, Interface Segregation |

### Cross-Pattern Observations

These five patterns do not operate in isolation — they form an interconnected system:

- **Observer + Command**: `CommandManager` uses the Observer mechanism to receive
  `UndoRedoMessage` events from `UndoManager`, keeping menu state (enabled/disabled Undo and
  Redo items) automatically synchronised with the command stack without any direct call from
  `UndoManager` into the UI layer.

- **Abstract Factory + Dependency Injection**: Plugin modules register `PluginProvider`
  implementations through the IoC container (`RegisteredFactory`), meaning the factory
  hierarchy is itself assembled via DI. This allows platform-specific factories (e.g.,
  `AudioUnitEffectsModule` on macOS only) to be conditionally registered without the rest of
  the system knowing which platform it is running on.

- **Strategy + Observer**: `DefaultPlaybackPolicy` communicates playback position updates back
  to the UI by publishing `AudioIOEvent` messages (Observer), keeping the visual playhead
  cursor in sync without the policy holding a direct reference to any UI component.

Taken together, the patterns reflect a deliberate architectural intent: the system should be
**reactive** (Observer), **reversible** (Command), **algorithmically flexible** (Strategy),
**format-agnostic** (Abstract Factory), and **component-substitutable** (DI). This is
consistent with the stated goal in the Architecture report of transitioning from the legacy
monolithic AU3 core toward a modular, maintainable, and evolvable architecture.

### Relationship to the Dependency Analysis

The Dependency Analysis identified several **cross-dimensional coupling hotspots** —
components that are simultaneously structural, data-level, and behavioural risks. The patterns
above are the primary mechanism by which Audacity manages (though does not fully resolve)
those risks:

- `WaveTrack` (the most dangerous coupling hotspot, Ca = 139) partially mitigates its risk by
  inheriting from `Observer::Publisher<WaveTrackMessage>` — changes to wave data are
  communicated via Observer rather than direct calls, limiting the blast radius of structural
  changes.
- `AudacityProject` (the service-locator hub) is where most `RegisteredFactory` entries are
  attached, making it the assembly point for DI — an acknowledgment that its role as a
  God Object is contained via the factory/DI pattern even if not fully eliminated.
- `gPrefs` (the Common Coupling anti-pattern) has no mitigating pattern yet — the
  Dependencies report recommends replacing it with a typed `IPreferences` interface, which
  would bring it in line with the DI pattern already used for other services.

---

*Evidence files referenced: `analysis/evidence/publish_usage.txt`,
`analysis/evidence/subscribe_usage.txt`, `analysis/evidence/undo_usage.txt`,
`analysis/evidence/command_usage.txt`, `analysis/evidence/factory_usage.txt`,
`analysis/evidence/plugin_usage.txt`;
architecture notes: `notes/davide/finals/candidate_patterns.md`,
`notes/davide/stats/pattern_strategy_candidates.txt`;
dependency analysis: `docs/dependencies-analysis.md`,
`analysis/dependencies/mt2-structural/coupling-metrics.txt`,
`analysis/dependencies/mt4-behavioral/behavioral-dependencies-summary.md`.*
