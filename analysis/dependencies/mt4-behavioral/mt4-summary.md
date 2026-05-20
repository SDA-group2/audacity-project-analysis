# MT4 Behavioral and Synchronization Dependency Evidence

## Evidence files

| File | Purpose |
|---|---|
| `audio-stream-evidence.txt` | Evidence for AudioIO, PortAudio stream lifecycle, and real-time callback behavior |
| `synchronization-evidence.txt` | Evidence for mutexes, atomics, waits, and synchronization primitives |
| `observer-evidence.txt` | Evidence for Observer::Publisher, Publish, and Subscribe behavior |
| `ui-event-evidence.txt` | Evidence for BasicUI::CallAfter, wxWidgets event queue, and deferred UI execution |
| `initialization-evidence.txt` | Evidence for ProjectManager, registries, module/plugin initialization, and startup ordering |

## Main findings

| ID | Dependency surface | Evidence target | Dependency type | Architectural meaning |
|---|---|---|---|---|
| B1 | Real-time audio engine | AudioIO / PortAudio stream lifecycle | Behavioral + timing | Playback and recording depend on ordered stream setup and callback execution |
| B2 | Audio synchronization | mutex / atomic / wait primitives | Synchronization | Shared audio state must be coordinated across runtime paths |
| B3 | Observer propagation | Observer::Publisher / Publish / Subscribe | Behavioral | State changes trigger indirect downstream behavior |
| B4 | Deferred UI execution | BasicUI::CallAfter / wx events | Behavioral + temporal | Execution is scheduled later on the UI/event thread |
| B5 | Initialization order | ProjectManager / registries / managers | Behavioral | Subsystems assume correct startup order |