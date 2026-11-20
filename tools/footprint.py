# Checks the baselines a statistics point changes against the fingerprint rows the same commits moved.
#
#   python3 footprint.py <statistics dir> <fingerprints output>...
#
# The changed baselines are the .sca files that differ from HEAD in <statistics dir> (git status). The
# moved rows are the run-0 rows the fingerprint runner reported as "FAILED (should be PASS)" in the given
# outputs (tests/fingerprint/fingerprints -d). Prints the baselines that changed without a moved row
# (usually a configuration whose baseline runs longer than its fingerprint row) and the moved rows,
# outside the excluded directories, whose baseline did not change (SKIP rows, for one).
import sys, re, subprocess
stats, logs = sys.argv[1], sys.argv[2:]
moved = set()
for log in logs:
    for m in re.finditer(r"^/(\S+)/ -f omnetpp\.ini -c (\S+) -r 0 .*?FAILED \(should be PASS\)", open(log).read(), re.M):
        moved.add(m.groups())
changed = set()
for line in subprocess.run(['git', '-C', stats, 'status', '--short'], capture_output=True, text=True).stdout.split('\n'):
    m = re.match(r'.M (.*)/omnetpp\.ini-(.*)-#0\.sca', line)
    if m:
        changed.add(m.groups())
EXCL2 = re.compile(r'(^|/)(cars|d2d_multihop|mec|videostreaming_dataset_generator)(/|$)')
print(f'changed baselines: {len(changed)}, moved run-0 rows: {len(moved)}')
print('changed without a moved row:', sorted(changed - moved))
print('moved (in scope) without a changed baseline:', sorted(x for x in moved - changed if not EXCL2.search(x[0])))
