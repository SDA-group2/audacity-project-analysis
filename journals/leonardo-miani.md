## May 1-3rd, 2026

During these few days I have started to take a look at the codebase.

Initially I was trying to separately analyze each directory in-depth, but I soon realized that without having a clear idea of how the project is structured as a whole, I won't be making any significant progress. So in the next few days I'm going to try to understand how the `muse_framework` is integrated in the main project.

## May 5th, 2026

Actually the issue here is that I'm working without a clear plan, so I'm going to take the next few days to improve my understanding of the C4 Model and come up with an outline that I can use as a baseline for the report. Ideally things should become easier once I know what to look for.

## May 11-12, 2026

Started working on the system context diagram + report.

## May 13th, 2026

Finished writing the system context report.

## May 19th, 2026

Finished a first draft of the container diagram.

## May 22-23rd, 2026

Started working on the "Cloud Sync" component diagram.

## May 25th, 2026

Finished the Cloud Sync component diagram. I have also jotted down a draft for the audio one, but I'm debating whether to actually keep it or not. While browsing the code, I've also spotted some design patterns, mainly Builder (`appfactory.cpp`) and Facade (used basically in every submodule in `src/`).

## May 31st, 2026

Migrated the Context and Container diagrams from Draw.io to Structurizr and applied some of the recommendations from the C4 review session.

## June 1-2nd, 2026

Identified some communications mechanisms in the container diagrams (FFmpeg and OpenVINO still missing), added component view to the Structurizr workspace (which is currently still missing some `src/` modules and interactions between components).

## June 3rd, 2026

Started architecture final report review.
