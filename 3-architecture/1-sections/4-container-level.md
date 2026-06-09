## Container Level

![Container Diagram.](figures/ContainerView.svg)

### The main containers

By taking a look at the project structure in the `src/` directory, it is pretty clear that Audacity is implemented as a **modular monolith**, where the application is deployed as a single desktop application and is internally divided into logical modules, each contributing a separate responsibility.

The core of the main desktop application is developed in C++, while the user interface layer is built using Qt and QML. This is where the main application modules are contained, such as the audio editing logic, the plugin/effect system, the cloud integration module and so on.

As shown in the diagram, the main desktop application interacts with the file system to store projects using Audacity's proprietary `.aup3` and `.aup4` formats, both of which are built on top of SQLite.

### What about other containers?

While Audacity also relies on other software programs, such as `libnyquist`, for giving the users a way to write custom plugins, and the `muse_framework`, which plays a central role in Audacity's new refactored architecture, we haven't decided to consider them as separate containers. As Simon Brown also says,

> "frameworks are usually something that you build your software on top of, while libraries are things that your software uses. In most cases, these are really just technology choices that components make use of, and are therefore implementation details rather than components in their own right."

Indeed, this is what we're seeing here. `libnyquist`, for example, is neatly integrated inside the `effects` module to give the users a way to extend the application to their likings.

### Relationship with the Clean Architecture blueprint

Audacity should not be described as a strict or textbook implementation of Clean Architecture. It is a large historical desktop application, and part of its current structure still depends on legacy AU3 code and on technical constraints accumulated over time.

However, the newer modular organization can be interpreted through some Clean Architecture principles. At container level, Audacity is best understood as a **modular monolith**: it is deployed as a single desktop application, but internally it separates user interaction, application coordination, domain-specific modules, adapters and infrastructure-related concerns.

A simplified reading is the following:

```text
UI / Presentation
    -> application actions and controllers
        -> domain-specific modules
            -> adapters, infrastructure, external systems and legacy code
```

In this interpretation, the **Audacity Desktop Application** contains the presentation and application-facing parts of the system. The user interacts with menus, toolbars, dialogs and the project scene, but these UI elements should mainly collect input and delegate operations rather than directly implementing all the audio-processing or persistence logic.

The **Audio Engine**, **Project Core** and **Effects and Plugins Engine** are closer to the application/domain side. They represent the parts of the system that coordinate playback, recording, project state, editing operations and the execution of effects. These are central to Audacity's behavior and should remain more stable than the external technologies used to support them.

External systems and technical dependencies belong to the outer layers. For example, the **Project File Database** is based on SQLite-backed `.aup3`/`.aup4` project files, **FFmpeg** supports import/export of additional audio formats, **audio.com** supports cloud-related features, and **OpenVINO** or **Whisper.cpp** can provide optional AI-related functionality. From a Clean Architecture perspective, these technologies should be treated as implementation details and accessed through dedicated modules or adapters.

The **Legacy Bridge** is particularly important in this reading. The `au3wrap` layer shows that Audacity is not replacing the old AU3 core all at once; instead, it encapsulates legacy functionality behind a boundary that can be used by the newer modular code. This is close to the role of an interface adapter: it allows the newer parts of the application to communicate with legacy code without exposing every internal detail of the old implementation.

Therefore, the main Clean Architecture relationship visible in the container diagram is not a perfect circular layered model, but the intended **direction of dependency and responsibility**:

```text
User interface
  -> application coordination
    -> core audio/project/effect modules
      -> infrastructure, plugin runtimes, file formats, cloud services and legacy code
```

This also affects how the container relationships should be read. For example, the Desktop Application does not mean that every UI class directly accesses SQLite, FFmpeg or plugin runtimes. Rather, the deployable desktop application uses those technologies through internal components such as Project Core, Import/Export, Effects and Plugins, Cloud Sync and the Legacy Bridge.

For this reason, Audacity can be described as a system that **does not implement Clean Architecture completely**, but whose ongoing modular refactoring follows similar goals: separating presentation from core behavior, isolating external dependencies, and wrapping legacy code behind clearer architectural boundaries.
