## Introduction

Small introduction regarding the transition from Audacity3.

- Brief description of the previous architectural style
- What were the main problems
- How the new architecture is trying to solve them

### Audacity's massive technical debt

For two decades, new features were built as expansions on top of existing code without a cohesive master plan. This led to an architecture where _parts of the codebase that should have been separate became utterly entangled_, leading to an almost unmaintainable project. This was aggravated by the decentralized, volunteer-based nature of the project, where various contributors added to the code over time without strict architectural oversight.

Another major problem lies in _WX Widgets_, the framework that was previously used to render the software's UI: not only it made implementing simple UI designs a nightmare, often requiring compromises on basic features like animations, transparency, and shadows, but it also caused inconsistencies across operating systems, where code that worked on macOS might not compile on Windows or look the same on Linux.

Because of this debt, it became virtually impossible to estimate task duration, with one-month projects frequently ballooning into four or five months of work.
## Tooling Declaration
## Context Level

### Diagram

TODO: add image

### Actors

According to [this video](https://youtu.be/QYM3TWf_G38?si=HPh6X9NU7opD_eNJ) from Tantacrul, a developer currently in charge of the application's UX/UI design, Audacity user base is split in the following macrocategories: simple audio editors, musicians, audio producers and academic users. In the system's context diagram, I've decided to simplify things a bit, dividing the user base into two main classes: _regular users_, who limit their usage to Audacity's core functionalities, and _academic users_, who may need to make use of some of Audacity's more advanced features, such as the ability to write Nyquist plugins.

### Software Systems

Although being quite complete by itself, Audacity relies on some external programs and services to provide some of its core functionalities.

#### FFmpeg

To allow the user to seamlessly import/export additional file formats, such as M4A and WMA, Audacity interacts with [FFmpeg](https://github.com/FFmpeg/FFmpeg), an open-source suite of libraries and programs for handling multimedia files. Due to patent restrictions, FFmpeg cannot be distributed with Audacity itself and needs to be installed separately by the user.

#### Cloud integration via audio.com

The ability to save project files in the cloud has been a feature since Audacity 3.5, released on 22/04/2024.

It is centered around [audio.com](https://audio.com/), a free audio hosting platform. It provides _background syncing_ (every time the project is saved locally, Audacity automatically syncs the latest changes in background, ensuring the online version remains up to date) and _version control and recovery_, allowing the user to revert the project to an earlier version.

Projects stored in the cloud can be directly opened from Audacity.

#### OpenVINO Plugins

On top of an already existing plugin ecosystem based on `libnyquist`, since version 3.7.4 Audacity has started implementing a set of AI-based plugins via [OpenVINO](https://github.com/openvinotoolkit/openvino). This expansion allows the system to delegate complex tasks, such as noise suppression, music separation, and automated transcription, to an external inference engine. All these models run locally on the user's hardware, ensuring privacy and eliminating the need for an internet connection.

To implement the automated transcription features, Audacity relies on [Whisper.cpp](https://github.com/ggml-org/whisper.cpp), a high-performance C++ port of OpenAI's [Whisper](https://github.com/openai/whisper) model.
## Container Level

## Relationship with the Clean Architecture blueprint
## Component Level
## Architectural Characteristics

By taking a look at the `src/` directory, it is pretty clear that Audacity follows a modular monolith architectural style: the application is divided into strict logical boundaries, each being represented by a submodule (e.g. `audio`, `project` etc). These modules are compiled together but remain highly decoupled, making it easy for teams to work on specific features without breaking the rest of the application.

---

## 1. Modularity

The most evident characteristic is **modularity**.

Audacity does not appear as a single indistinct block, but as a codebase divided into functional modules. Each module covers a specific part of the application: `projectscene` manages the project view, `trackedit` handles track editing, `effects` manages the effects/plugin system, `toast` handles notifications, `au3cloud` manages cloud synchronization, and so on.

This modularity does not turn Audacity into a distributed system, but it makes the monolith more organized and easier to control.

In simple terms:

> Audacity remains a single desktop application, but internally it tries to behave like a set of separate and coordinated modules.

---

## 2. Maintainability

The new organization improves **maintainability**, because it reduces the risk of every part of the system depending directly on every other part.

For example:

- changes to the track view should mainly remain inside `projectscene` and `trackedit`;
- changes to effects/plugins should mainly remain inside `effects`;
- changes to notifications should remain inside `toast`;
- changes related to cloud features should remain inside `au3cloud`.

This makes it easier to understand where to make a change and reduces the risk that a local modification breaks distant parts of the application.

The technical debt does not disappear completely: the presence of `au3wrap` shows that Audacity still has to coexist with legacy parts of the old core. However, the important point is that this debt is progressively encapsulated instead of remaining spread across the whole codebase.

---

## 3. Modifiability

**Modifiability** describes how easy it is to change or extend the system.

In Audacity, the division into modules helps because new features can be added in specific areas without changing the entire application.

For example:

- new UI components can be added inside `uicomponents` or `projectscene`;
- new editing features can be added inside `trackedit`;
- new built-in effects can be added inside `builtin_collection`;
- new plugin formats can be handled through dedicated modules/adapters;
- new cloud integrations can be isolated inside `au3cloud`.

The most interesting case is the effects/plugin subsystem: separating `effects_base` from concrete modules such as `nyquist`, `vst`, `lv2`, `audio_unit`, and `vamp` allows Audacity to manage different plugin formats through a common base.

In practice:

> If Audacity needs to support a new type of plugin, it should not be necessary to rewrite the whole application: it should be enough to add a new module connected to the effects system.

---

## 4. Extensibility

Audacity has historically been a highly extensible application, especially because of its plugin support.

This characteristic is clearly visible in the **Effects and Plugin Engine**, which includes several types of effects and plugins:

```text
Builtin Effects
Nyquist
VST
LV2
Audio Unit
Vamp
OpenVINO AI Tools as an optional extension
```

Extensibility allows Audacity to support additional functionality without having to include everything directly inside the application core.

However, this choice has a cost: the more plugin formats are supported, the more the system has to manage discovery, registration, compatibility, errors, external dependencies, and differences between operating systems.

For this reason, it is useful to have a central component such as:

```text
Effects Base Module
```

which acts as a common point between the UI, registry/scanning logic, and the specific modules for each plugin family.

---

## 5. Portability

Audacity is a cross-platform desktop application, so **portability** is a fundamental characteristic.

The application must run on different operating systems while keeping its behavior as consistent as possible. This affects both the UI and the audio/plugin layer.

The transition toward Qt/QML is important in this direction: the goal is to have a more modern UI that is more consistent and easier to maintain across platforms.

Portability also affects the plugin system:

- Audio Unit is mainly tied to the Apple/macOS ecosystem;
- VST and LV2 have different availability and behavior depending on the platform;
- the audio layer has to interact with different operating system audio stacks;
- some external dependencies may be installed or available differently depending on the platform.

Therefore, portability is a central quality attribute, but also one of the main sources of complexity.

---

## 6. Interoperability

Audacity has to interact with many external systems, formats, and runtimes.

These include:

- several audio file formats;
- FFmpeg for formats that are not directly supported;
- external plugins;
- audio.com for cloud synchronization;
- OpenVINO AI Tools as an optional extension;
- third-party runtimes and libraries;
- legacy AU3 code.

To prevent these external details from contaminating the whole system, it is important to model clear boundaries and adapters.

Examples:

```text
Effects and Plugin Engine -> plugin formats
Import/Export -> FFmpeg
Cloud Sync -> audio.com
Au3Wrap -> AU3 legacy core
```

In this way, external integrations are isolated behind specific components.

---

## 7. Testability

**Testability** seems to be supported by the new modular structure.

The codebase contains test directories in several modules, for example:

```text
src/appshell/tests
src/projectscene/tests
src/trackedit/tests
src/effects/effects_base/tests
src/effects/builtin_collection/tests
```

This is a positive sign: if modules have clearer responsibilities, it becomes easier to test them separately.

The presence of interfaces, controllers, and separated modules also helps create more focused tests, without having to start the whole application just to verify a single piece of logic.

Informally:

> The more the code is divided into pieces with clear responsibilities, the easier it becomes to test those pieces without dragging the whole of Audacity with them.

---

## 8. Usability

**Usability** is central because Audacity is a highly interactive application.

Users spend most of their time inside the project scene, working with tracks, timeline, toolbars, menus, effects, and editing operations. For this reason, the architecture must support a clear, responsive, and consistent UI.

Modules such as:

```text
appshell
projectscene
uicomponents
toast
```

are important not only from a visual point of view, but also from an architectural point of view.

Usability is not just about having a good-looking interface. It also means:

- clear feedback to the user;
- consistent actions;
- well-organized menus and toolbars;
- synchronized application state;
- proper handling of errors and long-running operations;
- separation between UI and application logic.

The `toast` module, for example, shows attention toward user notifications and feedback.

---

## 9. Performance

**Performance** is fundamental because Audacity works with audio, tracks, effects, and plugins.

There are two main types of performance to consider:

1. UI performance;
2. audio processing performance.

The UI must remain responsive even with large projects, many tracks, or complex operations. At the same time, effects and plugins must be able to process audio efficiently.

This separation is important: the UI should not directly execute heavy operations, but should send requests to dedicated subsystems.

For example:

```text
Desktop App UI -> Effects and Plugin Engine
Requests effect/plugin execution
```

This makes it easier to handle long-running operations, errors, status updates, and feedback to the user.

---

## 10. Reliability

**Reliability** describes the ability of the system to work correctly even in problematic situations.

For Audacity, this is very important because users work on audio projects that must not be corrupted or lost.

The most delicate areas are:

- project loading and saving;
- audio recording;
- import/export;
- execution of external plugins;
- cloud synchronization;
- handling unsupported formats;
- errors or crashes during long-running operations.

Separating modules such as `project`, `audio`, `effects`, and `au3cloud` helps contain problems. Ideally, an external plugin failure should not compromise the whole UI or corrupt the open project.

---

## 11. Evolvability

**Evolvability** is probably one of the most important characteristics for understanding Audacity's new architecture.

The starting problem was a historically large codebase, with a lot of technical debt and strongly intertwined parts. The new organization seems to move toward a gradual migration strategy:

- a new UI based on Qt/QML;
- more separated modules;
- wrappers around the old AU3 core;
- more isolated subsystems;
- support for new integrations such as cloud features and AI plugins.

The `au3wrap` module is especially significant: it shows that Audacity is not removing the old core all at once, but is gradually encapsulating it.

In simple terms:

> Audacity is not throwing away the old system in one step; it is building a more organized layer above and around the legacy core.

---

## 12. Deployability

Audacity's **deployability** is different from that of a web or distributed system.

Audacity is distributed as an installable desktop application, so many modules are compiled and released together as part of the same product.

However, there are also optional or separately installable components:

- FFmpeg can be installed separately;
- external plugins can be added by the user;
- OpenVINO AI Tools can be distributed as an optional bundle;
- some features depend on the operating system.

Therefore, Audacity can be described as:

> A desktop modular monolith with optional external dependencies and plugin bundles.

---

## 13. Security and Privacy

**Security** is not the main focus of the component diagram, but it is still important.

There are at least three aspects to consider.

The first one concerns external plugins: Audacity can load code, scripts, or modules developed by third parties. This creates an important trust boundary.

The second one concerns cloud synchronization: when a project is synchronized with audio.com, some user data leaves the local context.

The third one concerns local AI tools such as OpenVINO: if the processing happens locally, the audio does not necessarily need to be sent to remote services, which is an advantage from a privacy perspective.

In summary:

> Audacity has to balance extensibility and trust boundaries, especially when loading external plugins or synchronizing data to the cloud.

---

## Final Summary

| Characteristic | Why it matters in Audacity |
|---|---|
| **Modularity** | The codebase is divided into internal modules instead of being a single indistinct block. |
| **Maintainability** | Boundaries between UI, project, audio, effects, and cloud help reduce technical debt. |
| **Modifiability** | New features can be added inside specific modules. |
| **Extensibility** | The system supports multiple types of effects and plugins. |
| **Portability** | The application must run on multiple operating systems. |
| **Interoperability** | It must integrate with FFmpeg, external plugins, cloud services, AI runtimes, and legacy AU3 code. |
| **Testability** | Separated modules and interfaces make focused testing easier. |
| **Usability** | The modular UI supports a more modern and consistent user experience. |
| **Performance** | Audio editing and plugins require efficient processing and a responsive UI. |
| **Reliability** | Projects, audio, and plugins must be handled without corrupting data or blocking the application. |
| **Evolvability** | The structure enables a gradual migration from the old AU3 core. |
| **Deployability** | It is a modular monolithic desktop app, with optional external extensions. |
| **Security/Privacy** | External plugins, cloud sync, and local AI introduce trust boundaries that must be managed. |
# Relationship with Clean Architecture

Audacity does not follow Clean Architecture in a perfect or “textbook” way. It is not a project that was designed from scratch with those layers already cleanly separated.

However, by looking at the new modular structure, some ideas are quite close to Clean Architecture.

The general idea is this:

```text
UI / Presentation
    -> application logic / controllers
        -> domain-specific modules
            -> infrastructure / external systems / legacy code
```

So Audacity is not a pure Clean Architecture system, but it can be read as a **modular monolith that tries to better separate UI, application logic, infrastructure and legacy code**.

---

## Reading it at container level

At container level, the main parts of the system can be read like this:

| Clean Architecture Layer              | Audacity Elements                                                                                |
|---------------------------------------|--------------------------------------------------------------------------------------------------|
| **Presentation / UI**                 | Audacity Desktop Application                                                                     |
| **Application Layer**                 | action controller, editing orchestration, playback/recording requests, effect execution requests |
| **Domain / Core Logic**               | project model, track editing, audio operations, effect/plugin concept                            |
| **Interface Adapters**                | Au3Wrap, plugin adapters, import/export adapters, cloud wrappers                                 |
| **Infrastructure / External Systems** | Project File Database, FFmpeg, audio.com, OpenVINO AI Tools, Whisper.cpp, plugin runtimes        |

---

## Audacity Desktop Application

The **Audacity Desktop Application** maps quite well to the **Presentation** layer.

It is the part the user directly sees and uses: windows, menus, toolbars, project scene, dialogs, notifications and UI components.

From a Clean Architecture perspective, this part should not contain all the real logic of the application. It should mainly:

```text
collect user input
show the application state
forward requests to the correct modules
```

For example, the UI should not directly execute a plugin or directly manipulate low-level audio data. It should ask the proper module to do it.

---

## Audio, Playback and Recording Engine

The **Audio, Playback and Recording Engine** can be seen as part of the **application/domain logic**.

It manages playback, recording and audio operations. So it is much closer to Audacity’s core behavior than the UI.

In practice, the UI should ask for operations such as:

```text
play
record
stop
apply audio operation
```

without knowing all the technical details of the underlying audio stack.

---

## Effects and Plugin Engine

The **Effects and Plugin Engine** is a very interesting part because it sits somewhere between **application/domain logic** and the **adapter layer**.

On one hand, it manages concepts that are central to Audacity:

```text
effects
plugins
audio transformations
audio analysis
```

On the other hand, it has to communicate with very different technologies:

```text
Builtin Effects
Nyquist
VST
LV2
Audio Unit
Vamp
OpenVINO AI Tools as an optional extension
```

From a Clean Architecture perspective, this separation is useful because the rest of the application should not know the details of every plugin format.

The application should reason in general terms:

```text
I need to execute an effect
```

then the effects/plugin subsystem decides whether that effect is built-in, Nyquist, VST, LV2, Audio Unit, Vamp or something else.

---

## Project File Database

The **Project File Database** clearly belongs to the **Infrastructure / Data Layer**.

It is used to locally save Audacity projects, for example `.aup3` files.

Since it uses SQLite, it is a technological detail. In a Clean Architecture reading, the rest of the system should not depend too directly on SQLite.

Ideally, the system should talk to a project/persistence module, while the SQLite detail remains isolated.

---

## Cloud Sync and audio.com

The **Cloud Sync** part and the external system **audio.com** belong to the **Infrastructure / External Services** layer.

Cloud synchronization is not part of the core audio editing logic. It is an external feature that should remain separated from both the UI and the audio/project logic.

This separation is useful because the cloud side can change independently from the rest of the application.

---

## FFmpeg, OpenVINO and Whisper.cpp

Systems such as:

```text
FFmpeg
OpenVINO AI Tools
Whisper.cpp
```

are external dependencies.

In Clean Architecture terms, they belong to the outer layers, because they are technological details used by the application, but they should not define the internal structure of the core.

For example:

- FFmpeg is used for some import/export formats;
- OpenVINO AI Tools can be seen as an optional external bundle;
- Whisper.cpp can be used by local AI transcription tools.

These dependencies should stay behind clear adapters or boundaries.

---

## Au3Wrap and legacy code

`au3wrap` is one of the most important pieces to mention.

It shows that Audacity is not removing the old AU3 core all at once. Instead, it is trying to encapsulate it behind a wrapper/adapter layer.

From a Clean Architecture perspective, `au3wrap` can be read as an **interface adapter**.

The new modular frontend should not directly depend on all the details of the old core. `au3wrap` is exactly the bridge:

```text
new modular frontend
    -> Au3Wrap
        -> old AU3 core
```

This is also important because it shows a gradual migration: Audacity is not rewriting everything from scratch, but is building a cleaner new layer above and around the old system.

---

## Dependency direction

The most important point, in relation to Clean Architecture, is the direction of dependencies.

The ideal flow should be:

```text
UI
  -> controller / action layer
    -> application or domain modules
      -> adapters / infrastructure
```

and not:

```text
UI
  -> SQLite / FFmpeg / plugin runtime / legacy core directly
```

For this reason, in the diagram, it is better not to say that the Desktop App UI “executes plugins” or “does audio processing”.

It is better to say:

```text
Desktop App UI
  -> requests an operation
    -> the dedicated module executes it
```

Examples:

```text
Desktop App UI
  -> Effects and Plugin Engine
      -> specific plugin provider
```

or:

```text
Desktop App UI
  -> Audio, Playback and Recording Engine
      -> audio operation
```

---

## Limits compared to pure Clean Architecture

Audacity should not be described as a perfect example of Clean Architecture.

The main reasons are:

1. it is a large historical codebase;
2. it was not designed from scratch with Clean Architecture;
3. the presence of `au3wrap` shows that a lot of legacy code still exists;
4. some boundaries are likely still part of an ongoing migration.

So I would not say:

> Audacity implements Clean Architecture.

I would rather say:

> Audacity does not strictly implement Clean Architecture, but its new modular organization follows similar principles.

In other words:

> Audacity does not strictly implement Clean Architecture, but the new modular organization follows similar ideas: separation of the UI, more isolated application modules, external dependencies kept at the edges, and legacy code encapsulated through adapters.

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
