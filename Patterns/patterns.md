# Pattern Analysis — Audacity

**Course:** Software Design and Architecture — PoliTo 2025/2026
**System:** Audacity `master` branch
**Section:** Software Design Report — Patterns

Five patterns were identified through static grep analysis of the Audacity source tree, header-coupling metrics from the dependency analysis, and Git co-change data. Each follows the GoF canonical form: Intent → Participants → Evidence → Rationale → Alternatives.

---

## 1. Observer

**Intent.** Define a one-to-many dependency so that when a Subject changes state, all
Observers are notified automatically without the Subject referencing them directly.

**Participants.**

| GoF Role | Audacity Class | Location |
|---|---|---|
| Abstract Publisher | `Observer::Publisher<Message>` | `au3/libraries/au3-utility/Observer.h` |
| Concrete Subjects | `AudioIO`, `TrackList`, `UndoManager`, `WaveTrack` | various `au3/libraries/` |
| Subscription handle | `Observer::Subscription` (RAII) | `au3/libraries/au3-utility/Observer.h` |
| Concrete Observers | `CommandManager`, `TrackPanel`, `Viewport`, `EffectUI` | various |

**Evidence.** `Observer.h` (Ca = 87) is among the most-included headers in the codebase, with 191 `Publish` and 55 `Subscribe` call sites:

```cpp
// AudioIO.cpp:1215
Publish({ pOwningProject.get(), AudioIOEvent::PLAYBACK, true });

// CommandManager.cpp:125 — subscribes to undo stack changes
mUndoSubscription{ UndoManager::Get(project)
    .Subscribe(*this, &CommandManager::OnUndoRedo) };
```

The behavioural dependency analysis counts 1,012 `callbacks_events` matches — the dominant
coupling category — confirming that publish/subscribe is the primary inter-module communication
mechanism.

**Rationale.** When playback starts or a track is modified, multiple independent components must respond. Observer decouples these reactions from the event source, satisfying Modularity and Maintainability. The RAII `Subscription` handle eliminates dangling-callback bugs across the PortAudio/UI thread boundary.

**Alternatives.**

| Alternative | Pros | Cons |
|---|---|---|
| Direct method calls | Zero overhead; easy to trace | Subject must know all observers; violates OCP |
| Qt Signals & Slots | Thread-safe; Qt-integrated | Requires `QObject`; incompatible with legacy `au3/` layer |
| Global event bus | Full decoupling | Hidden dependencies; single point of failure |

---

## 2. Command

**Intent.** Encapsulate a request as an object to support undoable operations, queuing,
and decoupled execution.

**Participants.**

| GoF Role | Audacity Class | Location |
|---|---|---|
| Invoker | `MenuRegistry` / `Menus.cpp` | `au3/src/menus/` |
| Command Dispatcher | `CommandManager` | `au3/libraries/au3-menus/CommandManager.h` |
| Caretaker (stack) | `UndoManager` | `au3/libraries/au3-project-history/UndoManager.h` |
| Command snapshot | `UndoStackElem` | `au3/libraries/au3-project-history/UndoManager.cpp` |
| Receiver | `ProjectHistory` | `au3/libraries/au3-project-history/ProjectHistory.h` |

**Evidence.**

```cpp
// UndoManager.cpp:237
void UndoManager::PushState(const TranslatableString& longDescription,
                             const TranslatableString& shortDescription, UndoPush flags);

// ProjectHistory.cpp:81
undoManager.PushState(desc, shortDesc, flags);
```

`CommandManager` co-changes with `Project.cpp` 176 times in the Git history and `undo_usage.txt` contains 993 matching lines — confirming command dispatch and project state are tightly co-evolved.

**Rationale.** Every destructive edit must be reversible. `UndoManager` centralises this: any component calling `ProjectHistory::PushState()` participates in the undo stack. `CommandManager` keeps menu enablement in sync via `UndoRedoMessage` (Observer) without `UndoManager` referencing the UI.

**Alternatives.**

| Alternative | Pros | Cons |
|---|---|---|
| Memento (full snapshot) | Simple to implement | Memory-expensive for large multi-track projects |
| Event sourcing | Fine-grained undo; supports collaboration | Major architectural upheaval; all mutations must be pure events |
| No undo | Simplest code | Unacceptable for a professional audio editor |

---

## 3. Strategy

**Intent.** Define a family of interchangeable algorithms and let the client select one
at runtime without modifying the context.

**Participants.**

| GoF Role | Audacity Class | Location |
|---|---|---|
| Abstract Strategy | `PlaybackPolicy` | `au3/libraries/au3-audio-io/` |
| Concrete Strategy A | `DefaultPlaybackPolicy` | `src/au3audio/internal/defaultplaybackpolicy.h` |
| Concrete Strategy B | `ScrubbingPlaybackPolicy` | `au3/src/ScrubState.h:47` |
| Context | `AudioIO` / `Au3AudioEngine` | `src/au3audio/internal/au3audioengine.cpp` |

**Evidence.** `DefaultPlaybackPolicy` overrides all algorithmic hooks:

```cpp
// defaultplaybackpolicy.h:14
class DefaultPlaybackPolicy final : public PlaybackPolicy {
    bool Done(PlaybackSchedule&, unsigned long) override;
    PlaybackSlice GetPlaybackSlice(PlaybackSchedule&, size_t available) override;
    bool RepositionPlayback(...) override;
    bool Looping(const PlaybackSchedule&) const override;
    // ...
};
```

The concrete strategy is injected at stream-start via a factory lambda:

