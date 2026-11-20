# Compares two statistics trees value by value.
#
#   python3 scadiff.py <dirA> <dirB> [--files] [--stats N] [--onlyfiles <regex>]
#
# Every .sca present in both is parsed (shlex: INET's SCTP names contain spaces) into
# (module, scalar name) and (module, statistic, field) -> value. Prints the number of files that differ
# in values (run metadata such as run id and date does not count), added and removed files, and per
# statistic name the number of changed files and values and the median relative change.
# --files lists the changed files with their number of changed values.
# Compares every .sca under dirA and dirB by (module, name[, field]) -> value.
import sys, os, re, shlex, math, collections
A, B = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
def load(path):
    d = {}; cur = None
    for line in open(path, errors='replace'):
        if not line or line[0] not in 'sf': continue
        try: p = shlex.split(line)
        except ValueError: continue
        if p[0] == 'scalar' and len(p) >= 4:
            d[(p[1], p[2], '')] = p[3]; cur = None
        elif p[0] == 'statistic' and len(p) >= 3:
            cur = (p[1], p[2])
        elif p[0] == 'field' and cur and len(p) >= 3:
            d[(cur[0], cur[1], p[1])] = p[2]
    return d
def files(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        if '.git' in dp: continue
        for f in fn:
            if f.endswith('.sca'): out[os.path.relpath(os.path.join(dp, f), root)] = os.path.join(dp, f)
    return out
fa, fb = files(A), files(B)
only = None
if '--onlyfiles' in args: only = re.compile(args[args.index('--onlyfiles') + 1])
changed = {}; added = sorted(set(fb) - set(fa)); removed = sorted(set(fa) - set(fb))
bystat = collections.defaultdict(lambda: [0, 0, []])   # name:field -> [files, values, rel changes]
for f in sorted(set(fa) & set(fb)):
    if only and not only.search(f): continue
    da, db = load(fa[f]), load(fb[f])
    diff = [k for k in set(da) | set(db) if da.get(k) != db.get(k)]
    if not diff: continue
    changed[f] = diff
    seen = set()
    for k in diff:
        key = k[1] + (':' + k[2] if k[2] else '')
        s = bystat[key]; s[1] += 1
        if key not in seen: s[0] += 1; seen.add(key)
        try:
            va, vb = float(da.get(k, 'nan')), float(db.get(k, 'nan'))
            if math.isfinite(va) and math.isfinite(vb) and va != 0: s[2].append((vb - va) / abs(va))
        except ValueError: pass
print(f'files: {len(set(fa) & set(fb))} common, {len(changed)} changed, {len(added)} added, {len(removed)} removed')
for f in added: print('  ADDED', f)
for f in removed: print('  REMOVED', f)
if '--files' in args:
    for f, d in changed.items(): print(f'  {f}: {len(d)} values')
n = int(args[args.index('--stats') + 1]) if '--stats' in args else 40
print(f'statistics changed (files, values, median relative change), top {n} by files:')
for key, (nf, nv, rel) in sorted(bystat.items(), key=lambda kv: (-kv[1][0], -kv[1][1]))[:n]:
    med = sorted(rel)[len(rel) // 2] if rel else float('nan')
    print(f'  {key:45s} {nf:4d} files {nv:6d} values  median rel {med:+.3g}')
