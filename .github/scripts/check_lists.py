#!/usr/bin/env python3
"""Check feature lists against the format of AD-16 in flagscope (HU-18, HU-19).

Usage: check_lists.py PATH...  (paths relative to the repository root, as git prints them)
Prints one "file:line: problem" line per problem and exits 1 if there is any.
"""
import re
import sys
from pathlib import PurePosixPath

TITLE = "# flagscope feature list"
HEADER_KEYS = ("Build", "Architecture", "Generator", "Scanned")
U32_MAX = 2**32 - 1  # feature IDs and build numbers are u32 in flagscope-core
FEATURE_LINE = re.compile(r"[^\s:]+: [0-9]+")
BUILD = re.compile(r"([0-9]+)\.([0-9]+)")


def is_list(path):
    # AD-26: a list is any file in a top-level folder that does not start with a dot.
    parts = PurePosixPath(path).parts
    return len(parts) > 1 and not parts[0].startswith(".")


def check(path):
    problems = []

    def report(line, message):
        problems.append(f"{path}:{line}: {message}" if line else f"{path}: {message}")

    try:
        with open(path, "rb") as file:
            text = file.read().decode("utf-8")
    except UnicodeDecodeError:
        report(0, "the file is not UTF-8 text")
        return problems
    # A CR before LF is ignored, as flagscope-core does, so a Windows checkout with autocrlf passes too.
    lines = [line.removesuffix("\r") for line in text.split("\n")]
    if lines[-1] == "":
        lines.pop()

    # The header is read exactly as flagscope's ListHeader::parse reads it: the title, then these keys in order.
    if not lines or lines[0] != TITLE:
        report(1, f"the first line must be '{TITLE}'")
    header = {}
    for number, key in enumerate(HEADER_KEYS, start=2):
        line = lines[number - 1] if number <= len(lines) else ""
        prefix = f"# {key}: "
        if line.startswith(prefix) and line[len(prefix):]:
            header[key] = line[len(prefix):]
        else:
            report(number, f"line {number} must be '{prefix}<value>'")
    first = 0
    while first < len(lines) and lines[first].startswith("#"):
        first += 1

    build, architecture = header.get("Build", ""), header.get("Architecture", "")
    numbers = BUILD.fullmatch(build)
    if build and not (numbers and int(numbers[1]) <= U32_MAX and int(numbers[2]) <= U32_MAX):
        report(2, f"the build {build!r} in the header is not <major>.<revision>")
        numbers = None
    if numbers and architecture:
        expected = f"{architecture}/{numbers[1]}/{build}.txt"
        if path != expected:
            report(0, f"the header says build {build} on {architecture}, so the path must be {expected}")

    previous = None
    seen = {}
    for number, line in enumerate(lines[first:], start=first + 1):
        if line.startswith("#"):
            report(number, "a '#' line after the first feature line")
            continue
        if not FEATURE_LINE.fullmatch(line):
            report(number, f"not a 'Name: ID' line: {line!r}")
            continue
        name, feature_id = line.split(": ", 1)
        if int(feature_id) > U32_MAX:
            report(number, f"the ID of {name} is larger than {U32_MAX}")
        if name in seen:
            report(number, f"the name {name} is already on line {seen[name]}")
        else:
            seen[name] = number
        if previous is not None and name.encode() < previous.encode():
            report(number, f"{name} is out of order: it sorts before {previous} on the line above")
        previous = name
    return problems


def main(paths):
    lists = [path for path in paths if is_list(path)]
    problems = [problem for path in lists for problem in check(path)]
    for problem in problems:
        print(problem)
    print(f"Checked {len(lists)} list(s): {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
