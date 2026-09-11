#!/usr/bin/env bash
# ERNI analysis stack -- installer for a locked-down macOS work machine.
#
#   bash bootstrap_macos.sh
#
# Designed for: macOS, full network (github.com + pypi.org), NO admin rights
# and no ability to modify a shared Python.  It never writes outside $HOME.
#
# Strategy ladder -- takes the first that works:
#   1. venv in ~/erni-env          (cleanest; only writes to your home dir)
#   2. pip install --user          (when the venv module is unavailable)
# It will tell you which one it used and how to activate it.

set -euo pipefail

ROOT="${ERNI_ROOT:-$HOME/erni}"
ENVDIR="$HOME/erni-env"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Pinned commits -- these are the revisions the pipeline was verified against.
NBRAGG_SHA=ecaf764        # branch master (NOT main)
SAVEROI_SHA=abf97d4
NOTEBOOKS_SHA=6a7db0f
TSLSCHOOL_SHA=976587c

say()  { printf "\n\033[1m== %s\033[0m\n" "$*"; }
ok()   { printf "   \033[32mok\033[0m   %s\n" "$*"; }
warn() { printf "   \033[33mwarn\033[0m %s\n" "$*"; }
die()  { printf "\n\033[31mFAILED: %s\033[0m\n" "$*" >&2; exit 1; }

# ---------------------------------------------------------------- 1. python --
say "1/5  locating a usable Python (need >= 3.9)"
PY=""
for cand in python3.12 python3.11 python3.10 python3 /usr/bin/python3 \
            /opt/homebrew/bin/python3 /opt/anaconda3/bin/python3; do
  command -v "$cand" >/dev/null 2>&1 || continue
  v=$("$cand" -c 'import sys;print("%d.%d"%sys.version_info[:2])' 2>/dev/null) || continue
  maj=${v%%.*}; min=${v##*.}
  if [ "$maj" -eq 3 ] && [ "$min" -ge 9 ]; then PY="$cand"; break; fi
done
[ -n "$PY" ] || die "no python3 >= 3.9 found. Install one from python.org (no admin needed) and re-run."
ok "$PY  ($("$PY" -c 'import sys;print(sys.version.split()[0])'))"

# ------------------------------------------------------------------- 2. env --
say "2/5  setting up an install target"
MODE=""
if "$PY" -m venv --help >/dev/null 2>&1 && "$PY" -m venv "$ENVDIR" 2>/dev/null; then
  # shellcheck disable=SC1091
  source "$ENVDIR/bin/activate"
  PIP=(python -m pip)
  MODE="venv"
  ok "venv at $ENVDIR"
else
  warn "venv unavailable or blocked -- falling back to user-level installs"
  PIP=("$PY" -m pip)
  USERFLAG="--user"      # pip wants this after the subcommand, so pass it separately
  MODE="user"
  ok "will install with pip --user (into your home dir)"
fi
"${PIP[@]}" install ${USERFLAG:-} --upgrade pip setuptools wheel >/dev/null 2>&1 || \
  warn "could not upgrade pip -- continuing with the existing one"

# ----------------------------------------------------------------- 3. repos --
say "3/5  cloning repos into $ROOT/repos"
mkdir -p "$ROOT/repos"
clone_at() {  # name url sha [branch]
  local name=$1 url=$2 sha=$3 br=${4:-}
  local dir="$ROOT/repos/$name"
  if [ -d "$dir/.git" ]; then
    ok "$name already present -- fetching"
    git -C "$dir" fetch --all --quiet || warn "fetch failed for $name (offline?)"
  else
    git clone --quiet ${br:+--branch "$br"} "$url" "$dir" || die "clone failed: $name"
  fi
  git -C "$dir" checkout --quiet "$sha" || die "cannot check out $sha in $name"
  ok "$name @ $(git -C "$dir" rev-parse --short HEAD)"
}
clone_at nbragg             https://github.com/TsvikiHirsh/nbragg.git       "$NBRAGG_SHA" master
clone_at save_roi           https://github.com/TsvikiHirsh/save_roi.git     "$SAVEROI_SHA"
clone_at ncrystal-notebooks https://github.com/mctools/ncrystal-notebooks.git "$NOTEBOOKS_SHA"
clone_at TSL_School         https://github.com/highness-eu/TSL_School.git   "$TSLSCHOOL_SHA"

# -------------------------------------------------------------- 4. install ---
say "4/5  installing pinned dependencies"
"${PIP[@]}" install ${USERFLAG:-} -r "$HERE/requirements.lock.txt" \
  || die "dependency install failed -- see the pip output above"
ok "dependencies installed"

say "     installing nbragg and save_roi from the checkouts"
# These two are NOT on PyPI at the pinned versions; they must come from source.
"${PIP[@]}" install ${USERFLAG:-} "$ROOT/repos/nbragg"   || die "nbragg install failed"
"${PIP[@]}" install ${USERFLAG:-} "$ROOT/repos/save_roi" || die "save_roi install failed"
ok "nbragg + save_roi installed from source"

# --------------------------------------------------------------- 5. verify ---
say "5/5  verifying the installation"
mkdir -p "$ROOT/materials" "$ROOT/tools" "$ROOT/data" "$ROOT/work"
cp -f "$HERE"/tools/*.py       "$ROOT/tools/"     2>/dev/null || true
cp -f "$HERE"/materials/*.ncmat "$ROOT/materials/" 2>/dev/null || true

export NCRYSTAL_ONLINEDB_CACHEDIR="$ROOT/.ncrystal_cache"
mkdir -p "$NCRYSTAL_ONLINEDB_CACHEDIR"

python "$HERE/verify_install.py" --repos "$ROOT/repos" --materials "$ROOT/materials" \
  || die "verification failed -- do NOT run real data until this passes"

# ------------------------------------------------------------------ finish ---
cat <<EOF

$(printf '\033[1m=== installed ===\033[0m')

  layout      $ROOT/{repos,tools,materials,data,work}
  mode        $MODE

Add these to your ~/.zshrc so every new shell is ready:

EOF
if [ "$MODE" = "venv" ]; then
  cat <<EOF
    source $ENVDIR/bin/activate
    export NCRYSTAL_ONLINEDB_CACHEDIR="$ROOT/.ncrystal_cache"
EOF
else
  cat <<EOF
    export PATH="\$(python3 -m site --user-base)/bin:\$PATH"
    export NCRYSTAL_ONLINEDB_CACHEDIR="$ROOT/.ncrystal_cache"
EOF
fi
cat <<EOF

Next: put a TOF stack in $ROOT/data/ and follow RUNBOOK.md from step 1.
EOF
