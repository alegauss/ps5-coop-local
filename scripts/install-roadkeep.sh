#!/usr/bin/env sh
# Put the roadkeep launcher next to this repository.
#
# Why this exists
# ---------------
# The three files in docs/ are owned by the roadkeep CLI, and
# .claude/settings.json gates Edit/MultiEdit/NotebookEdit/Write/Bash behind
# `roadkeep.py guard`. The launcher is addressed relatively, as
# ../roadkeep/scripts/roadkeep.py, so it has to be a *sibling* of the repo
# root rather than anything inside it.
#
# When that sibling is missing the gate fails closed rather than open: python
# exits 2 because it cannot open the file, PreToolUse reads exit 2 as a block,
# and every mutating tool in the session is refused -- including the Write that
# would install the launcher. A session cannot dig itself out. So this runs
# from the SessionStart hook, before the gate is ever asked a question.
#
# Idempotent: with the launcher already present it is a no-op, which is the
# usual case on a machine that keeps its checkouts.
#
# Overrides:
#   ROADKEEP_HOME    where the launcher goes  (default: <repo>/../roadkeep)
#   ROADKEEP_REMOTE  where it is cloned from  (default: the GitHub remote)
#   ROADKEEP_REF     branch or tag to check out (default: the default branch)
set -eu

REPO_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TARGET=${ROADKEEP_HOME:-"$(dirname -- "$REPO_ROOT")/roadkeep"}
LAUNCHER="$TARGET/scripts/roadkeep.py"
REMOTE=${ROADKEEP_REMOTE:-https://github.com/alegauss/roadkeep.git}

log() { printf 'install-roadkeep: %s\n' "$*" >&2; }

# The guard and the MCP server both spell the interpreter `python`, not
# `python3`. Worth naming now: the failure it produces otherwise is
# `command not found` from a hook, which is easy to read as the launcher
# being missing again.
if ! command -v python >/dev/null 2>&1; then
  log "WARNING: 'python' is not on PATH -- the guard hook invokes it by that name"
fi

if [ -f "$LAUNCHER" ]; then
  log "already present at $TARGET"
  exit 0
fi

# Something is at the target but it is not a roadkeep checkout. Report it and
# stop. Deleting would be the wrong reflex: a clone from a concurrent turn is
# indistinguishable from a dead one at a glance, and the cost of being wrong is
# somebody else's working tree.
if [ -d "$TARGET" ] && [ -n "$(ls -A "$TARGET" 2>/dev/null || true)" ]; then
  if git -C "$TARGET" rev-parse HEAD >/dev/null 2>&1; then
    log "ERROR: $TARGET is a git checkout, but has no scripts/roadkeep.py"
    log "       check that it is really alegauss/roadkeep:"
    log "       git -C $TARGET remote get-url origin"
  else
    log "ERROR: $TARGET is not empty and is not a git checkout; refusing to overwrite"
  fi
  exit 1
fi

log "cloning $REMOTE -> $TARGET"
# GIT_LFS_SKIP_SMUDGE is load-bearing where the clone goes through an anonymous
# git proxy that does not serve LFS objects: unprefixed, the smudge filter
# aborts the whole clone.
if [ -n "${ROADKEEP_REF:-}" ]; then
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --branch "$ROADKEEP_REF" "$REMOTE" "$TARGET"
else
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 "$REMOTE" "$TARGET"
fi

# Verify the thing we came for, rather than trusting the clone's exit code: a
# clone of the wrong ref, or of a repo whose layout moved, succeeds and still
# leaves the gate broken.
if [ ! -f "$LAUNCHER" ]; then
  log "ERROR: clone succeeded but $LAUNCHER is missing"
  log "       the launcher path in .claude/settings.json may need updating"
  exit 1
fi

log "installed $(git -C "$TARGET" rev-parse --short HEAD 2>/dev/null || echo '?') at $TARGET"
