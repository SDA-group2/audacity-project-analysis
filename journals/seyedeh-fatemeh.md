# Journal – Seyedeh Fatemeh

## Week 1

**Hours spent:** ~12 hours

**Activities:**
- Established the dedicated Git workflow and created the `feature/sahar-dependencies-analysis` branch
- Cloned the Audacity repository and explored the modular `libraries/` vs `src/` architectural layout
- Configured the local static analysis environment and toolchain
- Generated the compilation database (`compile_commands.json`) using CMake
- Deployed and verified analysis tools including Cppcheck, Include-What-You-Use (IWYU), Doxygen, and Graphviz
- Initialized the report documentation structure and established the `analysis/` evidence vault

**Outcome:**
- Created a fully reproducible static-analysis pipeline
- Indexed 1232 translation units to form the compile-time structural baseline
- Secured the foundational infrastructure required for the dependency analysis report

---

## Week 2

**Hours spent:** ~15 hours

**Activities:**
- Focused on extracting and analyzing Audacity's Structural Dependencies
- Mapped primary inheritance chains, demonstrating transitive compile-time coupling across architectural layers, such as `Track -> AudioTrack -> WaveTrack`
- Developed Python scripts to compute header-level coupling metrics, including fan-in and fan-out
- Identified structural hotspots such as `WaveTrack.h`, `Project.h`, `Prefs.h`, and `AudioIO.h`
- Extracted and analyzed inter-library dependencies, mapping 466 unique dependency edges across 78 internal libraries
- Rendered architectural dependency visualizations using Graphviz, including `inter-library-graph.svg`
- Drafted the Structural Dependencies section of the report backed by quantitative evidence

**Outcome:**
- Proved deep compile-time coupling across Audacity's internal modules
- Produced the inter-library dependency graph and metric tables
- Completed the first major analytical dimension: Structural Dependencies

---

## Week 3

**Hours spent:** ~14 hours

**Activities:**
- Pivoted the entire analysis pipeline from the static `Audacity-3.7.7` tag to the active `master` branch to meet the active-codebase requirement
- Re-ran the static analysis toolchain and regenerated structural baseline artifacts for the master branch
- Executed the Data-Level Dependency analysis using the dependency taxonomy introduced in the Software Design and Architecture course
- Audited shared configuration and preference mechanisms, identifying global configuration coupling across independent subsystems
- Analyzed the `AudacityProject` project context and project-scoped attached objects as centralized shared-state dependency points
- Analyzed the `TrackList` shared mutable data model, identifying data-level coupling across editing, playback, effect processing, and persistence
- Mapped persistence coupling in the AUP3/SQLite-based project architecture, including project file I/O and shared storage representation
- Initiated behavioral dependency analysis by inspecting Observer patterns and deferred asynchronous execution mechanisms such as `Observer::Publisher` and `BasicUI::CallAfter`

**Outcome:**
- Successfully synchronized the analysis target with the active development branch
- Completed the Data-Level Dependencies section with concrete source-code evidence
- Maintained a clean, incremental Git commit history documenting a reproducible research workflow

---

## Week 4

**Hours spent:** ~10 hours

**Activities:**
- Completed Micro-Task 4: Behavioral and Synchronization Dependency Analysis
- Collected source-code evidence for AudioIO and PortAudio stream lifecycle behavior
- Mapped real-time audio execution dependencies, including playback/recording startup, stream lifecycle order, and callback execution
- Extracted synchronization evidence involving mutexes, atomics, waits, and coordination mechanisms
- Analyzed Observer-based propagation through publisher/subscriber mechanisms
- Analyzed deferred UI execution through event queues and mechanisms such as `BasicUI::CallAfter`
- Investigated initialization-order dependencies around project management, registries, modules, plugins, and startup logic
- Created MT4 evidence files under `analysis/dependencies/mt4-behavioral/`
- Updated the main Dependencies report with the final Behavioral and Synchronization Dependencies section
- Generated and shared the master-branch source-file list with a teammate for alignment with the Overview report

**Outcome:**
- Completed the third required dependency dimension: Behavioral and Synchronization Dependencies
- Produced source-code evidence for runtime coupling, including audio callbacks, synchronization primitives, observer propagation, deferred UI execution, and initialization-order assumptions
- Completed the Dependencies section across all three required dimensions:
  1. Structural Dependencies
  2. Data-Level Dependencies
  3. Behavioral and Synchronization Dependencies
- Pushed the final MT4 commit to the branch `feature/sahar-dependencies-analysis`