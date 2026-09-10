#!/usr/bin/env python3
"""Install the roadkeep CLI from PyPI.

Why this exists
---------------
roadkeep owns the writes to docs/ROADMAP.md, docs/CHANGELOG.md and
docs/IMPROVEMENTS.md, and .claude/settings.json runs ``roadkeep guard`` from a
PreToolUse hook matching Edit|MultiEdit|NotebookEdit|Write|Bash. On a machine
without the CLI that hook fails, and a hook failing with exit 2 blocks every
mutating tool in the session -- including the ones that would install the CLI.
A fresh container is exactly that machine, and the state is unrecoverable from
inside a session.

So this runs as the first SessionStart hook, ahead of the guard, and puts the
CLI in place before the gate is asked anything.

Idempotent: with roadkeep already importable or on PATH it is a no-op, which is
the usual case on a machine that keeps its environment between sessions.

Overrides
---------
ROADKEEP_VERSION
    A pip version specifier such as ``0.2.0``. Defaults to the latest release.

Note on ``[install] wired = "0.2.450"`` in roadkeep.toml: that is not a PyPI
version -- the package index publishes 0.2.0 -- so it is deliberately not used
as a pin here. Set ROADKEEP_VERSION if this project needs to freeze one.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

PACKAGE = "roadkeep"
MIN_PYTHON = (3, 11)  # roadkeep's own requires-python


def log(msg: str) -> None:
    print(f"install-roadkeep: {msg}", file=sys.stderr)


def installed() -> bool:
    """True when roadkeep can already be reached by either route.

    The import check is the one that matters after a ``--user`` install, where
    the console script lands in a directory PATH may not carry.
    """
    if shutil.which(PACKAGE):
        return True
    try:
        subprocess.run(
            [sys.executable, "-c", f"import {PACKAGE}"],
            check=True,
            capture_output=True,
        )
    except (subprocess.CalledProcessError, OSError):
        return False
    return True


def pip_install(spec: str, *extra: str) -> bool:
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", *extra, spec]
    log(" ".join(cmd))
    try:
        return subprocess.run(cmd).returncode == 0
    except OSError as exc:
        log(f"could not run pip: {exc}")
        return False


def main() -> int:
    if installed():
        log("already installed")
        return 0

    if sys.version_info < MIN_PYTHON:
        want = ".".join(str(n) for n in MIN_PYTHON)
        log(f"ERROR: roadkeep needs Python >= {want}")
        log(f"       this is {sys.version.split()[0]} at {sys.executable}")
        return 1

    version = os.environ.get("ROADKEEP_VERSION", "").strip()
    spec = f"{PACKAGE}=={version}" if version else PACKAGE

    # Plain install first. --break-system-packages is the documented escape for
    # a PEP 668 externally-managed interpreter, which is what most container
    # images now ship; --user then covers an unwritable site-packages.
    for extra in ((), ("--break-system-packages",), ("--user", "--break-system-packages")):
        if pip_install(spec, *extra):
            break
    else:
        log(f"ERROR: could not install {spec}")
        return 1

    # Verify what we came for rather than trusting pip's exit code: an install
    # into an interpreter other than the one the hooks use still leaves the
    # gate broken, and does it silently.
    if not installed():
        log("ERROR: pip reported success but roadkeep is still not importable")
        log(f"       interpreter: {sys.executable}")
        log(f"       PATH: {os.environ.get('PATH', '')}")
        return 1

    log(f"installed {spec}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
