## Introduction

### Audacity's massive technical debt

For two decades, new features were built as expansions on top of existing code without a cohesive master plan. This led to an architecture where _parts of the codebase that should have been separate became utterly entangled_, leading to an almost unmaintainable project. This was aggravated by the decentralized, volunteer-based nature of the project, where various contributors added to the code over time without strict architectural oversight.

Another major problem lies in _WX Widgets_, the framework that was previously used to render the software's UI: not only it made implementing simple UI designs a nightmare, often requiring compromises on basic features like animations, transparency, and shadows, but it also caused inconsistencies across operating systems, where code that worked on macOS might not compile on Windows or look the same on Linux.

Because of this debt, it became virtually impossible to estimate task duration, with one-month projects frequently ballooning into four or five months of work.

<!-- TODO: add a few lines on how the new architecture is planning to solve these problems. -->
