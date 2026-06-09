# Audio Management Component

`src/` modules:

- `au3audio`
- `audio`
- (possibly) `record`

## au3audio

### Audio Devices Provider

- `src/audio/audiodevicesprovider.h/cpp`: exposing methods such as `handleDeviceChange()`, `currentInputDevice()`, `setInputDevice()` this module is responsible for handling audio from a hardware standpoint

It's interesting to note that this class is the concrete implementation of the interface in `src/audio/iaudiodevicesprovider.h`.

### Audio Engine

- `src/au3audio/internal/au3audioengine.h/cpp`: contains methods such as `start/stop/pauseStream`, `set/getPlaybackVolume`...

Similarly to the audio devices provider component, `au3audioengine` is also the concrete implementation of `src/audio/iaudioengine.h`.

### Playback Policy

- `defaultplaybackpolicy.cpp/h`
- `au3-audio-io/PlaybackSchedule.h`
