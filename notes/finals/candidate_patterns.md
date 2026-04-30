# Candidate Patterns

## Overview

The analysis of the source code highlights several recurring design patterns used in Audacity. These patterns are inferred from:
- naming conventions (e.g., *Service*, *Model*, *Policy*, *Listener*)
- class structure and inheritance
- interaction mechanisms (e.g., notifications, event handling, dependency injection)

---

## 1. Observer Pattern

### Evidence

The codebase makes extensive use of notification-based communication:

- `.onNotify(...)` and `.onReceive(...)` calls
- `.notify()` triggers in multiple components
- event-based subscriptions

Examples:
- Preferences models reacting to configuration changes  
- Audio device provider notifying UI components  
- Project scene reacting to state changes  

```cpp
audioDevicesProvider()->apiChanged().onNotify(this, [this]() { ... });
m_audioApiChanged.notify();
```

### Interpretation

This strongly indicates the use of an Observer pattern, where:

- subjects emit events or notifications
- observers subscribe and react asynchronously

### Role in the system
- decouples UI from business logic
- enables reactive updates across modules
- widely used in:
  - preferences system
  - audio subsystem
  - project scene
## 2. Service Pattern (Dependency Injection)

### Evidence

Several classes follow a Service + Interface structure:

- IAu3AudioComService
- IRealtimeEffectService
- IToastService

Injected via:
```
muse::ContextInject<effects::IRealtimeEffectService> realtimeEffectService{ this };
```
or:
```
muse::GlobalInject<IToastService> toastService;
```
### Interpretation

This suggests a Service pattern with Dependency Injection, where:

- services are accessed through interfaces
- concrete implementations are injected at runtime

### Role in the system
- decouples components from concrete implementations
- enables modular architecture
- allows swapping implementations (e.g., real vs stub)

## 3. Stub Pattern (Testing / Fallback)

### Evidence

Presence of explicit Stub implementations:

- Au3AudioComServiceStub
- QML viewer stubs for plugins (VST, LV2, AudioUnit)

Example:

```cpp
class Au3AudioComServiceStub : public IAu3AudioComService
```

### Interpretation

This indicates a Stub pattern, used to:

- replace real services when unavailable
- support testing or offline scenarios

#### Role in the system
- improves testability
- allows partial system execution without full backend
- useful for optional features (e.g., cloud services)

## 4. Model-View Pattern / MVVM-like Pattern in QML

### Evidence

The preferences system and the UI rely on:

- `PreferencesModel` classes
- QML views bound to C++ properties through `Q_PROPERTY`
- reactive updates triggered by Qt signals

Example:

```cpp
Q_PROPERTY(QString currentPageId
           READ currentPageId
           WRITE setCurrentPageId
           NOTIFY currentPageIdChanged)
```

### Interpretation

This resembles a Model-View pattern, or an MVVM-like pattern in the context of QML.

In this structure:

- models expose state through properties;
- models notify changes through signals;
- QML views bind declaratively to those properties;
- the UI updates automatically when the underlying state changes.

#### Role in the system

- separate UI representation from application logic;
- enable declarative and reactive UI updates;
- keep the interface maintainable and modular.
- is heavily used in:
  - the Preferences UI;
  - the Project scene UI.

## 5. Strategy Pattern (Playback Policy)

### Evidence

Presence of interchangeable policies:

- PlaybackPolicy
- DefaultPlaybackPolicy

Example:
```
return std::make_unique<DefaultPlaybackPolicy>(...);
```

### Interpretation

This suggests a Strategy pattern, where:

- different playback behaviors are encapsulated in policy classes
- the concrete policy is selected at runtime 

#### Role in the system
- enables flexible playback behavior
- isolates algorithmic variations
- supports extensibility

## 6. Event Filter Pattern (Qt-specific)

#### Evidence

Multiple classes override:
```
bool eventFilter(QObject* obj, QEvent* event)
```

Used in:

- ProjectViewState
- TapHoldShortcut
- UI controllers

### Interpretation

This reflects a Qt Event Filter pattern, where:

- objects intercept and process events before normal handling

#### Role in the system
- handles keyboard shortcuts
- manages global UI interactions
- enables custom input behavior


## Summary

The most relevant candidate patterns identified are:

- Observer Pattern → dominant, used across the system
- Service Pattern (with Dependency Injection) → core architectural pattern
- Model-View (MVVM-like) → used for UI (QML + Models)
- Strategy Pattern → used in playback logic
- Stub Pattern → used for modularity and testing
- Event Filter Pattern → Qt-specific input handling

### Most Significant Patterns

The most architecturally significant patterns are:

- Observer Pattern → drives system reactivity
- Service + Dependency Injection → defines modular architecture
- Model-View (MVVM-like) → structures the UI layer

These patterns together indicate a system designed to be:

- modular
- reactive
- UI-driven
