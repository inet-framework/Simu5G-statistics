# Per-UE regime analysis between two statistics trees (for a change of the SINR-to-BLER mapping).
#
#   python3 regimes.py <dirA> <dirB>
#
# For every UE module (ue*, car*) of every file whose values differ, the UE's mean received SINR in
# <dirA> (rcvdSinrDl/rcvdSinrUl) puts it in a regime: below 0, 0 to 20, above 20 dB, per direction. The
# change of its first-transmission HARQ error rate and of its average CQI from <dirA> to <dirB> is
# collected per (direction, statistic, regime); printed: number of UEs, mean change, a 95% interval
# (1.96 standard errors), UEs up and down.
# Limits: one seed per configuration, so a single UE's change is noise and only the aggregate counts;
# the regime is the UE's mean SINR, while its receptions spread around it; background UEs record
# neither statistic and are not counted.
import sys, os, re, shlex, math, collections
A, B = sys.argv[1], sys.argv[2]
def load(p):
    d = {}; cur = None
    for line in open(p, errors='replace'):
        if line[:1] not in 'sf': continue
        try: q = shlex.split(line)
        except ValueError: continue
        if q[0] == 'scalar' and len(q) >= 4: d[(q[1], q[2])] = q[3]; cur = None
        elif q[0] == 'statistic' and len(q) >= 3: cur = (q[1], q[2])
        elif q[0] == 'field' and cur and len(q) >= 3: d[(cur[0], cur[1] + ':' + q[1])] = q[2]
    return d
UE = re.compile(r'^(.*?\.(?:ue|car)[A-Za-z0-9_]*(?:\[\d+\])?)\.')
def f(x):
    try: v = float(x); return v if math.isfinite(v) else None
    except (TypeError, ValueError): return None
acc = collections.defaultdict(list); nfiles = 0
for dp, dn, fn in os.walk(A):
    if '.git' in dp: continue
    for fname in fn:
        if not fname.endswith('.sca'): continue
        rel = os.path.relpath(os.path.join(dp, fname), A); pb = os.path.join(B, rel)
        if not os.path.exists(pb): continue
        da, db = load(os.path.join(A, rel)), load(pb)
        if da == db: continue
        nfiles += 1
        ues = {}
        for (mod, name), v in da.items():
            m = UE.match(mod + '.')
            if m: ues.setdefault(m.group(1), {}).setdefault(name, []).append((mod, v))
        for ue, stats in ues.items():
            for d in ('Dl', 'Ul'):
                sinr = [f(v) for mod, v in stats.get(f'rcvdSinr{d}:mean', []) if f(v) is not None]
                if not sinr: continue
                s = sinr[0]
                reg = '<0' if s < 0 else ('0-20' if s < 20 else '>20')
                for stat in (f'harqErrorRate_1st_{d}:mean', f'averageCqi{d}:mean'):
                    for mod, v in stats.get(stat, []):
                        a, b = f(v), f(db.get((mod, stat)))
                        if a is not None and b is not None:
                            acc[(d, stat.split(':')[0].replace('_' + d, '').replace(d, ''), reg)].append(b - a)
print(f'{nfiles} changed files')
for k in sorted(acc):
    xs = acc[k]; n = len(xs); m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float('nan')
    ci = 1.96 * sd / math.sqrt(n) if n > 1 else float('nan')
    print(f'  {k[0]} {k[1]:18s} SINR {k[2]:5s}: n={n:4d}  mean change {m:+.4f} +- {ci:.4f}  ({sum(x>0 for x in xs)} up, {sum(x<0 for x in xs)} down)')
