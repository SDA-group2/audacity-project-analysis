# Knowledge Dependencies

## Scope

We analyzed knowledge dependencies by inspecting the Git commit history and identifying files that were frequently changed together in the same commit.

The analysis focuses on source files under:
- `src/`
- selected legacy components when relevant

The goal is to identify logical or maintenance-related relationships between files, even when these relationships are not always visible through direct code dependencies such as `#include` statements.

---

## Method

Knowledge dependencies were extracted from the Git history by counting how often pairs of files appeared together in the same commit.

For each commit:
- the list of modified files was collected
- repeated files in the same commit were ignored
- pairs of files changed together were counted
- frequently co-changing pairs were ranked by occurrence count

Large commits should be interpreted carefully because they may represent refactoring, renaming, migration, or formatting changes rather than meaningful functional coupling.

---

## Most Frequent Co-change Pairs

| File A | File B | Co-change count | Comment |
|---|---|---:|---|
| `src/TrackPanel.cpp` | `src/TrackPanel.h` | 326 | Expected implementation/header co-change |
| `src/effects/Effect.cpp` | `src/effects/Effect.h` | 237 | Expected pair for the core effect abstraction |
| `src/Project.cpp` | `src/Project.h` | 235 | Expected pair for the central project model |
| `src/Menus.cpp` | `src/Menus.h` | 195 | Expected implementation/header co-change for menu logic |
| `src/AudioIO.cpp` | `src/AudioIO.h` | 194 | Expected pair for audio input/output logic |
| `src/effects/lv2/LV2Effect.cpp` | `src/effects/lv2/LV2Effect.h` | 188 | Expected pair for LV2 effect support |
| `src/effects/VST/VSTEffect.cpp` | `src/effects/VST/VSTEffect.h` | 177 | Expected pair for VST effect support |
| `src/Menus.cpp` | `src/Project.cpp` | 176 | Interesting dependency between menu logic and project state |
| `src/WaveTrack.cpp` | `src/WaveTrack.h` | 146 | Expected pair for core audio track representation |
| `src/effects/audiounits/AudioUnitEffect.cpp` | `src/effects/audiounits/AudioUnitEffect.h` | 142 | Expected pair for Audio Unit effect support |
| `src/effects/VST/VSTEffect.cpp` | `src/effects/ladspa/LadspaEffect.cpp` | 141 | Interesting co-change between different plugin/effect backends |
| `src/effects/ladspa/LadspaEffect.cpp` | `src/effects/ladspa/LadspaEffect.h` | 126 | Expected implementation/header co-change |
| `src/widgets/Ruler.cpp` | `src/widgets/Ruler.h` | 124 | Expected UI component implementation/header co-change |
| `src/effects/VST/VSTEffect.cpp` | `src/effects/audiounits/AudioUnitEffect.cpp` | 121 | Interesting co-change between different effect plugin systems |
| `src/Project.cpp` | `src/TrackPanel.cpp` | 121 | Interesting relationship between project state and track UI |
| `src/commands/CommandManager.cpp` | `src/commands/CommandManager.h` | 120 | Expected pair for command management |
| `src/Track.cpp` | `src/Track.h` | 119 | Expected implementation/header co-change |
| `src/effects/audiounits/AudioUnitEffect.cpp` | `src/effects/ladspa/LadspaEffect.cpp` | 117 | Interesting co-change between plugin backends |
| `src/effects/ladspa/LadspaEffect.cpp` | `src/effects/lv2/LV2Effect.cpp` | 109 | Interesting co-change between plugin backends |
| `src/Menus.cpp` | `src/Project.h` | 106 | Indicates frequent evolution between menu actions and project model |
| `src/effects/nyquist/Nyquist.cpp` | `src/effects/nyquist/Nyquist.h` | 105 | Expected implementation/header co-change |
| `src/effects/Effect.cpp` | `src/effects/nyquist/Nyquist.cpp` | 105 | Interesting relationship between base effect logic and Nyquist effects |
| `src/effects/Effect.cpp` | `src/effects/VST/VSTEffect.cpp` | 103 | Indicates shared evolution between core effects and plugin-specific effects |
| `src/effects/VST/VSTEffect.cpp` | `src/effects/lv2/LV2Effect.cpp` | 103 | Interesting co-change between plugin backends |
| `src/Menus.cpp` | `src/commands/CommandManager.h` | 96 | Suggests menu logic is closely related to command infrastructure |
| `src/Menus.cpp` | `src/TrackPanel.cpp` | 96 | Suggests interaction between menu actions and track panel UI |
| `src/TrackArtist.cpp` | `src/TrackPanel.cpp` | 90 | Suggests strong relation between track rendering and track panel UI |
| `src/effects/Equalization.cpp` | `src/effects/Equalization.h` | 88 | Expected implementation/header co-change |
| `src/ShuttleGui.cpp` | `src/ShuttleGui.h` | 88 | Expected pair for UI construction utility |
| `src/trackedit/internal/au3/au3interaction.cpp` | `src/trackedit/internal/au3/au3interaction.h` | 84 | Expected pair for AU3 track editing interaction |

