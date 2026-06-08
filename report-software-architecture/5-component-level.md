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

The use of the OCP is particularly evident in the `effects` component, especially in the way Audacity handles different effect technologies.

At high-level, the application provides an effect loader in `effects_base/ieffectloader.h`, which defines what the system needs to know about a plugin family. Then the `EffectsProvider` (defined in `effects_base/internal/effectsprovider.cpp`) can load a new family of effects by simply asking for the correct loader and calling it polymorphically, as show in the following snippet. This represents the "closed" part of the principle, as these two classes never need to change, even when new technologies are added.

```cpp
bool EffectsProvider::loadEffect(const EffectId& effectId) const
{
    const IEffectLoaderPtr loader = this->loader(effectId);
    if (!loader) { return false; }
    return loader->ensurePluginIsLoaded(effectId);
}
```

The "open" part can be seen in the ways the actual effect technologies are implemented: each plugin family simply needs to define a custom `EffectLoader`, which is then registered into `IEffectLoadersRegister` (below is an example for `libnyquist`).

```cpp
m_effectLoader = std::make_shared<NyquistEffectsLoader>();
auto loadersRegister = globalIoc()->resolve<IEffectLoadersRegister>(moduleName());
if (loadersRegister) {
    loadersRegister->registerLoader(m_effectLoader);
}
```

#### Liskov Substitution Principle (LSP)

#### Interface Segregation Principle (ISP)

The `trackedit` component inside the `src/` directory shows both a violation and an in-progress solution of the ISP.

`src/trackedit/itrackeditinteraction.h` is a ~150 line long, "fat" interface that takes charge of at least four unrelated responsibilities:

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
