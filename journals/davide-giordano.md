# Journal – Davide Giordano

## Week 1

**Hours spent:** ~12 hours

**Activities:**
- Cloned and explored the Audacity repository
- Analyzed the overall project structure (`src/`, `au3/`, modules)
- Identified main areas of interest: UI, audio processing, project management, effects/plugins, cloud integration and legacy bridge
- Started reviewing source files to understand the role of the main modules
- Took notes on potentially relevant modules for dependency, architecture and pattern analysis

**Outcome:**
- Gained an initial understanding of the system architecture
- Identified key areas of interest for dependency and pattern analysis
- Contributed to defining the scope of the analysis, focusing mainly on `src/` and selected legacy AU3-related components

---

## Week 2

**Hours spent:** ~15 hours

**Activities:**
- Continued in-depth code exploration across multiple modules
- Analyzed include relationships to identify code dependencies
- Extracted and processed include data, including most dependent files and most included headers
- Started exploring Git history to identify co-change patterns
- Identified initial candidate design patterns, including Observer, Strategy, Adapter, Command and Builder-like construction
- Discussed findings with the team and refined the analysis approach

**Outcome:**
- Produced initial code dependency analysis
- Produced knowledge dependency data based on co-change relationships
- Contributed to identifying and validating design patterns
- Prepared material used in the Design report

---

## Week 3

**Hours spent:** ~14 hours

**Activities:**
- Designed the first version of the C4 architecture diagrams: Context, Container and Component levels
- Modeled system boundaries, external actors and external dependencies
- Identified the main architectural style as a modular monolith
- Structured the first component diagrams around the Desktop App UI and the Effects/Plugin subsystem
- Started writing the Software Architecture report
- Documented architectural decisions and clarified abstraction levels in the diagrams

**Outcome:**
- Completed the initial Context and Container diagrams
- Defined the high-level structure of the Component diagrams
- Produced the initial version of the Software Architecture report
- Improved understanding of how different subsystems interact within Audacity

---

## Week 4

**Hours spent:** ~13 hours

**Activities:**
- Refactored the architecture diagrams using Structurizr DSL
- Reviewed the C4 abstraction levels to avoid modeling internal modules as containers
- Refined the Container diagram by keeping only deployable/runtime elements such as the Desktop Application and Project File Database
- Revised the Component diagram by grouping related UI elements and integrating notifications/toasts into the UI component
- Added and refined internal component relationships, including:
  - `Application Entry -> UI Elements`
  - `UI Elements -> Timeline Visualization and Editing`
  - `Timeline Visualization and Editing -> Project Core`
  - `Import/Export Module -> FFmpeg`
  - `Effects and Plugins Engine -> OpenVINO`
  - `Cloud Sync -> audio.com`
- Clarified that some component relationships are architectural dependencies and not necessarily direct function calls
- Added relationship technologies/communication mechanisms where appropriate

**Outcome:**
- Produced a cleaner Structurizr-based architecture model
- Clarified the distinction between Container level and Component level
- Improved the accuracy of external system relationships, especially for FFmpeg and OpenVINO
- Reduced ambiguity in the Component diagram

---

## Week 5

**Hours spent:** ~12 hours

**Activities:**
- Wrote and refined the architecture report section under the 2500-word limit
- Added the tooling declaration for Structurizr DSL
- Wrote the Context, Container and Component level explanations
- Added the relationship with the Clean Architecture blueprint at Container level
- Added the SOLID principles discussion at Component level
- Wrote the Architectural Characteristics section, focusing on:
  - modularity
  - maintainability
  - extensibility
  - portability
  - interoperability
  - performance and reliability
  - evolvability
- Removed duplicated or unnecessary explanations from the report

**Outcome:**
- Produced a concise and structured Software Architecture section
- Ensured the report matched the required structure
- Connected the C4 diagrams with architectural reasoning
- Reduced repeated content and improved readability

---

## Week 6

**Hours spent:** ~10 hours

**Activities:**
- Continued the design pattern analysis on the Audacity source code
- Re-evaluated the role of `appfactory.cpp` and interpreted it as a Builder-like / Application Builder pattern rather than a simple Factory
- Identified module-level Facade candidates through `*Module` classes
- Prepared pattern hints for the rest of the group, including:
  - Facade
  - Command
  - Adapter
  - Strategy / Plugin Provider
- Documented one complete pattern instance and provided shorter hints for the remaining ones
- Reviewed how component relationships should be described in the report, avoiding presenting them as direct call graphs

**Outcome:**
- Produced material for the Design Patterns section
- Clarified the interpretation of `AppFactory`
- Helped distribute pattern analysis work across the team
- Improved consistency between the architecture diagrams and the code-level analysis