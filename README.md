Simu5G statistics baselines
===========================

The run-0 scalar results (`.sca`) of Simu5G's example configurations, one baseline per configuration,
recorded with opp_repl's statistical tests. Each commit is a point: the baselines of one Simu5G commit,
with a message that says what changed, which Simu5G commits changed it, why the new values are right,
and how that was established (a Method section).

Recording a point
-----------------

    tools/statpoint.sh <simu5g tree> <commit> <this repo> <output dir>

builds the tree in debug and records with `tools/statrec.py`: every working directory except `cars`,
`d2d_multihop`, `mec` and `videostreaming_dataset_generator`, then `rnisTest`. Use a worktree of the
Simu5G repo for the tree, and set `PYTHON` (a python that loads OMNeT++'s scave bindings) and `OPP_REPL`
(opp_repl's source directory). A pass recorded against an older point rewrites files whose values equal
the newer point's with only new run metadata (run id, date); keep the newer point's version of those.

Writing a point's message
-------------------------

The subject names the Simu5G commit and a label: `Update statistical baselines for Simu5G dev (<hash>,
<label>)`. Right after the opening paragraph, a section maps every commit the message names to its
subject line, in the order of first mention, so that a reader need not look the hashes up:

    Simu5G commits named here
    -------------------------
      c3ab8e2d4 LteSchedulerEnb: fix: a UE's allowed-band restriction also applied to the UEs scheduled after it in the slot
      0363fed3f phy-fixes: tests/doc: chore: the model-deviation and open-defect lists leave the repository

A commit of this repo is listed the same way, its subject marked `statistics:`; its hash changes when
this history is rewritten. Then come the recording calls, the pass's counts, and the sections Method,
What changed, Attribution and Why the new values are right.

Analyzing a point
-----------------

- `tools/scadiff.py <dirA> <dirB>`: what changed, value by value, keyed by (module, name[, field]);
  run metadata does not count. Export a point with `git archive <commit> | tar -x -C <dir>`.
- `tools/footprint.py <this repo> <fingerprints output>...`: the changed baselines against the run-0
  fingerprint rows the same Simu5G commits moved. A baseline that changed without a moved row usually
  runs longer than its fingerprint row.
- `tools/uestats.py <dirA> <dirB> <file regex>`: the key statistics of every UE that differ.
- `tools/regimes.py <dirA> <dirB>`: the per-UE regime analysis for changes of the SINR-to-BLER mapping:
  the change of each UE's first-transmission HARQ error rate and CQI, grouped by its mean SINR at
  `<dirA>` (below 0, 0 to 20, above 20 dB). One seed per configuration: only the aggregate counts.

Record a point at each cut that separates changes of different kinds, so that each has its own diff.
