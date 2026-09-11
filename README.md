# backgroundInfo

Notes, analysis scripts and accumulated context for the LANL **ERNI** work — energy-resolved
neutron imaging of hydride moderators at LANSCE (HIPPO FP4).

This repo carries the *text*: state documents, scripts, reference material. The neutron data
stays on the work machine at `~/Desktop/hippo`.

## Read first

**[HANDOFF.md](HANDOFF.md)** — the current state of the work, written to be picked up cold.
The YH₂ in-situ heating campaign, the measurement to run first, what calibration transfers
from the earlier ZrH₂ run and what does not, and the traps that each cost a debugging cycle.

Then:

- **[CLAUDE.md](CLAUDE.md)** — project instructions and standing corrections
- **[ERNI-RESUME.md](ERNI-RESUME.md)** — running log of the ZrH₂ run 111859 analysis, including
  two findings that were later retracted; read the dated sections in order
- **[HANDBOOK.md](HANDBOOK.md)**, **[HANDBOOK-II.md](HANDBOOK-II.md)** — background reference

## Layout

```
HANDOFF.md              current state, start here
CLAUDE.md               project instructions
ERNI-RESUME.md          run 111859 analysis log
HANDBOOK.md             background reference
HANDBOOK-II.md          background reference
braggIterations.py      Brendt Wohlberg's original analysis script
erni-toolkit/
  README.md             toolkit overview
  RUNBOOK.md            environment setup and procedures
  bootstrap_macos.sh    environment bootstrap
  verify_install.py     install check
  requirements.lock.txt pinned versions
  materials/            NCMAT skeletons for δ-YH₂ and δ-ZrH₂
  tools/                analysis scripts — see HANDOFF.md for what each does
```

## Two things worth knowing before running anything

**Most scripts were written for run 111859** — ZrH₂ in an aluminium can, flight path 8.95 m.
The YH₂ campaign uses a different detector position, a TZM can and a different sample. The
method carries over; the numbers do not. HANDOFF.md has the full list.

**Verify by executing.** Every real bug this stack produced was invisible to reading.
