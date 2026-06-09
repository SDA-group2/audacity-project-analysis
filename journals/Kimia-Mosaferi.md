# Journal – Kimia Mosaferi

## Week 1

**Hours spent:** ~6 hours

**Activities:**
- Read through the project specification and clarified the scope of the Pattern Analysis section
- Studied the teammates' completed Architecture and Dependencies reports to understand which
  components and coupling hotspots had already been identified
- Reviewed the course material on design patterns (GoF taxonomy, canonical form, pattern
  language) to align the analysis with the expected academic framework
- Cloned the Audacity `master` branch repository locally to have direct access to the source tree

**Outcome:**
- Established a clear understanding of which patterns were likely candidates based on
  the architectural characteristics and dependency hotspots already documented by teammates
- Identified the five most architecturally significant pattern categories to investigate:
  Observer, Command, Strategy, Abstract Factory, and Dependency Injection

---

## Week 2

**Hours spent:** ~10 hours

**Activities:**
- Designed and executed a grep-based static analysis of the full source tree
  (`au3/libraries/`, `au3/src/`, `au3/modules/`, `src/`) to collect evidence for each
  candidate pattern
- Generated evidence files by searching for canonical method names and structural idioms:
  `Publish`, `Subscribe` (Observer); `PushState`, `Undo`, `Redo` (Command);
  `PlaybackPolicy`, `make_unique<...Policy>` (Strategy);
  `PluginProvider`, `DiscoverPluginsAtPath`, `Factory::Call` (Abstract Factory);
  `GlobalInject`, `ContextInject`, `registerExport` (Dependency Injection)
- Produced the following evidence files: `publish_usage.txt`, `subscribe_usage.txt`,
  `undo_usage.txt`, `command_usage.txt`, `factory_usage.txt`, `plugin_usage.txt`,
  `observer_classes.txt`, `execute_usage.txt`, `create_usage.txt`
- Used AI-assisted tooling (Claude) to help interpret the evidence, map GoF roles to
  concrete Audacity classes, and structure the analysis
- Cross-referenced findings against the coupling metrics (`coupling-metrics.txt`) and
  knowledge dependency co-change data produced by the Dependencies team

**Outcome:**
- Confirmed all five candidate patterns with high confidence through source-code evidence
- Produced a structured evidence vault under `analysis/evidence/` and initial pattern
  candidate summaries under `analysis/patterns/`

---

## Week 3

**Hours spent:** ~8 hours

**Activities:**
- Wrote the complete Pattern Analysis section of the Software Design report
- For each of the five patterns, documented:
  - GoF intent and participant roles mapped to specific Audacity classes and file locations
  - Concrete code evidence with exact file paths and line references
  - Architectural rationale (why the pattern is used, which problem it solves)
  - Alternative design approaches with pros and cons
- Connected pattern findings to the Dependency Analysis (structural hotspots, coupling
  metrics) and Architecture report (architectural characteristics such as Modularity,
  Extensibility, Testability)
- Noted cross-pattern interactions (e.g., Observer + Command, Abstract Factory + DI)
- Reviewed the final document for consistency with the course template and word budget

**Outcome:**
- Delivered `patterns.md` — the complete Pattern Analysis section of the Design report
- Identified five patterns: Observer, Command, Strategy, Abstract Factory,
  and Dependency Injection, each with full GoF role mapping, code evidence,
  and alternative analysis
- Section is ready for integration into the team's final Design report
