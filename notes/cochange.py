from collections import Counter
from itertools import combinations
from pathlib import Path
import subprocess

TARGET_PREFIXES = (
    "src/",
    "au3/src/",
    "au3/libraries/",
    "au3/modules/",
)

EXCLUDED_PARTS = (
    "thirdparty/",
    "docs/",
    "images/",
    "help/",
    "buildscripts/",
)

log = subprocess.check_output(
    ["git", "log", "--name-only", "--pretty=format:COMMIT"],
    text=True,
    errors="ignore"
)

commits = []
current_files = []

for line in log.splitlines():
    line = line.strip()

    if line == "COMMIT":
        if current_files:
            commits.append(sorted(set(current_files)))
        current_files = []
        continue

    if not line:
        continue

    if not line.startswith(TARGET_PREFIXES):
        continue

    if any(part in line for part in EXCLUDED_PARTS):
        continue

    if line.endswith((".cpp", ".h", ".hpp", ".cxx", ".cc")):
        current_files.append(line)

if current_files:
    commits.append(sorted(set(current_files)))

pairs = Counter()

for files in commits:
    # Skip huge commits because they are usually formatting, moves, or mass refactors
    if len(files) > 30:
        continue

    for a, b in combinations(files, 2):
        pairs[(a, b)] += 1

output = Path("notes/top_cochange_pairs.txt")
with output.open("w", encoding="utf-8") as f:
    for (a, b), count in pairs.most_common(100):
        f.write(f"{count}\t{a}\t{b}\n")

print(f"Written: {output}")
