# Design Pattern Hints – Audacity Source Code

This file contains short hints for the design pattern analysis.  
Only the first pattern is meant to be developed fully; the others are intentionally short so they can be expanded by the rest of the group.

---

## 1. Builder / Application Builder

### Classes involved

```text
src/app/main.cpp
src/app/appfactory.cpp
src/app/appfactory.h
src/app/guiapp.h
src/app/guiapp.cpp
src/app/pluginregistrationapp.h
src/app/pluginregistrationapp.cpp
```

Main classes / concepts:

```text
AppFactory
GuiApp
PluginRegistrationApp
IApplication
AudacityCmdOptions
RunMode
```

### Why this pattern is used

Audacity does not start by directly creating a single fixed application object.  
The startup phase first reads the command-line options, identifies the required run mode, and then delegates the construction of the correct application to `AppFactory`.

Depending on the run mode, the application can be built as a normal GUI application or as a specific application used for audio plugin registration.

For this reason, `AppFactory` can be interpreted as a **Builder-like Application Builder**: it centralizes the construction and configuration of the application instead of spreading this logic across `main.cpp`.

### Problem solved

This pattern keeps the startup logic cleaner and allows Audacity to support different execution modes without making the entry point responsible for all construction details.

In simple terms:

> `main.cpp` starts the process, but `AppFactory` decides how the actual application must be built.

---

# Other pattern hints

## 2. Facade

- Many modules expose a `*Module` class, such as `AudioModule`, `AppShellModule`, `EffectsModule`, `TrackEditModule`, `ToastModule`.
- These classes can be interpreted as Facades because they expose each subsystem through a clean entry point, hiding internal services/controllers from `AppFactory` and the rest of the application.

---

## 3. Command

- The UI action system around `ApplicationUiActions`, `ApplicationActionController`, `IActionsDispatcher` and `ActionCode` is a good Command-like example.
- UI elements trigger actions by code, while the controller/dispatcher decides which operation must actually be executed.

---

## 4. Adapter

- `au3wrap`, especially classes such as `IAu3Project` and `Au3ProjectAccessor`, works as an Adapter between the new modular frontend and the legacy AU3 core.
- It allows the new architecture to use old AU3 functionality without depending directly on all legacy implementation details.

---

## 5. Strategy / Plugin Provider

- The effect/plugin system uses a common abstraction such as `IEffectLoader`, with concrete loaders like `BuiltinEffectsLoader`, `NyquistEffectsLoader`, `Vst3EffectLoader`, `Lv2EffectLoader` and `AudioUnitEffectLoader`.
- Each loader provides a different strategy for loading a specific family of effects/plugins.


---


## 6. Service Locator

### Where it appears in the code

The Service Locator pattern appears in Audacity through the project-scoped object registry implemented by `AudacityProject` and `ClientData::Site<AudacityProject>`.

Main source locations:

```text
au3/libraries/lib-project/Project.h
au3/libraries/lib-utility/ClientData.h
au3/libraries/lib-project-history/
au3/src/ProjectFileIO.h
au3/libraries/lib-audio-io/

```

### Involved classes and roles

| Pattern role | Audacity element |
|---|---|
| Service Locator / Registry | `AudacityProject` |
| Registry mechanism | `ClientData::Site<AudacityProject>` |
| Service base type | `ClientData::Base` |
| Concrete services | `UndoManager`, `ProjectFileIO`, AudioIO project/session data |
| Client | Any component calling `ServiceName::Get(project)` |

### Problem it solves

Audacity has many project-scoped services that need to share the same lifetime as an open project. Examples include undo history, project persistence, audio I/O state, selection state, and track-related services.

Passing all these services explicitly through constructors would create long dependency chains and would make many components depend directly on services they do not always need.

Instead, Audacity uses `AudacityProject` as a project-level service registry. Components that need a service retrieve it from the project object, for example through a static accessor such as `UndoManager::Get(project)`.

In this way, `AudacityProject` becomes a central access point for project-scoped services. New services can be attached to the project without modifying every client that uses the project.

### Why this pattern is used

The pattern is useful because Audacity is a large modular desktop application with many subsystems. The same open project must coordinate editing, playback, persistence, history, and UI state. A Service Locator gives these subsystems a common project-scoped context.

It also supports extensibility: services can be registered and retrieved without forcing `AudacityProject` to explicitly construct every possible concrete subsystem in its own source code.

### Possible alternatives

A possible alternative is Dependency Injection. With Dependency Injection, each component would receive the services it needs through its constructor or setter methods. This would make dependencies more explicit and would improve testability, because mock services could be passed during unit testing.

However, in a large application like Audacity, pure Dependency Injection could create complex constructor chains and require a large amount of explicit wiring. The Service Locator is simpler for project-scoped services, but it hides dependencies and makes them harder to detect with static analysis.

### Critical evaluation

The Service Locator pattern is a reasonable architectural trade-off in Audacity. It improves lifecycle management because services are tied to the lifetime of `AudacityProject`, and it avoids spreading service construction logic throughout the codebase.

However, it also introduces hidden coupling. Any component with access to an `AudacityProject` can retrieve many services without declaring those dependencies explicitly in its interface. This makes the design less transparent and can reduce testability.

Therefore, the pattern solves a real extensibility and lifecycle problem, but it also contributes to the dependency hotspot around `AudacityProject`.
