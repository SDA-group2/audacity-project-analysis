## Component Level

### SOLID Principles

#### Single Responsibility Principle (SRP)

The SRP can be seen being used around the whole application. At the component level, by inspecting the `src/` directory it is clear that each component only contributes towards a specific feature (e.g. the `au3cloud/` module only handles user authentication and project cloud sync, while `effects/` takes care of the effects and plugins support).

```txt
./src/
├── app
├── au3audio
├── au3cloud
├── ...
├── effects
└── uicomponents
```

If we zoom one level further, we can see that this principle is also applied at the code level: in the `au3cloud/internal` directory, for example, we can see that almost each class/interface pair is responsible for only one subtask inside the "cloud" domain (e.g. `cloudurlhandler.cpp/h` handles cloud-application interactions, such as opening a project stored in the cloud directly into Audacity given a specific URI, and `au3cloudservice.cpp/h` handles user authentication with `audio.com`, including sign-in and sign-out operations).

#### Open-Closed Principle (OCP)

<!-- The use of the OCP is particularly evident in the effects and plugins engine, particularly in the way the different effect/plugins technologies are handled. -->
<!---->
<!-- The core effects engine, `effects_base`, defines abstract interfaces that define how plugins are loaded and managed, without having actual knowledge of the actual formats. -->

#### Liskov Substitution Principle (LSP)

#### Interface Segregation Principle (ISP)

The `trackedit` component inside the `src/` directory shows both a violation and an in-progress solution of the ISP.

`src/trackedit/itrackeditinteraction.h` is a ~150 line long, "fat" interface that bundles at least four unrelated client roles:

| Responsibility    | Methods                                           |
| ----------------- | ------------------------------------------------- |
| Clip manipulation | `changeClipStartTime`, `trimClipsLeft`, ...       |
| Track management  | `newMonoTrack`, `deleteTracks`, `moveTracks`, ... |
| Undo/redo history | `undo`, `redo`, ...                               |
| Clipboard         | `pasteFromClipboard`, `clearClipboard`, ...       |

A comment in the same file denotes that the developers are already aware of this issue

```cpp
//! NOTE Interface for interacting with the project
//! When it gets big, maybe we’ll divide it into several
```

Indeed, this interface is currently being split into multiple segregated replacements, such as `iclipsinteraction.h`, `itracksinteraction.h` and so on.

#### Dependency Inversion Principle (DIP)

The codebase heavily utilizes the DIP throughout the `src/` directory. Taking the `au3audiocomservice.cpp` class inside the `au3cloud` component as an example (although it should be noted that many other choices were possible), we can see that interactions with the filesystem do not depend directly on low-level utilities modules, such as the operating system's filesystem APIs, but rather use a `filesystem` object, which is an instance of the higher-level `IFileSystem` interface, as see in the following line taken from the related header file.

```cpp
muse::GlobalInject<muse::io::IFileSystem> filesystem;
```
