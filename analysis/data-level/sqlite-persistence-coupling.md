# MT3 — SQLite Persistence and SampleBlock Coupling

## Purpose

This document analyzes data-level dependencies caused by the SQLite-based persistence architecture used in the active Audacity master branch.

The objective is to identify architectural coupling introduced through shared database schemas, centralized persistence services, and shared audio block storage structures.

## Architectural Context

The active Audacity master branch persists project state using SQLite-based AUP3 storage.

The persistence architecture is centered around:

- `ProjectFileIO`
- `DBConnection`
- `SqliteSampleBlock`
- `SampleBlock`
- and SQLite schema definitions.

The analysis shows that many independent subsystems depend on the same persistence schema and shared database structures.

## Shared Persistence Structures

The following database tables were identified:

```sql
CREATE TABLE IF NOT EXISTS <schema>.project
CREATE TABLE IF NOT EXISTS <schema>.autosave
CREATE TABLE IF NOT EXISTS <schema>.sampleblocks
```

Additional cloud synchronization persistence tables include:

```sql
CREATE TABLE IF NOT EXISTS projects
CREATE TABLE IF NOT EXISTS block_hashes
CREATE TABLE IF NOT EXISTS pending_snapshots
CREATE TABLE IF NOT EXISTS pending_project_blobs
CREATE TABLE IF NOT EXISTS pending_project_blocks
CREATE TABLE IF NOT EXISTS project_users
```

These tables are shared across multiple architectural modules.

## SampleBlock Shared Dependency

The analysis identified widespread subsystem dependencies on:

```cpp
SampleBlock
SqliteSampleBlock
SampleBlockIDSet
SampleBlockHashes
```

Representative evidence:

### Cloud Synchronization

```cpp
#include "au3-wave-track/SampleBlock.h"
```

### Snapshot Upload

```cpp
task.Block.Block = sampleBlockFactory->CreateFromId(
```

### Remote Snapshot Storage

```sql
INSERT INTO sampleblocks (...)
```

### Block Hashing

```cpp
VisitBlocks(TrackList::Get(project));
```

## ProjectFileIO Centralized Persistence Gateway

The persistence architecture is coordinated through:

```cpp
ProjectFileIO::Get(AudacityProject& project)
```

Representative evidence:

```cpp
auto& result = project.AttachedObjects::Get< ProjectFileIO >(sFileIOKey);
```

This mechanism attaches persistence services directly to project-scoped runtime state.

The dependency spans:

- project loading,
- autosave,
- cloud synchronization,
- waveform persistence,
- track restoration,
- and snapshot migration.

## Schema Version Coupling

The analysis identified centralized schema evolution management through:

```cpp
ProjectFormatVersion
PRAGMA user_version
```

Representative evidence:

```cpp
// ProjectFormatVersion / PRAGMA user_version tracks the SQLite database schema
```

This means multiple architectural modules implicitly depend on synchronized schema compatibility.

## Dependency Interpretation

The persistence architecture represents a combination of:

- schema coupling,
- shared database coupling,
- persistence-layer coupling,
- and centralized storage dependency.

Independent architectural modules exchange information indirectly through shared persistence structures rather than isolated service contracts.

The architectural consequences include:

- hidden persistence dependencies,
- schema migration sensitivity,
- runtime compatibility constraints,
- centralized storage coupling,
- and reduced subsystem independence.

The use of shared `sampleblocks` storage further increases coupling because waveform persistence, synchronization, hashing, autosave, and cloud upload logic all depend on the same underlying persistence schema.

Therefore, the active Audacity master branch preserves a highly centralized persistence architecture despite ongoing modularization efforts.