---

## Initial Observations

- Many of the highest co-change pairs are expected `.cpp` / `.h` pairs. This is normal in C++ projects, where implementation and interface files often evolve together.

- Core entities such as `Project`, `TrackPanel`, `WaveTrack`, `AudioIO`, `Menus`, and `CommandManager` appear frequently in co-change results. This suggests that they are maintenance hotspots and central parts of the system.

- Several co-change pairs connect UI-related files with project or command logic, for example:
  - `Menus.cpp` and `Project.cpp`
  - `Menus.cpp` and `CommandManager.h`
  - `Menus.cpp` and `TrackPanel.cpp`
  - `Project.cpp` and `TrackPanel.cpp`

  This suggests that user interface actions, project state, and editing behavior are historically coupled.

- The effect subsystem shows strong internal knowledge dependencies. Files related to VST, LV2, LADSPA, AudioUnit, Nyquist, and the generic `Effect` abstraction often change together. This indicates that different effect backends share common evolution pressure.

- Some co-change relationships are not simply implementation/header pairs. These are the most interesting for the report because they may reveal hidden architectural coupling.

---

## Relevant Knowledge Dependency Clusters

### 1. Project and UI Interaction Cluster

Relevant pairs:
- `src/Menus.cpp` ↔ `src/Project.cpp`
- `src/Project.cpp` ↔ `src/TrackPanel.cpp`
- `src/Menus.cpp` ↔ `src/TrackPanel.cpp`
- `src/Menus.cpp` ↔ `src/commands/CommandManager.h`

Interpretation:

This cluster suggests that project state, user commands, menus, and track panel behavior often evolve together. This is expected in a desktop audio editor, because many user actions directly affect the current project and its tracks. However, it may also indicate tight coupling between UI actions and application logic.

---

### 2. Effects and Plugin Backends Cluster

Relevant pairs:
- `src/effects/Effect.cpp` ↔ `src/effects/VST/VSTEffect.cpp`
- `src/effects/Effect.cpp` ↔ `src/effects/nyquist/Nyquist.cpp`
- `src/effects/VST/VSTEffect.cpp` ↔ `src/effects/lv2/LV2Effect.cpp`
- `src/effects/VST/VSTEffect.cpp` ↔ `src/effects/audiounits/AudioUnitEffect.cpp`
- `src/effects/audiounits/AudioUnitEffect.cpp` ↔ `src/effects/ladspa/LadspaEffect.cpp`
- `src/effects/ladspa/LadspaEffect.cpp` ↔ `src/effects/lv2/LV2Effect.cpp`

Interpretation:

The effect subsystem shows strong co-change between different plugin technologies. This suggests that changes to effect handling, plugin loading, or effect execution often require coordinated updates across multiple plugin backends.

This is a strong knowledge dependency because the files may belong to different concrete implementations, but they evolve together due to shared abstractions or shared requirements.

---

### 3. Audio Track and Visualization Cluster

Relevant pairs:
- `src/WaveTrack.cpp` ↔ `src/WaveTrack.h`
- `src/TrackPanel.cpp` ↔ `src/TrackPanel.h`
- `src/TrackArtist.cpp` ↔ `src/TrackPanel.cpp`
- `src/Project.cpp` ↔ `src/TrackPanel.cpp`

Interpretation:

These relationships suggest that the representation of audio tracks, their visualization, and their integration into the project UI are closely related. This is expected in an audio editor, where changes to audio data structures often affect rendering and interaction behavior.

---

## Consistency with Code Dependencies

Some knowledge dependencies are consistent with code dependencies. For example:
- `.cpp` / `.h` pairs are naturally consistent with direct code dependencies.
- `Effect.cpp` and `Effect.h` likely represent a direct implementation/interface relationship.
- `Project.cpp` and `Project.h` are expected to change together.

More interesting are the relationships that may not be direct include dependencies but still change together often:
- `Menus.cpp` and `Project.cpp`
- `Project.cpp` and `TrackPanel.cpp`
- `VSTEffect.cpp` and `LV2Effect.cpp`
- `VSTEffect.cpp` and `AudioUnitEffect.cpp`
- `LadspaEffect.cpp` and `LV2Effect.cpp`

These suggest knowledge dependencies that are not necessarily visible from imports alone. They may reflect shared feature changes, common abstractions, or parallel maintenance across similar subsystems.

---

## Summary

The knowledge dependency analysis confirms that Audacity has several central maintenance areas:

1. Project and UI interaction
2. Effects and plugin backends
3. Audio track representation and visualization
4. Command and menu infrastructure

The most interesting result is the strong co-change among different effect/plugin backends. This indicates that while these backends may be implemented as separate modules, they are often maintained together, probably because they implement similar responsibilities under shared architectural constraints.

This finding should be compared with code dependency results to identify whether the architecture reflects these maintenance relationships clearly or whether some dependencies are hidden and only visible through commit history.
