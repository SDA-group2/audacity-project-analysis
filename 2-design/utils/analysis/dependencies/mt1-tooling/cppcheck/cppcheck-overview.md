# MT1 — Cppcheck Static Analysis Overview

## Purpose

This document summarizes the Cppcheck run executed on the Audacity 3.7.7 compilation database generated during MT1.

The goal of this step is not to treat Cppcheck warnings as final architectural conclusions, but to use them as lightweight static-analysis evidence supporting the dependency-analysis workflow.

## Input

- Target system: Audacity
- Version/tag: Audacity-3.7.7
- Compilation database: `E:\SDA\Audacity-Source\audacity\build-sda\compile_commands.json`
- Translation units checked: 1231 / 1231
- Cppcheck version: 2.20.0

## Command Used

```bat
cppcheck --project=build-sda\compile_commands.json --enable=warning,style,performance,portability --std=c++17 --inline-suppr --suppress=missingIncludeSystem --output-file="E:\SDA\Final project\audacity-project-analysis\analysis\dependencies\mt1-tooling\cppcheck\cppcheck-summary.txt"
```

## Raw Output

The raw Cppcheck output was generated locally as:

```text
analysis\dependencies\mt1-tooling\cppcheck\cppcheck-summary.txt
```

The raw file is intentionally not committed because it is large and noisy:

- Size: 2,458,699 bytes
- Lines: 37,668
- Matched findings: 8,055

## Top Finding Categories

| Count | Cppcheck ID |
|---:|---|
| 2144 | variableScope |
| 690 | noExplicitConstructor |
| 546 | constVariablePointer |
| 544 | missingOverride |
| 367 | unusedStructMember |
| 323 | constParameterPointer |
| 306 | duplInheritedMember |
| 277 | unreadVariable |
| 235 | nullPointerOutOfMemory |
| 227 | uninitMemberVar |
| 211 | cstyleCast |
| 191 | uninitvar |
| 167 | dangerousTypeCast |
| 162 | functionStatic |
| 161 | constVariableReference |
| 132 | ctuOneDefinitionRuleViolation |
| 98 | shadowVariable |
| 93 | knownConditionTrueFalse |
| 83 | useStlAlgorithm |
| 81 | constParameterCallback |

## Interpretation

The Cppcheck results show a large number of style, maintainability, and safety-related findings across the compiled Audacity codebase.

For the dependency-analysis part of the project, the most relevant categories are not individual low-level style warnings, but the findings that point to architectural maintainability risks, such as:

- duplicated inherited members, which may indicate complex inheritance relationships;
- missing overrides, which may make class hierarchy behavior less explicit;
- uninitialized members and variables, which may indicate fragile object lifecycle assumptions;
- cross-translation-unit one-definition-rule findings, which may reveal structural risks across compilation units.

These results will be used as supporting evidence only. The main dependency analysis will still focus on structural, data-level, and behavioral dependencies using the compilation database, source structure, include relationships, and architectural documentation.
