# MT3 — AudacityProject Shared Context Dependency Analysis

## Purpose

This document analyzes data-level dependencies centered around `AudacityProject` in the active Audacity master branch.

The objective is to identify architectural coupling caused by shared project context access patterns and attached runtime services.

## Architectural Context

The active Audacity master branch preserves a hybrid architecture composed of:

- legacy AU3 subsystems under `au3/`
- newer modularized services under `src/`

Within this architecture, `AudacityProject` acts as a shared project-level context object used across numerous independent subsystems.

The analysis shows that many components depend directly or indirectly on `AudacityProject` for:

- shared runtime state,
- service attachment,
- project-scoped registries,
- effect state access,
- import/export coordination,
- playback coordination,
- UI state,
- and cloud synchronization metadata.

## Evidence of Widespread Structural Reach

The following architectural areas reference `AudacityProject`:

- audio I/O
- playback
- effects
- realtime effects
- import/export
- cloud synchronization
- menus
- snapping
- project history
- project file I/O
- toolbars
- track management
- waveform rendering
- spectrogram visualization
- preferences
- command processing
- UI overlays
- selection management

The dependency spans both:

- `au3/libraries`
- `au3/src`
- and newer `src/` modular services.

## Representative Evidence

### Audio I/O

```cpp
static ProjectAudioIO& Get(AudacityProject& project);
```

### Effects

```cpp
const AudacityProject* EffectBase::FindProject() const;
```

### Import / Export

```cpp
ExportTask Build(AudacityProject& project);
```

### Cloud Synchronization

```cpp
std::weak_ptr<AudacityProject> mWeakProject;
```

### Realtime Effects

```cpp
[](AudacityProject& project) { return &RealtimeEffectList::Get(project); }
```

## ClientData::Site Dependency Model

The analysis also identified extensive use of:

```cpp
ClientData::Site<T>
```

This mechanism is used to dynamically attach additional runtime objects and registries to host entities such as:

- `AudacityProject`
- `Track`
- `WaveClip`
- `ChannelGroup`

Representative evidence:

```cpp
using AttachedProjectObjects = ClientData::Site<
```

This pattern effectively turns `AudacityProject` into a runtime attachment container capable of accumulating heterogeneous subsystem state.

## Dependency Interpretation

The dependency structure around `AudacityProject` represents a combination of:

- common coupling,
- stamp coupling,
- and service-locator-style architectural dependency.

Subsystems become indirectly coupled through shared access to project-scoped attached objects and registries.

The architectural consequences include:

- hidden dependency propagation,
- increased runtime coupling,
- reduced subsystem isolation,
- more difficult dependency tracing,
- and tighter integration between legacy and modularized services.

The presence of `ClientData::Site` further increases architectural complexity because subsystem dependencies may be attached dynamically rather than through explicit compile-time interfaces.

Therefore, the active Audacity master branch still exhibits significant centralized project-context coupling despite ongoing architectural modularization efforts.