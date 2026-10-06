"""Number '@@' step placeholders and lint house-style sequence diagrams.

Usage:
    python number_steps.py [--shapes] [--no-colon] <file.puml> [<file.puml> ...]

    --shapes    convention uses UML shapes (boundary/control/entity/database/...)
                instead of plain `participant` declarations
    --no-colon  convention does NOT prefix participant labels with ':'

Numbering (only for files that still contain '@@'):
    main flow steps            -> 1.  2.  3. ...
    k-th `break` after step N  -> N.k.1.  N.k.2. ...

Lint (always): reports style violations; exit code 1 if any file has problems.
"""
import re
import sys
from pathlib import Path

ARROW_RE = re.compile(r"^\s*(\w+)\s*(-->|->)\s*(\w+)(\s*(\+\+|--))?\s*:\s*(.*)$")
BREAK_RE = re.compile(r"^\s*break\b")
END_RE = re.compile(r"^\s*end\s*$")
DECL_RE = re.compile(
    r'^\s*(actor|participant|boundary|control|entity|database|collections|queue)\s+"([^"]*)"\s+as\s+(\w+)'
)
SHAPES = {"boundary", "control", "entity", "database", "collections", "queue"}
CODE_LABEL_RE = re.compile(r"[A-Za-z_]\w*\(|[{}]|/api/|=>|\breq\.|\bres\.")
STEP_RE = re.compile(r"^\d+(\.\d+\.\d+)?\. \S")
DISCOURAGED = re.compile(r"^\s*(alt|else|opt|loop|group|ref|par|note)\b")
MERGED_NAME_RE = re.compile(r"\+|&|/|,|\band\b")
GENERIC_ACTOR_NAMES = {"", "actor", "user", "users", "role", "person", "someone", "client"}


def number(lines):
    main, break_count, prefix, sub = 0, {}, None, 0
    out = []
    for line in lines:
        if BREAK_RE.match(line):
            if prefix is not None:
                raise ValueError("nested break is not allowed")
            break_count[main] = break_count.get(main, 0) + 1
            prefix, sub = f"{main}.{break_count[main]}", 0
        elif END_RE.match(line) and prefix is not None:
            prefix = None
        elif "@@" in line:
            if prefix is None:
                main += 1
                label = f"{main}."
            else:
                sub += 1
                label = f"{prefix}.{sub}."
            line = line.replace("@@", label, 1)
        out.append(line)
    return out


def lint(lines, allow_shapes, require_colon):
    problems = []
    text = "\n".join(lines)
    if re.search(r"^\s*title\b", text, re.M):
        problems.append("has a `title` (the document heading lives outside the image)")
    if "hide footbox" not in text:
        problems.append("missing `hide footbox`")
    if "ParticipantPadding" in text:
        problems.append("uses `skinparam ParticipantPadding` (renders a warning banner)")

    actor_aliases = []
    depth = 0
    for no, line in enumerate(lines, 1):
        d = DECL_RE.match(line)
        if d:
            kind, label, alias = d.groups()
            if kind == "actor":
                actor_aliases.append(alias)
                bare = label.lstrip(":").strip().lower()
                if bare in GENERIC_ACTOR_NAMES or "<" in label or ">" in label:
                    problems.append(f"line {no}: actor label {label!r} is generic/placeholder - use the concrete user role (ask if unknown)")
            else:
                if kind in SHAPES and not allow_shapes:
                    problems.append(f"line {no}: `{kind}` shape used - declare with `participant` (or lint with --shapes if the convention uses shapes)")
                if require_colon and not label.startswith(":"):
                    problems.append(f"line {no}: participant label {label!r} should start with ':' (e.g. ':{label}')")
                if MERGED_NAME_RE.search(label):
                    problems.append(f"line {no}: participant {label!r} looks like several files merged - use one participant per file")
        if DISCOURAGED.match(line):
            problems.append(f"line {no}: `{line.strip().split()[0]}` - house style uses flat `break` blocks and labels instead")
        if BREAK_RE.match(line):
            depth += 1
            if depth > 1:
                problems.append(f"line {no}: nested break")
        elif END_RE.match(line):
            depth = max(0, depth - 1)
        a = ARROW_RE.match(line)
        if a:
            label = a.group(6).strip()
            if "@@" in label:
                problems.append(f"line {no}: unnumbered step")
            elif not STEP_RE.match(label):
                problems.append(f"line {no}: label should start with a step number like `3.` or `3.1.1.`")
            if CODE_LABEL_RE.search(label):
                problems.append(f"line {no}: label looks like code ({label!r}) - use short prose")

    if not actor_aliases:
        problems.append("no actor declared")
    for alias in actor_aliases:
        if not re.search(rf"^activate {alias}\s*$", text, re.M) or not re.search(rf"^deactivate {alias}\s*$", text, re.M):
            problems.append(f"actor `{alias}` lifeline not activated (`activate {alias}` ... `deactivate {alias}`)")
    return problems


def main(argv):
    allow_shapes = "--shapes" in argv
    require_colon = "--no-colon" not in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    failed = False
    for path in paths:
        p = Path(path)
        lines = p.read_text(encoding="utf-8").splitlines()
        if any("@@" in l for l in lines):
            lines = number(lines)
            p.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
            status = "numbered"
        else:
            status = "checked"
        problems = lint(lines, allow_shapes, require_colon)
        if problems:
            failed = True
            print(f"[FAIL] {p} ({status})")
            for msg in problems:
                print(f"   - {msg}")
        else:
            print(f"[ OK ] {p} ({status})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
