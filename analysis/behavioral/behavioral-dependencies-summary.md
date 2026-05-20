# MT4 Behavioral and Synchronization Dependency Summary

## Matches by dependency category

| Category | Matches |
|---|---:|
| callbacks_events | 1012 |
| state_transitions | 410 |
| audio_stream_control | 172 |
| blocking_or_waiting | 35 |
| synchronization | 12 |
| threading | 5 |

## Matches by component

| Component | Matches |
|---|---:|
| Other | 1113 |
| Effects | 287 |
| GUI/UI | 246 |

## Component x category matrix

| Component | audio_stream_control | blocking_or_waiting | callbacks_events | state_transitions | synchronization | threading |
|---|---:|---:|---:|---:|---:|---:|
| Effects | 15 | 7 | 222 | 43 | 0 | 0 |
| GUI/UI | 29 | 7 | 134 | 72 | 2 | 2 |
| Other | 128 | 21 | 656 | 295 | 10 | 3 |

## Interpretation guide

- `audio_stream_control` indicates behavioral dependencies around playback, recording, and PortAudio stream lifecycle.
- `callbacks_events` indicates callback/event-driven dependencies, especially GUI event dispatch and deferred execution.
- `synchronization` and `blocking_or_waiting` indicate synchronization dependencies, where one execution path may wait for another.
- `state_transitions` indicates sequential ordering assumptions such as start/stop/pause/commit/flush operations.
