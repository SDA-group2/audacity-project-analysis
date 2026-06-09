from pathlib import Path
import re
from collections import defaultdict

SRC_ROOT = Path(r"E:\SDA\Audacity-Source\audacity")
OUT = Path(r"analysis\dependencies\mt2-structural\coupling-metrics.txt")

SCAN_DIRS = [
    SRC_ROOT / "src",
    SRC_ROOT / "libraries",
]

EXTENSIONS = {".cpp", ".h", ".cxx", ".cc", ".hpp"}
HEADER_EXTS = {".h", ".hpp"}

include_re = re.compile(r'^\s*#\s*include\s+[<"]([^>"]+)[>"]')

include_map = defaultdict(set)
reverse_map = defaultdict(set)

all_files = []

for scan_dir in SCAN_DIRS:
    for path in scan_dir.rglob("*"):
        if path.is_file() and path.suffix in EXTENSIONS:
            all_files.append(path)

for path in all_files:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        continue

    for line in lines:
        m = include_re.match(line)
        if not m:
            continue

        included = Path(m.group(1)).name
        include_map[path].add(included)
        reverse_map[included].add(path)

header_files = [p for p in all_files if p.suffix in HEADER_EXTS]

results = []

for header in header_files:
    basename = header.name
    ca = len(reverse_map[basename])
    ce = len(include_map[header])
    total = ca + ce
    instability = round(ce / total, 3) if total else 0.0

    try:
        rel = str(header.relative_to(SRC_ROOT)).replace("\\", "/")
    except ValueError:
        rel = str(header)

    results.append((rel, ca, ce, instability))

results_by_ca = sorted(results, key=lambda x: x[1], reverse=True)
results_by_ce = sorted(results, key=lambda x: x[2], reverse=True)

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8") as f:
    f.write("AUDACITY 3.7.7 — HEADER COUPLING METRICS\n")
    f.write("=" * 90 + "\n")
    f.write("Ca = Afferent coupling / fan-in\n")
    f.write("Ce = Efferent coupling / fan-out\n")
    f.write("I  = Ce / (Ca + Ce)\n")
    f.write("=" * 90 + "\n\n")

    f.write("TOP 30 BY AFFERENT COUPLING Ca\n")
    f.write("-" * 90 + "\n")
    f.write(f"{'File':<70} {'Ca':>5} {'Ce':>5} {'I':>6}\n")
    f.write(f"{'-'*70} {'-'*5} {'-'*5} {'-'*6}\n")

    for rel, ca, ce, instability in results_by_ca[:30]:
        short = rel[-68:] if len(rel) > 68 else rel
        f.write(f"{short:<70} {ca:>5} {ce:>5} {instability:>6.3f}\n")

    f.write("\n\nTOP 30 BY EFFERENT COUPLING Ce\n")
    f.write("-" * 90 + "\n")
    f.write(f"{'File':<70} {'Ca':>5} {'Ce':>5} {'I':>6}\n")
    f.write(f"{'-'*70} {'-'*5} {'-'*5} {'-'*6}\n")

    for rel, ca, ce, instability in results_by_ce[:30]:
        short = rel[-68:] if len(rel) > 68 else rel
        f.write(f"{short:<70} {ca:>5} {ce:>5} {instability:>6.3f}\n")

print(f"Wrote: {OUT}")
print("Top 10 by Ca:")
for rel, ca, ce, instability in results_by_ca[:10]:
    print(f"{rel} | Ca={ca} Ce={ce} I={instability}")