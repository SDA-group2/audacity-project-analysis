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
- Mapped primary inheritance chains, demonstrating transitive compile-time coupling across architectural layers (e.g., `Track` -> `AudioTrack` -> `WaveTrack`)
- Developed Python scripts to compute header-level coupling metrics (fan-in/fan-out), identifying structural hotspots like `WaveTrack.h`
- Extracted and analyzed inter-library dependencies, mapping 466 unique dependency edges across 78 internal libraries
- Rendered architectural dependency visualizations using Graphviz (`inter-library-graph.svg`)
- Drafted the Structural Dependencies section of the report backed by quantitative evidence

**Outcome:**
- Proved deep compile-time coupling across Audacity's internal modules
- Produced the inter-library dependency graph and metric tables
- Completed the first major analytical dimension (Structural) for the SDA report

---

## Week 3

**Hours spent:** ~14 hours

**Activities:**
- Pivoted the entire analysis pipeline from the static `Audacity-3.7.7` tag to the active `master` branch to strictly meet course requirements and align with the architecture team
- Re-ran the complete static analysis toolchain and regenerated all structural baseline artifacts for the master branch
- Executed Data-Level Dependency analysis using Yourdon & Constantine's coupling taxonomy
- Audited the `gPrefs` global configuration registry, proving widespread Common Coupling across independent subsystems
- Analyzed the `AudacityProject` service locator pattern (`ClientData::Site<T>`), mapping how project-scoped attached objects create centralized dependencies
- Analyzed the `TrackList` shared mutable data model, establishing evidence for Stamp Coupling and Observer-driven propagation
- Mapped SQLite persistence coupling (Schema Coupling) within the AUP3 project architecture (e.g., `ProjectFileIO`, `SqliteSampleBlock`)
- Initiated Behavioral Dependency analysis, focusing on Observer patterns (`Observer::Publisher`) and deferred asynchronous execution (`BasicUI::CallAfter`)

**Outcome:**
- Successfully synchronized the analysis target with the active development branch
- Completed the Data-Level dependencies report section with concrete grep/scripting evidence
- Maintained a clean, incremental Git commit history documenting a highly reproducible research workflow