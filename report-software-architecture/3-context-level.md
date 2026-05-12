## Context Level

### Diagram

TODO: add image

### Actors

According to [this video](https://youtu.be/QYM3TWf_G38?si=HPh6X9NU7opD_eNJ) from Tantacrul, a developer currently in charge of the application's UX/UI design, Audacity user base is split in the following macrocategories: simple audio editors, musicians, audio producers and academic users. In the system's context diagram, I've decided to simplify things a bit, dividing the user base into two main classes: _regular users_, who limit their usage to Audacity's core functionalities, and _academic users_, who may need to make use of some of Audacity's more advanced features, such as the ability to write Nyquist plugins.

### Software Systems

Although being quite complete by itself, Audacity relies on some external programs and services to provide some of its core functionalities.

#### FFmpeg

To allow the user to seamlessly import/export additional file formats, such as M4A and WMA, Audacity interacts with [FFmpeg](https://github.com/FFmpeg/FFmpeg), an open-source suite of libraries and programs for handling multimedia files. Due to patent restrictions, FFmpeg cannot be distributed with Audacity itself and needs to be installed separately by the user.

#### OpenVINO and Whisper

#### Cloud storage support via audio.com

---

After playing a bit with the software, I've noticed that Audacity:

<!-- - has a _notification system_, to notify the user that a new update is available. (Actually this might have been removed in Audacity4, or may have not yet been implemented. Anyway, it was probably built-in even in Audacity3, so it's probably worth removing from the list.) -->

- has _cloud integration_, to save and synchronize projects over multiple devices.
  - this requires to register a new account at [audio.com](https://audio.com/), which will later need to be linked to Audacity.
- stores projects as a `.aup3`/`.aup4` file, a proprietary project file format to store audio recordings, tracks, edits, and effects in a single, unified **SQLite 3 database**.
- (already mentioned, but...) has a plugin manager, to install Nyquist and VST3 plugins.
- supports speech to text translation, via [Whisper](https://github.com/openai/whisper).
- Has FFmpeg integration to import and export a variety of audio formats, including M4A and WMA.
