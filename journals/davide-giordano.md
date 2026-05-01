# Journal – Davide Giordano

## Week 1

**Hours spent:** ~12 hours

**Activities:**
- Cloned and explored the Audacity repository
- Analyzed the overall project structure (`src/`, `au3/`, modules)
- Identified main components (UI, audio processing, project management)
- Started reviewing source files to understand core functionality
- Took notes on potentially relevant modules for further analysis

**Outcome:**
- Gained an initial understanding of the system architecture
- Identified key areas of interest for dependency and pattern analysis
- Contributed to defining the scope of the analysis (focus on `src/` and selected legacy components)

---

## Week 2

**Hours spent:** ~15 hours

**Activities:**
- Continued in-depth code exploration across multiple modules
- Analyzed include relationships to identify code dependencies
- Extracted and processed include data (most dependent files, most included headers)
- Started exploring Git history to identify co-change patterns
- Identified candidate design patterns (Observer, Service/DI, Strategy, MVVM-like)
- Discussed findings with the team and refined analysis approach

**Outcome:**
- Produced initial code dependency analysis
- Produced knowledge dependency data (co-change relationships)
- Contributed to identifying and validating design patterns
- Prepared material used in the Design report

## Week 3

**Hours spent**: ~14 hours

**Activities**:

- Designed the C4 architecture diagrams (Context, Container, Component)
- Modeled system boundaries, external actors, and dependencies
- Identified and structured main containers (UI Layer, Core Layer, Audio Engine, Project Management, etc.)
- Refined relationships between internal modules and external systems (file system, plugins, hardware, cloud services)
- Started writing the Software Architecture report
- Documented architectural decisions and clarified abstraction levels in diagrams

**Outcome**:

- Completed Context and Container diagrams
- Defined the high-level structure of the Component diagrams
- Produced the initial version of the Software Architecture report
- Improved understanding of how different subsystems interact within Audacity