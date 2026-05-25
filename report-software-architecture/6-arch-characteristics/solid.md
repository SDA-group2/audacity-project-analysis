# SOLID Principles

The SOLID principles make more sense at the **component diagram** level than at the container level.

Let's see if the different components repect that principles.
---

# SOLID in the Desktop App UI

## Single Responsibility Principle

The **Single Responsibility Principle** is quite visible in the way the UI components are divided.

Each component has a fairly precise responsibility.

For example:

```text
Audacity Application Bootstrap
```

is responsible for starting the application, interpreting the run mode, creating the correct app and initializing the rest.

```text
App Shell Module
```

is responsible for the “shell” of the app: windows, dialogs, startup flow, sessions and global actions.

```text
Application Action Controller
```

collects user actions and forwards them to the correct module or service.

```text
Project Scene Module
```

manages the main view when a project is open: tracks, timeline, toolbar, status bar, play cursor and related QML views.

```text
Track Edit Module
```

manages the track editing logic.

```text
UI Components Module
```

contains reusable UI components.

```text
Toast Module
```

manages notifications, messages and user feedback.

This division follows SRP quite well because each component has one main reason to change.

For example:

- if I change the notification system, I should mostly touch `toast`;
- if I change how tracks are edited, I should mostly touch `trackedit`;
- if I change the project view, I should mostly touch `projectscene`.

---

## Dependency Inversion Principle

The **Dependency Inversion Principle** is visible in the fact that the UI should not depend directly on external systems or low-level details.

The correct flow is:

```text
User
  -> App Shell
  -> Application Action Controller
  -> Project Scene / Track Edit / Effects UI
  -> Project / Audio / Plugin / Cloud modules
```

So the UI should not directly talk to:

```text
SQLite
FFmpeg
audio.com
OpenVINO
Whisper.cpp
internals of the old AU3 core
```

Instead, it should delegate work to specific modules.

An important example is:

```text
Au3Wrap Module
```

which acts as an adapter between the new modular frontend and the old AU3 core.

In simple terms:

> The UI does not depend directly on all the technical details of Audacity, but goes through controllers, application modules and adapters.

---

## Interface Segregation Principle

The **Interface Segregation Principle** can be read in the separation of UI responsibilities.

The Desktop App UI is not modeled as one huge component exposing every possible operation. It is divided into smaller components:

```text
App Shell Module
Project Scene Module
Track Edit Module
UI Components Module
Toast Module
```

This prevents every part of the UI from needing to know everything.

For example:

- `Toast Module` does not need to know how track editing works;
- `Track Edit Module` does not need to manage windows, startup flow or sessions;
- `Project Scene Module` does not need to directly handle cloud sync.

So each component exposes only what is needed for its own role, instead of creating one large and confusing interface.

---

## Open/Closed Principle

The **Open/Closed Principle** is less visible in the UI than in the plugin system, but it can still be observed.

For example, new UI components can be added to:

```text
uicomponents
```

without rewriting the entire application shell.

New views, toolbars or project-related controls can be added to:

```text
projectscene
```

while new editing features can mainly evolve inside:

```text
trackedit
```

So the UI is organized in a way that supports local extensions, without modifying one huge central UI block.

---

# SOLID in the Effects and Plugin Engine

## Open/Closed Principle

The **Open/Closed Principle** is probably the most important SOLID principle for the Effects and Plugin Engine.

The system has a common base:

```text
Effects Base Module
```

and then specific modules:

```text
Builtin Effects Module
Nyquist Effects Module
VST Effects Module
LV2 Effects Module
Audio Unit Effects Module
Vamp Effects Module
OpenVINO AI Tools as an optional extension
```

This means that Audacity can support different effect/plugin technologies through dedicated modules.

At architectural level, the idea is:

```text
add a new effect/plugin type
    -> add a specific module/provider
    -> do not rewrite the whole effect system
```

So the system is fairly:

```text
open for extension
closed for modification
```

at least from an architectural point of view.

---

## Single Responsibility Principle

The **Single Responsibility Principle** is also quite visible in the plugin subsystem.

Each module manages a specific family of effects or plugins:

```text
Builtin Effects Module
```

manages Audacity’s native effects.

```text
Nyquist Effects Module
```

manages Nyquist effects and scripts.

```text
VST Effects Module
```

manages VST plugin support.

```text
LV2 Effects Module
```

manages LV2 plugin support.

```text
Audio Unit Effects Module
```

manages Audio Unit support.

```text
Vamp Effects Module
```

manages Vamp plugins, which are more oriented toward audio analysis.

This separation is useful because every plugin format has different requirements: runtime, discovery, compatibility, errors, installation and platform support.

If everything were inside a single component, that component would become huge and hard to maintain.

---

## Dependency Inversion Principle

The **Dependency Inversion Principle** is visible in the relationship between the common effects system and the specific providers.

The rest of Audacity should not know the internal details of:

```text
Nyquist
VST
LV2
Audio Unit
Vamp
```

It should instead reason through a more general concept:

```text
effect/plugin
```

The flow is:

```text
User selects an effect/plugin
  -> Effects UI / Menus
  -> Effects Base Module
  -> specific effect/plugin provider
```

So the rest of the app depends on a more abstract logic, while the details of each technology remain confined inside the specific modules.

---

## Interface Segregation Principle

The **Interface Segregation Principle** is important because plugin formats are very different from each other.

Nyquist, VST, LV2, Audio Unit and Vamp do not all have the same needs. It would not make much sense to force them into one giant interface with methods that some plugins would never use.

For this reason, it is better to have separate modules:

```text
Nyquist Effects Module
VST Effects Module
LV2 Effects Module
Audio Unit Effects Module
Vamp Effects Module
```

In simple terms:

> Each plugin family exposes only what is actually needed for its own type of integration, while the common effects system coordinates them at a higher level.

---

## Liskov Substitution Principle

The **Liskov Substitution Principle** can be discussed at a higher level.

If Audacity treats different effects through the same general abstraction, then each concrete provider should behave consistently with what the system expects from an “effect”.

For example, whether an effect comes from:

```text
Builtin Effects
Nyquist
VST
LV2
Audio Unit
Vamp
```

the rest of the app should still be able to:

```text
discover it
show it to the user
configure it
execute it
apply it to the project/audio
```

Of course, every format has different details, but all of them must respect the general contract expected by the effects system.
