## Introduction

### Audacity's massive technical debt

For two decades, new features were built as expansions on top of existing code without a cohesive master plan. This led to an architecture where parts of the codebase that should have been separate became utterly entangled, leading to an almost unmaintainable project. This was aggravated by the decentralized, volunteer-based nature of the project, where various contributors added to the code over time without strict architectural oversight.

Another major problem lies in WX Widgets, the framework that was previously used to render the software's UI: not only it made implementing simple UI designs a nightmare, often requiring compromises on basic features like animations, transparency, and shadows, but it also caused inconsistencies across operating systems, where code that worked on macOS might not compile on Windows or look the same on Linux.

Because of this debt, it became virtually impossible to estimate task duration, with one-month projects frequently ballooning into four or five months of work.

### The Solution

The main objective of Muse Group, the company who acquired Audacity, is to solve most of these issues by by re-platforming to the Qt framework, in order to get rid of the old UI based on WX Widgets, while also refactoring the code into a more modular architecture that takes advantage of other components defined in the muse framework.
