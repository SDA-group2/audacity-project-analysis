# Code Dependencies

## Scope
We analyzed include relationships in:
- `src/`
- `au3/src/`
- `au3/libraries/`
- `au3/modules/`

We excluded third-party code, documentation, images, and build scripts.

---

## Most Dependent Files

| File | Number of includes | Comment |
|---|---:|---|
| au3/src/AudacityApp.cpp | 98 | Main application entry point, likely orchestrates multiple subsystems |
| au3/modules/nyquist/mod-nyq-bench/NyqBench.cpp | 71 | Benchmark/testing module, depends on many components |
| src/projectscene/projectscenemodule.cpp | 65 | Core module in new architecture, likely coordinates project-related features |
| src/effects/builtin_collection/internal/builtincollectionloader.cpp | 58 | Handles loading of built-in effects, interacts with multiple subsystems |
| src/app/appfactory.cpp | 56 | Factory responsible for creating application components |
| au3/src/ProjectFileManager.cpp | 55 | Manages project files, central to persistence logic |
| au3/src/effects/EffectUI.cpp | 51 | UI component for effects, connects UI and processing logic |
| au3/src/FreqWindow.cpp | 50 | UI component, likely tied to audio visualization |
| au3/src/TimerRecordDialog.cpp | 47 | UI dialog with dependencies on recording logic |
| au3/src/BatchProcessDialog.cpp | 46 | Batch processing interface, integrates multiple functionalities |

---

## Most Included Headers

| Header | Number of references | Comment |
|---|---:|---|
| <memory> | 237 | Widely used standard library for memory management |
| <vector> | 206 | Core container used throughout the system |
| <algorithm> | 154 | Standard algorithms, common utility usage |
| "ShuttleGui.h" | 154 | UI-related component, indicates strong UI presence |
| "modularity/ioc.h" | 129 | Dependency injection / modularity system |
| <wx/defs.h> | 125 | wxWidgets UI framework |
| <functional> | 123 | Functional programming utilities |
| "framework/global/modularity/ioc.h" | 118 | Extended modularity/IoC framework |
| "Project.h" | 115 | Core domain object representing projects |
| "context/iglobalcontext.h" | 103 | Global context management |
| "Prefs.h" | 99 | Application preferences/configuration |
| <string> | 96 | Standard string usage |
| <optional> | 96 | Optional values handling |
| <wx/log.h> | 95 | Logging via UI framework |
| <QObject> | 93 | Qt-related component (mixed frameworks) |
| "wxPanelWrapper.h" | 93 | UI abstraction layer |
| "WaveTrack.h" | 88 | Core audio data structure |
| "log.h" | 83 | Logging utilities |
| "ViewInfo.h" | 82 | UI/view-related information |
| "ProjectHistory.h" | 78 | Project state/history management |
| "Observer.h" | 53 | Suggests observer pattern usage |
| "au3-utility/Observer.h" | 48 | Alternative observer implementation |

---

## Initial Observations

- Files with a very high number of includes (e.g., `AudacityApp.cpp`, `appfactory.cpp`) appear to act as **orchestrators**, coordinating multiple subsystems such as UI, audio processing, and project management.

- Core domain concepts such as `Project`, `WaveTrack`, and `Prefs` are among the most frequently included headers, indicating their **central role across the system**.

- The presence of `modularity/ioc.h` and related headers suggests the use of a **dependency injection / inversion of control mechanism**, supporting a modular architecture.

- A strong presence of UI-related headers (`ShuttleGui.h`, wxWidgets components) indicates **tight coupling between UI and application logic** in several parts of the system.

- The coexistence of different frameworks (e.g., wxWidgets and Qt elements like `QObject`) suggests **heterogeneity in the codebase**, possibly due to legacy evolution.

- The presence of `Observer.h` and similar headers suggests **potential use of the Observer pattern**, which should be further validated in the pattern analysis phase.

- Several highly dependent files are located under `au3/`, indicating that **legacy components still play a significant role** in the system and may be tightly integrated with newer modules under `src/`.
