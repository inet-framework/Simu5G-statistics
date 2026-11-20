# Prints the key statistics of every UE module (cellular NIC, apps) that differ between two
# statistics trees, for the files matching a regex: SINR, CQI, HARQ error rates, delays, frame loss,
# throughput, distance, received packets.
#
#   python3 uestats.py <dirA> <dirB> <file regex>
import sys, os, re, shlex
A, B, rx = sys.argv[1], sys.argv[2], re.compile(sys.argv[3])
KEYS = ['rcvdSinrDl:mean','averageCqiDl:mean','harqErrorRate_1st_Dl:mean','harqErrorRateDl:mean','macDelayDl:mean',
        'voipFrameLoss:mean','voipFrameDelay:mean','voipReceivedThroughput:mean','cbrFrameLoss:mean','cbrFrameDelay:mean','cbrReceivedThroughput:mean',
        'distance:mean','packetReceived:count']
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
for dp, dn, fn in os.walk(A):
    if '.git' in dp: continue
    for f in sorted(fn):
        rel = os.path.relpath(os.path.join(dp, f), A)
        if not f.endswith('.sca') or not rx.search(rel): continue
        da, db = load(os.path.join(A, rel)), load(os.path.join(B, rel))
        print('==', rel)
        for (mod, name), va in sorted(da.items()):
            if name in KEYS and '.ue' in mod and da.get((mod, name)) != db.get((mod, name)) and va != 'nan':
                print(f'   {mod.split(".",1)[1][:45]:45s} {name:28s} {va:>14s} -> {db.get((mod,name),"-"):>14s}')
