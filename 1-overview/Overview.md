# Overview

**System:** Audacity, version 4.0 development line (`master` branch)
**Course:** Software Design and Architecture, PoliTo 2025/2026


## 1. Purpose of the System

Audacity is a free, open source, cross platform digital audio editor and recorder. It lets users record live audio, import and export a wide range of formats, and edit and process multitrack projects through standard cut, copy, and paste editing, a large set of built in effects, and support for external plugin formats. The project has been developed since 1999 and, since 2021, is maintained and funded by Muse Group.

This analysis targets the 4.0 development line on the `master` branch. Version 4.0 is not an incremental release: it is a substantial re architecture of the long lived 3.x codebase, replacing the previous wxWidgets interface with a new Qt and QML frontend while keeping the existing audio engine and editing core during a gradual migration. This makes 4.0 the interesting case to analyze, because its design and architecture choices are explicitly about managing the transition away from a heavily entangled legacy system.

## 2. Main Stakeholders

The architecture is shaped by four main groups of stakeholders.

**End users.** Following the categorization used in the project's own UX material, the user base groups into regular users, who use core recording and editing features, and academic or advanced users, who rely on more specialized capabilities such as spectral analysis and writing Nyquist plugins. Both groups need a responsive interface, project files that are not corrupted or lost, and consistent behavior across Windows, macOS, and Linux.

**Muse Group.** As the owner and funder of the project since 2021, Muse Group is the primary institutional stakeholder. It drives the roadmap, including the move to the shared Qt and QML framework also used by MuseScore, and decisions on cloud integration and telemetry.

**Contributors and maintainers.** Audacity is developed in the open by a large community alongside the Muse Group team. They depend on a codebase that can be understood and changed module by module, which is what the new modular structure aims to provide.

**Third party integrators.** Independent developers and external services connect through stable boundaries: plugin authors targeting the supported effect formats, the FFmpeg project for additional file formats, and the audio.com platform for cloud features.

## 3. System Description

Audacity 4.0 is structured as a modular monolith. It is distributed and runs as a single desktop application, but internally the code is divided into modules with defined responsibilities that are compiled together while remaining loosely coupled.

At the top level the codebase is organized into three parts: `au3/`, the legacy Audacity 3 engine and editing core that is being refactored; `src/`, the new Audacity 4 frontend; and `muse/`, the shared application framework (also used by MuseScore) that the refactored version builds on. The `muse/` framework is treated here as the underlying framework rather than as analyzed application code.

The new `src/` directory is organized into modules such as `app`/`appshell` (startup and shell), `projectscene`, `trackedit`, and `uicomponents` (the Qt and QML UI), `effects` (plugins and effects), `project`, `playback`, `record`, `au3cloud` (cloud sync), and `toast` (notifications). The legacy core under `au3/` is organized into the `au3-*` internal libraries (`au3/libraries`), the legacy application code (`au3/src`), and the legacy plugin modules (`au3/modules`). The `au3wrap` module adapts the new frontend to the legacy core, which is how the project encapsulates its technical debt rather than rewriting everything at once.

Internally the application uses a dependency injection container from the Muse framework to wire services to consumers, keeping modules substitutable and testable. Externally it integrates with FFmpeg for extra import and export formats, audio.com for optional cloud sync (since 3.5), and, since 3.7.4, OpenVINO and Whisper.cpp for locally run AI features such as noise suppression and transcription. The effect engine supports several plugin families: built in effects, Nyquist, VST, LV2, LADSPA, Audio Unit, and Vamp. The system is written predominantly in C++, with QML for the new user interface.

## 4. Code Statistics

The analysis covers the compiled `master` tree: the new `src/` frontend together with the legacy core under `au3/libraries`, `au3/src`, and `au3/modules`. No files were selected manually; the scope is the set of translation units the build compiles, which the CMake compilation database used in the dependency analysis resolves to **1,232 translation units**. The `muse/` framework is excluded as an underlying dependency. Measured directly across the same source tree, the scope is summarized below (SLOC counts non blank, non comment lines).

| Area | Source files | SLOC | Physical lines |
|---|---:|---:|---:|
| `au3/src` (legacy application) | 379 | 107,085 | 146,272 |
| `au3/libraries` (legacy `au3-*` libraries) | 442 | 89,969 | 125,464 |
| `src/` (new 4.0 frontend) | 532 | 80,590 | 105,642 |
| `au3/modules` (legacy plugin modules) | 123 | 19,683 | 27,273 |
| **Total** | **1,476** | **297,327** | **404,651** |

The 1,232 figure comes from the dependency analysis's compile database, generated on the Audacity 3.7.7 release tag, which also counts bundled lib-src third-party sources; the 1,476 count here is measured on the master tree with third-party code excluded, so the two are not directly comparable.

In terms of modules and packages, the system contains more than 110 internal modules: around 22 top level modules in the new `src/` frontend, 77 `au3-*` libraries under `au3/libraries`, and 17 legacy plugin modules under `au3/modules`.

The project records more than 380 contributors in its Git history, which begins in 2010 (the project itself dates to 1999). Development is highly active, with several hundred commits merged per month through GitHub pull requests, confirming the system is under continuous development.

A note on scope: the assignment guideline of roughly 100,000 lines refers to a single focused component. The analyzed scope here is larger because studying the 4.0 transition requires spanning both the new frontend and the legacy core it wraps. Taken on its own, the new Audacity 4 code in `src/` is about 80,000 lines, close to that guideline; the legacy `au3/` core is included because the new frontend still depends on and refactors it. The detailed dependency and pattern analysis concentrates on the most architecturally significant areas: the new `src/` frontend modules and the core `au3-*` libraries such as track, audio I/O, project, and effects.