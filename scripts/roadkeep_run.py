#!/usr/bin/env python3
"""Resolve the roadkeep CLI, however this machine has it, and run it.

Three installs are in the wild and all of them are legitimate:

1. ``pip install roadkeep``, giving a ``roadkeep`` console script on PATH
2. the same wheel where PATH misses pip's script directory -> ``-m roadkeep``
3. a sibling checkout at ``../roadkeep/scripts/roadkeep.py``

The callers -- the hooks in .claude/settings.json and the server in .mcp.json --
should not have to know which. This is written in Python rather than sh because
those callers already require a python interpreter, and some of them run on
Windows where ``sh`` is not dependable.

Exit codes are roadkeep's own, passed through untouched. That matters: a
PreToolUse hook exiting 2 means "block this tool call", and that verdict belongs
to roadkeep, not to this wrapper.

When roadkeep is NOT found this exits 1, deliberately, and never 2. A missing
CLI is an infrastructure fault rather than a policy violation, and exit 2 from a
hook matching Edit|MultiEdit|NotebookEdit|Write|Bash blocks every mutating tool
in the session -- including the ones needed to install the CLI, which makes the
state unrecoverable from inside a session. Exit 1 is loud and reported but
leaves the session able to repair itself.

The trade is deliberate and worth naming: while roadkeep is missing the governed
files are unguarded, so the message says exactly that.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
LEGACY = os.path.join(
    os.path.dirname(REPO_ROOT), "roadkeep", "scripts", "roadkeep.py"
)


def resolve():
    """Return the argv prefix that runs roadkeep, or None if it is absent."""
    exe = shutil.which("roadkeep")
    if exe:
        return [exe]

    local = os.path.join(os.path.expanduser("~"), ".local", "bin", "roadkeep")
    if os.access(local, os.X_OK):
        return [local]

    try:
        subprocess.run(
            [sys.executable, "-c", "import roadkeep"],
            check=True,
            capture_output=True,
        )
        return [sys.executable, "-m", "roadkeep"]
    except (subprocess.CalledProcessError, OSError):
        pass

    if os.path.isfile(LEGACY):
        return [sys.executable, LEGACY]

    return None


def main(argv):
    cmd = resolve()
    if cmd is None:
        installer = os.path.join(HERE, "install_roadkeep.py")
        print(
            "roadkeep: not installed.\n"
            f"  install it with:  {sys.executable} {installer}\n"
            "  until it is back, docs/ROADMAP.md, docs/CHANGELOG.md and\n"
            "  docs/IMPROVEMENTS.md are UNGUARDED -- do not hand-edit them.",
            file=sys.stderr,
        )
        return 1

    try:
        return subprocess.run(cmd + list(argv)).returncode
    except OSError as exc:
        print(f"roadkeep: could not run {cmd[0]}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
