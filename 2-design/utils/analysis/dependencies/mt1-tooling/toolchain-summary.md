# MT1 — Static Analysis Toolchain Setup

## Target System

- System: Audacity
- Version/tag: Audacity-3.7.7
- Source location: `E:\SDA\Audacity-Source\audacity`
- Git commit: `5ef610ed2`
- Build directory: `build-sda`

## Toolchain

| Tool | Version / Status |
|---|---|
| MSVC C/C++ compiler | 19.44.35227 for x64 |
| CMake | 4.3.2 |
| Ninja | 1.13.2 |
| Python | 3.12.3 |
| Cppcheck | 2.20.0 |
| Doxygen | 1.17.0 |
| Graphviz dot | 14.1.5 |

## CMake Configuration Command

```bat
cmake -S . -B build-sda -G Ninja -DCMAKE_BUILD_TYPE=RelWithDebInfo -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DAUDACITY_BUILD_LEVEL=2
```

## Result

CMake configuration completed successfully.

Generated file:

```text
E:\SDA\Audacity-Source\audacity\build-sda\compile_commands.json
```

Evidence:

```text
compile_commands.json size: 7,382,294 bytes
translation unit entries: 1232
first file: E:/SDA/Audacity-Source/audacity/lib-src/libvamp/src/vamp-hostsdk/PluginBufferingAdapter.cpp
```

## Academic Relevance

This step establishes the evidence base for the dependency analysis. The generated compilation database will be used to inspect structural dependencies, especially include-level and translation-unit-level coupling across Audacity's `src/`, `libraries/`, `modules/`, and `lib-src/` directories.