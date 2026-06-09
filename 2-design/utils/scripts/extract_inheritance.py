from pathlib import Path
import re

SRC_ROOT = Path(r"E:\SDA\Audacity-Source\audacity")
OUT = Path(r"analysis\dependencies\mt2-structural\inheritance-raw.txt")

TARGET_CLASSES = {
    "Track",
    "PlayableTrack",
    "AudioTrack",
    "SampleTrack",
    "WaveTrack",
    "LabelTrack",
    "TimeTrack",
    "NoteTrack",
}

SEARCH_ROOTS = [
    SRC_ROOT / "libraries",
    SRC_ROOT / "src",
]

CLASS_START = re.compile(r"^\s*class\b")
PURE_VIRTUAL = re.compile(r"=\s*0\s*;")

def rel(path: Path) -> str:
    try:
        return str(path.relative_to(SRC_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)

def normalize_decl(lines):
    return " ".join(line.strip() for line in lines)

def extract_class_name_and_base(decl):
    # Handles:
    # class TRACK_API Track : public ChannelGroup
    # class WAVE_TRACK_API WaveTrack final : public AudioTrack
    # class Foo : public Bar, public Baz
    decl = decl.replace("{", " { ").replace(";", " ; ")
    m = re.search(
        r"\bclass\s+(?:(?:[A-Z0-9_]+_API|[A-Za-z_][A-Za-z0-9_]*_API)\s+)?"
        r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
        r"(?:\s+final)?"
        r"(?:\s*:\s*(?P<bases>[^;{]+))?",
        decl,
    )
    if not m:
        return None, None

    name = m.group("name")
    bases_raw = m.group("bases")
    if not bases_raw:
        return name, None

    bases = []
    for part in bases_raw.split(","):
        part = part.strip()
        part = re.sub(r"\bpublic\b|\bprotected\b|\bprivate\b|\bvirtual\b", "", part).strip()
        bases.append(part)
    return name, ", ".join(bases)

def scan_class_declarations():
    rows = []
    target_rows = []

    for root in SEARCH_ROOTS:
        for path in root.rglob("*.h"):
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue

            i = 0
            while i < len(lines):
                line = lines[i]

                if CLASS_START.search(line):
                    start_line = i + 1
                    decl_lines = [line]

                    # collect multi-line declaration until { or ;
                    j = i
                    while j + 1 < len(lines) and "{" not in normalize_decl(decl_lines) and ";" not in normalize_decl(decl_lines):
                        j += 1
                        decl_lines.append(lines[j])
                        if len(decl_lines) > 12:
                            break

                    decl = normalize_decl(decl_lines)
                    name, bases = extract_class_name_and_base(decl)

                    # skip pure forward declarations like: class WaveTrack;
                    is_forward_decl = ";" in decl and "{" not in decl and bases is None

                    if name and bases and not is_forward_decl:
                        row = f"{rel(path)}:{start_line}: {decl}"
                        rows.append(row)

                        if name in TARGET_CLASSES or any(t in bases for t in TARGET_CLASSES):
                            target_rows.append(row)

                    i = j

                i += 1

    return rows, target_rows

def scan_pure_virtual_track():
    rows = []
    track_h = SRC_ROOT / "libraries" / "lib-track" / "Track.h"
    try:
        lines = track_h.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return rows

    for i, line in enumerate(lines, 1):
        if PURE_VIRTUAL.search(line):
            rows.append(f"{rel(track_h)}:{i}: {line.strip()}")
    return rows

all_rows, target_rows = scan_class_declarations()
pure_virtual_rows = scan_pure_virtual_track()

OUT.parent.mkdir(parents=True, exist_ok=True)

with OUT.open("w", encoding="utf-8") as f:
    f.write("=== ALL PUBLIC INHERITANCE RELATIONSHIPS ===\n")
    for row in all_rows:
        f.write(row + "\n")

    f.write("\n=== TARGET TRACK-RELATED INHERITANCE RELATIONSHIPS ===\n")
    for row in target_rows:
        f.write(row + "\n")

    f.write("\n=== PURE VIRTUAL INTERFACE OF Track.h ===\n")
    for row in pure_virtual_rows:
        f.write(row + "\n")

    f.write("\n=== SUMMARY ===\n")
    f.write(f"Total public inheritance declarations found: {len(all_rows)}\n")
    f.write(f"Track-related inheritance declarations found: {len(target_rows)}\n")
    f.write(f"Pure virtual Track interface entries found: {len(pure_virtual_rows)}\n")

print(f"Wrote: {OUT}")
print(f"Total public inheritance declarations found: {len(all_rows)}")
print(f"Track-related inheritance declarations found: {len(target_rows)}")
print(f"Pure virtual Track interface entries found: {len(pure_virtual_rows)}")