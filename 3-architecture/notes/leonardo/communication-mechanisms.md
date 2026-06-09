The function calls responsible for exporting/importing project files into Audacity are declared in `src/au3wrap/internal/au3project.h` and defined `src/au3wrap/internal/au3project.cpp`.

`/au3/modules/import-export/mod-ffmpeg/`: library that handles FFmpeg integration.

Question: apparently `project/internal/audaciytproject.cpp` is responsible for saving files in the file system. Then what's the responsibility of `importexport`?

_Timeline Visualization and Editing_:

- `trackedit`: for example, `trackeditinteraction.cpp/.h` defines a set of methods for timeline editing.
- `spectrogram`

_Audio Recording_: `record`: module that handles audio recording.
