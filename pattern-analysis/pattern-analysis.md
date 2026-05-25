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
