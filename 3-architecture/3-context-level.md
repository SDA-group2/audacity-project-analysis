## Context Level

### Diagram

![System Context Diagram.](./figures/ContextView.svg)

### Actors

According to [this video](https://youtu.be/QYM3TWf_G38?si=HPh6X9NU7opD_eNJ) from Tantacrul, a developer currently in charge of the application's UX/UI design, Audacity user base is split in the following macrocategories: simple audio editors, musicians, audio producers and academic users. In the system's context diagram, We've decided to simplify things a bit, dividing the user base into two main classes: _regular users_, who limit their usage to Audacity's core functionalities, and _academic users_, who may need to make use of some of Audacity's more advanced features, such as the ability to write Nyquist plugins.

### Software Systems

Although being quite complete by itself, Audacity relies on some external programs and services to provide some of its core functionalities.

#### FFmpeg

To allow the user to seamlessly import/export additional file formats, such as M4A and WMA, Audacity interacts with [FFmpeg](https://github.com/FFmpeg/FFmpeg), an open-source suite of libraries and programs for handling multimedia files. Due to patent restrictions, FFmpeg cannot be distributed with Audacity itself and needs to be installed separately by the user.

#### Cloud integration via audio.com

The ability to save project files in the cloud has been a feature since Audacity 3.5, released on 22/04/2024.

It is centered around [audio.com](https://audio.com/), a free audio hosting platform. It provides _background syncing_ (every time the project is saved locally, Audacity automatically syncs the latest changes in background, ensuring the online version remains up to date) and _version control and recovery_, allowing the user to revert the project to an earlier version. To take advantage of these feature, the user needs to register an account on `audio.com`.

Projects stored in the cloud can be directly opened from Audacity.

#### OpenVINO Plugins

On top of an already existing plugin ecosystem based on `libnyquist`, since version 3.7.4 Audacity has started implementing a set of AI-based plugins via [OpenVINO](https://github.com/openvinotoolkit/openvino). This expansion allows the system to delegate complex tasks, such as noise suppression, music separation, and automated transcription, to an external inference engine. All these models run locally on the user's hardware, ensuring privacy and eliminating the need for an internet connection.

To implement the automated transcription features, Audacity relies on [Whisper.cpp](https://github.com/ggml-org/whisper.cpp), a high-performance C++ port of OpenAI's [Whisper](https://github.com/openai/whisper) model.
