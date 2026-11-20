#!/bin/bash
# Records one statistics point of a Simu5G tree into a statistics repo.
#
#   tools/statpoint.sh <simu5g tree> <commit> <statistics dir> <output dir>
#
# The tree must be a clean checkout of <commit> (a worktree keeps the main checkout on its branch).
# Builds it in debug, runs statrec.py with SIMU5G_ROOT=<tree> and STATS=<statistics dir>, and rewrites
# the image path that the recorded .sca files name from <tree> to the main checkout, the parent of
# <statistics dir>. Build and recording logs go to <output dir>.
# Environment: PYTHON, a python that loads OMNeT++'s scave bindings (default python3);
#              OPP_REPL, opp_repl's source directory (added to PYTHONPATH).
set -u
W=$(realpath "$1"); C=$2; STATSDIR=$(realpath "$3"); OUT=$4
M=$(dirname "$STATSDIR")
TOOLS=$(dirname "$(realpath "$0")")
mkdir -p "$OUT"
cd "$W" && [ "$(git rev-parse HEAD)" = "$(git rev-parse "$C^{commit}")" ] && git diff --quiet HEAD || { echo "$W is not a clean checkout of $C"; exit 1; }
nice -n 19 make MODE=debug -j8 > "$OUT/build.log" 2>&1 || { echo "BUILD FAILED, see $OUT/build.log"; exit 1; }
export SIMU5G_ROOT=$W
PYTHONPATH="$PYTHONPATH:${OPP_REPL:?set OPP_REPL to the opp_repl source directory}" OPP_FILE=$M/simu5g.opp STATS=$STATSDIR \
    nice -n 19 "${PYTHON:-python3}" "$TOOLS/statrec.py" > "$OUT/statrec.out" 2>&1
echo "statrec exit $?"
cd "$STATSDIR" && git status --short --untracked-files=all | grep -E '\.sca$' | awk '{print $2}' | while read f; do
    sed -i "s|$W/images|$M/images|" "$f"; done
grep -E "^== |^   " "$OUT/statrec.out"
