## Architectural Characteristics

To summarize, the architecture of Audacity is designed to balance the needs of two primary stakeholders: the end-users and the open-source developers. The major refactoring that's currently being carried out is aimed at improving the overall experience for both parties.

### User-Oriented Characteristics

From a user standpoint, Audacity should appear as a fast, reliable and extensible audio editor, that does not sacrifice on its looks.

The architecture maintains its _performance_ by keeping the core audio engines in highly optimized, native C++ components. Cloud support via `audio.clom` has been added to provide a higher degree of _reliability_, by allowing users to save their projects online, as well as locally on their personal machine. The ability to write `nyquist` plugins allows more experienced users to _extend_ the application to their liking and, finally, the UX/UI experience has been greatly improved thanks to the Qt re-platform.

### Developer-Oriented Characteristics

One of the main objectives of the new architecture is to simplify the development experience. The modular structure improves _maintainability_ because changes can remain localized to a specific component, and _extendability_, since modules can be developed independently and later loaded independently at startup. This aspect has also been greatly improved by the adoption of the `muse_framework`, which provides abstractions that can be used to further decouple components.

_Portability_ has also been greatly improved, thanks to the re-platform to Qt: now developers can rest assured that a UI component will look and work the same on every operating system.
