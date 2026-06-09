# MT2 — Compile Database Structural Overview

## Purpose

This document summarizes the top-level structural distribution of Audacity 3.7.7 translation units using the compilation database generated in MT1.

The goal is to establish a reproducible baseline for structural dependency analysis before inspecting inheritance, include fan-in/fan-out, and inter-library dependencies.

## Input

- Target system: Audacity
- Version/tag: Audacity-3.7.7
- Compilation database: `E:\SDA\Audacity-Source\audacity\build-sda\compile_commands.json`
- Total translation units: 1232

## Reproducible Command

The following command was executed from the report repository:

`python -c "import json, pathlib, collections; p=pathlib.Path(r'E:\SDA\Audacity-Source\audacity\build-sda\compile_commands.json'); root=pathlib.Path(r'E:\SDA\Audacity-Source\audacity'); data=json.load(open(p,encoding='utf-8')); c=collections.Counter(); [c.update([pathlib.Path(e['file']).resolve().relative_to(root).parts[0] if pathlib.Path(e['file']).resolve().is_relative_to(root) else 'external']) for e in data]; print('total translation units:', len(data)); print(); [print(f'{k}: {v}') for k,v in c.most_common()]"`

## Results

| Top-level directory | Translation units |
|---|---:|
| `libraries` | 426 |
| `src` | 375 |
| `lib-src` | 316 |
| `modules` | 83 |
| `tests` | 30 |
| `build-sda` | 1 |
| `win` | 1 |

## Interpretation

The compilation database confirms that Audacity's compile-time structure is distributed across several major architectural regions.

The largest group is `libraries`, which indicates that much of the architectural skeleton is implemented in reusable internal libraries rather than only in the application-level `src` directory.

The `src` directory remains highly relevant because it contains application-level integration code. However, the structural dependency analysis cannot focus on `src` alone: it must also inspect `libraries`, especially `lib-track`, `lib-wave-track`, `lib-project`, `lib-effects`, and `lib-audio-io`.

The `lib-src` directory also contributes a large number of translation units. This suggests that third-party or bundled library code is a significant compile-time component of the system, but the main architectural dependency analysis should prioritize Audacity-owned modules first.

This measurement provides the baseline for the next MT2 steps: inheritance tracing, include-level fan-in/fan-out metrics, and inter-library dependency graph extraction.