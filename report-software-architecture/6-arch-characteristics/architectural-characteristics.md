## Architectural Characteristics

By taking a look at the `src/` directory, it is pretty clear that Audacity follows a modular monolith architectural style: the application is divided into strict logical boundaries, each being represented by a submodule (e.g. `audio`, `project` etc). These modules are compiled together but remain highly decoupled, making it easy for teams to work on specific features without breaking the rest of the application.
