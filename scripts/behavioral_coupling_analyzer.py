from pathlib import Path
import argparse
import csv
import json
import re
from collections import defaultdict

PATTERNS = {
    "threading": [
        r"\bstd::thread\b",
        r"\bwxThread\b",
        r"\bstd::async\b",
        r"\bstd::future\b",
        r"\bstd::promise\b",
    ],
    "synchronization": [
        r"\bstd::mutex\b",
        r"\bstd::recursive_mutex\b",
        r"\bstd::lock_guard\b",
        r"\bstd::unique_lock\b",
        r"\bstd::condition_variable\b",
        r"\bstd::atomic\b",
        r"\bstd::shared_mutex\b",
    ],
    "blocking_or_waiting": [
        r"\bwait\(",
        r"\bsleep_for\b",
        r"\bsleep_until\b",
        r"\bPa_Sleep\b",
        r"\bJoin\(",
        r"\bWait\(",
    ],
    "callbacks_events": [
        r"\bCallAfter\b",
        r"\bBind\(",
        r"\bEVT_",
        r"\bProcessEvent\b",
        r"\bQueueEvent\b",
        r"\bwxPostEvent\b",
        r"\bcallback\b",
        r"\bCallback\b",
    ],
    "audio_stream_control": [
        r"\bPa_OpenStream\b",
        r"\bPa_StartStream\b",
        r"\bPa_StopStream\b",
        r"\bPa_CloseStream\b",
        r"\bPa_AbortStream\b",
        r"\bAudioIO\b",
        r"\bStartStream\b",
        r"\bStartMonitoring\b",
    ],
    "state_transitions": [
        r"\bStart\b",
        r"\bStop\b",
        r"\bPause\b",
        r"\bResume\b",
        r"\bCommit\b",
        r"\bRollback\b",
        r"\bFlush\b",
    ],
}

SOURCE_EXTENSIONS = {
    ".cpp", ".cxx", ".cc", ".c",
    ".h", ".hpp", ".hxx"
}


def classify_file(path: Path) -> str:
    parts = [p.lower() for p in path.parts]

    if "lib-audio-io" in parts:
        return "Audio I/O"
    if "lib-track" in parts or "lib-wave-track" in parts:
        return "Track Model"
    if "lib-effects" in parts or "effects" in parts:
        return "Effects"
    if "lib-project" in parts or "project" in parts:
        return "Project State"
    if "widgets" in parts or "ui" in parts:
        return "GUI/UI"
    if "libraries" in parts:
        return "Libraries"
    if "src" in parts:
        return "Application Core"

    return "Other"


def scan_file(path: Path, root: Path):
    text = path.read_text(errors="ignore")
    rel = path.relative_to(root)

    matches = []

    for category, regexes in PATTERNS.items():
        for rgx in regexes:
            for match in re.finditer(rgx, text):
                line_no = text.count("\n", 0, match.start()) + 1
                line_start = text.rfind("\n", 0, match.start()) + 1
                line_end = text.find("\n", match.start())
                if line_end == -1:
                    line_end = len(text)

                line = text[line_start:line_end].strip()

                matches.append({
                    "file": str(rel).replace("\\", "/"),
                    "component": classify_file(rel),
                    "category": category,
                    "pattern": rgx,
                    "line": line_no,
                    "evidence": line[:250],
                })

    return matches


def write_csv(rows, output_file):
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["file", "component", "category", "pattern", "line", "evidence"]
        )
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows, output_file):
    by_category = defaultdict(int)
    by_component = defaultdict(int)
    by_component_category = defaultdict(lambda: defaultdict(int))

    for row in rows:
        by_category[row["category"]] += 1
        by_component[row["component"]] += 1
        by_component_category[row["component"]][row["category"]] += 1

    with output_file.open("w", encoding="utf-8") as f:
        f.write("# MT4 Behavioral and Synchronization Dependency Summary\n\n")

        f.write("## Matches by dependency category\n\n")
        f.write("| Category | Matches |\n")
        f.write("|---|---:|\n")
        for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {category} | {count} |\n")

        f.write("\n## Matches by component\n\n")
        f.write("| Component | Matches |\n")
        f.write("|---|---:|\n")
        for component, count in sorted(by_component.items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {component} | {count} |\n")

        f.write("\n## Component x category matrix\n\n")
        categories = sorted(PATTERNS.keys())
        f.write("| Component | " + " | ".join(categories) + " |\n")
        f.write("|---|" + "|".join(["---:"] * len(categories)) + "|\n")

        for component in sorted(by_component_category.keys()):
            counts = [str(by_component_category[component].get(cat, 0)) for cat in categories]
            f.write(f"| {component} | " + " | ".join(counts) + " |\n")

        f.write("\n## Interpretation guide\n\n")
        f.write("- `audio_stream_control` indicates behavioral dependencies around playback, recording, and PortAudio stream lifecycle.\n")
        f.write("- `callbacks_events` indicates callback/event-driven dependencies, especially GUI event dispatch and deferred execution.\n")
        f.write("- `synchronization` and `blocking_or_waiting` indicate synchronization dependencies, where one execution path may wait for another.\n")
        f.write("- `state_transitions` indicates sequential ordering assumptions such as start/stop/pause/commit/flush operations.\n")


def write_json(rows, output_file):
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True, help="Path to Audacity source repository")
    parser.add_argument("--out", required=True, help="Output directory")
    args = parser.parse_args()

    src = Path(args.src).resolve()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        raise SystemExit(f"Source path does not exist: {src}")

    rows = []

    for path in src.rglob("*"):
        if path.is_file() and path.suffix.lower() in SOURCE_EXTENSIONS:
            rows.extend(scan_file(path, src))

    write_csv(rows, out / "behavioral-dependencies.csv")
    write_json(rows, out / "behavioral-dependencies.json")
    write_summary(rows, out / "behavioral-dependencies-summary.md")

    print(f"Scanned source: {src}")
    print(f"Matches found: {len(rows)}")
    print(f"CSV written to: {out / 'behavioral-dependencies.csv'}")
    print(f"Summary written to: {out / 'behavioral-dependencies-summary.md'}")


if __name__ == "__main__":
    main()