## Container Level

![Container Diagram.](./figures/ContainerView.svg)

### The main containers

By taking a look at the project structure in the `src/` directory, it is pretty clear that Audacity is implemented as a **modular monolith**, where the application is deployed as a single desktop application and is internally divided into logical modules, each contributing a separate responsibility.

The core of the main desktop application is developed in C++, while the user interface layer is built using Qt and QML. This is where the main application modules are contained, such as the audio editing logic, the plugin/effect system, the cloud integration module and so on.

As shown in the diagram, the main desktop application interacts with the file system to store projects using Audacity's proprietary `.aup3` and `.aup4` formats, both of which are built on SQLite.

### What about other containers?

While Audacity also relies on other software programs, such as `libnyquist`, for giving the users a way to write custom plugins, and the `muse_framework`, which plays a central role in Audacity's new refactored architecture, we haven't decided to consider them as separate containers. As Simon Brown also says,

> "frameworks are usually something that you build your software on top of, while libraries are things that your software uses. In most cases, these are really just technology choices that components make use of, and are therefore implementation details rather than components in their own right."

<!-- Indeed, this can also be seen -->

### Relationship with the Clean Architecture blueprint
