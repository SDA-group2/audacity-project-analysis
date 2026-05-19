from pathlib import Path
import re
from collections import defaultdict, Counter

SRC_ROOT = Path(r"E:\SDA\Audacity-Source\audacity")
LIB_ROOT = SRC_ROOT / "libraries"

OUT_DIR = Path(r"analysis\dependencies\mt2-structural")
TXT_OUT = OUT_DIR / "inter-library-deps.txt"
DOT_OUT = OUT_DIR / "inter-library-deps.dot"

EXTENSIONS = {".h", ".hpp", ".cpp", ".cc", ".cxx"}
HEADER_EXTENSIONS = {".h", ".hpp"}

include_re = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]')

libs = sorted(
    p for p in LIB_ROOT.iterdir()
    if p.is_dir() and p.name.startswith("lib-")
)

lib_names = {p.name for p in libs}

# Map header basename -> owning lib-* directories
header_to_libs = defaultdict(set)

for lib in libs:
    for path in lib.rglob("*"):
        if path.is_file() and path.suffix in HEADER_EXTENSIONS:
            header_to_libs[path.name].add(lib.name)

# edges[(source_lib, target_lib)] = include count
edges = Counter()
evidence = defaultdict(list)

for lib in libs:
    source_lib = lib.name

    for path in lib.rglob("*"):
        if not path.is_file() or path.suffix not in EXTENSIONS:
            continue

        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        for line_no, line in enumerate(lines, 1):
            m = include_re.match(line)
            if not m:
                continue

            include_path = m.group(1)
            included_name = Path(include_path).name

            target_libs = set()

            # Case 1: include by header basename, e.g. #include "WaveTrack.h"
            target_libs.update(header_to_libs.get(included_name, set()))

            # Case 2: include path contains lib-* directory name
            normalized = include_path.replace("\\", "/")
            for part in normalized.split("/"):
                if part in lib_names:
                    target_libs.add(part)

            for target_lib in target_libs:
                if target_lib == source_lib:
                    continue

                edge = (source_lib, target_lib)
                edges[edge] += 1

                if len(evidence[edge]) < 5:
                    rel = str(path.relative_to(SRC_ROOT)).replace("\\", "/")
                    evidence[edge].append(
                        f"{rel}:{line_no}: #include {include_path}"
                    )

OUT_DIR.mkdir(parents=True, exist_ok=True)

with TXT_OUT.open("w", encoding="utf-8") as f:
    f.write("MT2 - Inter-library Structural Dependencies\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Audacity source root: {SRC_ROOT}\n")
    f.write(f"Library directories scanned: {len(libs)}\n")
    f.write(f"Unique inter-library dependency edges: {len(edges)}\n\n")

    f.write("DEPENDENCY EDGES BY SOURCE LIBRARY\n")
    f.write("-" * 80 + "\n")

    by_source = defaultdict(list)
    for (src, dst), count in edges.items():
        by_source[src].append((dst, count))

    for src in sorted(by_source):
        f.write(f"\n{src}\n")
        for dst, count in sorted(by_source[src], key=lambda x: (-x[1], x[0])):
            f.write(f"  -> {dst}  [include_count={count}]\n")

    f.write("\n\nTOP 30 INTER-LIBRARY EDGES BY INCLUDE COUNT\n")
    f.write("-" * 80 + "\n")
    f.write(f"{'Source':<35} {'Target':<35} {'Count':>6}\n")
    f.write(f"{'-'*35} {'-'*35} {'-'*6}\n")

    for (src, dst), count in edges.most_common(30):
        f.write(f"{src:<35} {dst:<35} {count:>6}\n")

    f.write("\n\nEVIDENCE SAMPLES\n")
    f.write("-" * 80 + "\n")

    for (src, dst), count in edges.most_common(30):
        f.write(f"\n{src} -> {dst}  [include_count={count}]\n")
        for row in evidence[(src, dst)]:
            f.write(f"  {row}\n")

with DOT_OUT.open("w", encoding="utf-8") as f:
    f.write("digraph InterLibraryDeps {\n")
    f.write("  rankdir=LR;\n")
    f.write('  node [shape=box, style="rounded"];\n')

    for (src, dst), count in edges.most_common():
        src_label = src.replace("lib-", "")
        dst_label = dst.replace("lib-", "")
        f.write(f'  "{src_label}" -> "{dst_label}" [label="{count}"];\n')

    f.write("}\n")

print(f"Wrote: {TXT_OUT}")
print(f"Wrote: {DOT_OUT}")
print(f"Library directories scanned: {len(libs)}")
print(f"Unique inter-library dependency edges: {len(edges)}")
print("Top 10 edges:")
for (src, dst), count in edges.most_common(10):
    print(f"{src} -> {dst} | count={count}")