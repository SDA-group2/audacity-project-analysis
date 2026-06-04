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