```cpp
// au3audioengine.cpp:32
options.policyFactory = [&project, trackEndTime, loopEndTime](
    const AudioIOStartStreamOptions&) -> std::unique_ptr<PlaybackPolicy>
{
    return std::make_unique<DefaultPlaybackPolicy>(project, trackEndTime, loopEndTime, ...);
};
```

**Rationale.** Normal, looped, and scrubbing playback have mutually incompatible buffer-filling logic. Strategy externalises each mode into a dedicated class, satisfying OCP: new modes are added as `PlaybackPolicy` subclasses without modifying the real-time audio engine callback.

---

## 4. Abstract Factory (Plugin Provider System)

**Intent.** Provide an interface for creating families of related objects — here, audio
effect plugin instances — without specifying their concrete classes.

**Participants.**

| GoF Role | Audacity Class | Location |
|---|---|---|
| Abstract Factory | `PluginProvider` | `au3/libraries/au3-components/PluginProvider.h` |
| Abstract Product | `EffectPlugin` / `EffectInstanceFactory` | `au3/libraries/au3-effects/EffectPlugin.h` |
| Concrete Factories | `VSTEffectsModule`, `LV2EffectsModule`, `LadspaEffectsModule`, `AudioUnitEffectsModule`, Nyquist module | per-format `au3/` paths |
| Client | `PluginManager` | `au3/libraries/au3-module-manager/PluginManager.h` |

**Evidence.** `PluginProvider.h:82` declares the abstract factory method:
```cpp
virtual std::unique_ptr<ComponentInterface> LoadPlugin(const PluginPath& path) = 0;
```
The five plugin backends co-change at 103–141 commits per pair, confirming they are maintained as a coordinated family.

**Rationale.** Supporting VST3, LV2, LADSPA, AudioUnit, and Nyquist on three OSes is the core Extensibility challenge. `PluginProvider` inverts the dependency so `PluginManager` never references concrete plugin SDKs. Adding a new format requires only a new subclass, realising the Architecture report's stated goal that new plugin types should not require rewriting the application.

**Alternatives.**

| Alternative | Pros | Cons |
|---|---|---|
| Switch on format type in `PluginManager` | Simple | Every new format requires changing the manager; violates OCP |
| Service Locator (register by string key) | Dynamic | No compile-time interface contract; obscures dependencies |

---

## 5. Dependency Injection

**Intent.** Supply concrete implementations of service interfaces at assembly time,
separating construction from use and enabling substitution without modifying consumers.

**Participants.**

| Role | Audacity Class | Location |
|---|---|---|
| Service interfaces | `IToastService`, `IRealtimeEffectService`, `IAu3AudioComService` | `src/toast/`, `src/effects/`, `src/au3cloud/` |
| IoC container | `muse::ioc()` / `globalIoc()` | `modularity/ioc.h` (included 129 times) |
| Injection sites | `muse::GlobalInject<T>`, `muse::ContextInject<T>` | consumer headers |
| Stubs | `Au3AudioComServiceStub` | `src/stubs/au3cloud/` |

**Evidence.**
```cpp
globalIoc()->registerExport<IToastService>(mname, m_toastService); // toastmodule.cpp:37
muse::GlobalInject<toast::IToastService> toastService;              // projectactionscontroller.h:40
ioc()->registerExport<IAu3AudioComService>(mname, new Au3AudioComServiceStub(iocContext())); // stub
```

**Rationale.** Several services are optional at runtime (cloud sync, notifications). Without DI, consumers would embed `if (!cloudService)` guards and include cloud SDK headers directly. With DI, the IoC container swaps in a stub at startup and consuming code is unchanged, enabling the Testability characteristic in the Architecture report. `GlobalInject` (app-scoped) and `ContextInject` (project-scoped) mirror the two-level context in the dependency analysis.

**Alternatives.** A Service Locator (`static GetInstance()`) is simpler but creates the same hidden global-dependency problem that `gPrefs` already demonstrates. Constructor injection is explicit but does not scale to the number of services Audacity uses.

---

## 6. Summary

| # | Pattern | Primary Files | Architectural Characteristic | Principle |
|---|---|---|---|---|
| 1 | **Observer** | `Observer.h`, `AudioIO.cpp`, `UndoManager.cpp` | Modularity, Maintainability | Open/Closed, Low Coupling |
| 2 | **Command** | `UndoManager.cpp`, `ProjectHistory.cpp`, `CommandManager.cpp` | Reliability, Usability | Single Responsibility |
| 3 | **Strategy** | `defaultplaybackpolicy.h`, `ScrubState.h`, `au3audioengine.cpp` | Extensibility, Performance | Open/Closed, DIP |
| 4 | **Abstract Factory** | `PluginProvider.h`, `EffectPlugin.h`, `PluginManager.h` | Extensibility, Portability | Dependency Inversion, OCP |
| 5 | **DI / IoC** | `ioc.h`, `IToastService.h`, stub modules | Testability, Modifiability | DIP, Interface Segregation |

The five patterns form an interconnected system: Observer + Command keeps menu state in sync
with the undo stack; Abstract Factory + DI assembles the plugin hierarchy via the IoC container;
Strategy + Observer allows `DefaultPlaybackPolicy` to publish position updates without holding
any UI reference. Together they realise the architecture's core goal: a reactive, reversible,
format-agnostic, and component-substitutable system.

---

*Evidence: `analysis/evidence/publish_usage.txt`, `subscribe_usage.txt`, `undo_usage.txt`,
`command_usage.txt`, `factory_usage.txt`, `plugin_usage.txt`;
architecture notes: `notes/davide/finals/candidate_patterns.md`;
dependency analysis: `docs/dependencies-analysis.md`, `coupling-metrics.txt`.*
