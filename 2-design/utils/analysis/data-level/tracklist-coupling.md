# MT3 — TrackList Shared Data Model Coupling

## Purpose

This document analyzes data-level dependencies centered around `TrackList` in the active Audacity master branch.

The objective is to identify architectural coupling caused by shared mutable track structures and project-wide track registries.

## Architectural Context

The active Audacity master branch stores project track state inside `TrackList`.

The analysis shows that `TrackList` acts as a centralized shared data model used across many independent subsystems.

The dependency crosses:

- audio processing,
- effects,
- cloud synchronization,
- project persistence,
- import/export,
- snapping,
- track editing,
- label management,
- and waveform processing.

## Core Shared-State Mechanism

`TrackList` is globally retrievable from `AudacityProject`:

```cpp
TrackList& TrackList::Get(AudacityProject& project)
{
    return project.AttachedObjects::Get< TrackList >(key);
}
```

The runtime attachment mechanism is initialized through:

```cpp
static const AudacityProject::AttachedObjects::RegisteredFactory key{
    [](AudacityProject& project) { return TrackList::Create(&project); }
};
```

This architecture effectively turns `TrackList` into a project-wide shared mutable registry.

## Representative Dependency Evidence

### Built-in Effects

```cpp
auto range = TrackList::Get(p).Selected<const WaveTrack>();
```

### Cloud Synchronization

```cpp
VisitBlocks(TrackList::Get(project));
```

### Import / Export

```cpp
const auto& tracks = TrackList::Get(project);
```

### Project Persistence

```cpp
auto& trackList = TrackList::Get(mProject);
```

### Snapping

```cpp
SnapManager(const AudacityProject& project, const TrackList& tracks, ...)
```

## Shared Mutable Structures

The analysis also identified extensive use of:

```cpp
std::shared_ptr<Track>
std::shared_ptr<TrackList>
TrackList&
```

across subsystem boundaries.

Representative examples include:

```cpp
std::shared_ptr<TrackList> mTracks{};
```

```cpp
TrackList& outputs
```

```cpp
TrackList::Create(&project)
```

## Event Propagation Coupling

The dependency structure also includes observer-based propagation through:

```cpp
TrackListEvent
```

Representative evidence:

```cpp
[this](const TrackListEvent& event)
```

```cpp
case TrackListEvent::ADDITION:
case TrackListEvent::DELETION:
case TrackListEvent::PERMUTED:
```

This means modifications to shared track state propagate indirectly to subscribers throughout the system.

## Dependency Interpretation

The dependency structure around `TrackList` represents a combination of:

- stamp coupling,
- shared mutable data coupling,
- and observer-driven dependency propagation.

Multiple architectural subsystems exchange and manipulate complex shared structures rather than isolated data values.

The architectural consequences include:

- increased runtime coupling,
- hidden side effects,
- indirect dependency propagation,
- more difficult state tracing,
- and reduced subsystem isolation.

The use of observer notifications (`TrackListEvent`) further increases dependency complexity because state changes may trigger cascaded reactions across unrelated architectural modules.

Therefore, the active Audacity master branch preserves a highly centralized shared track-state architecture despite ongoing modularization efforts.