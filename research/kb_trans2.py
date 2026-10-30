"""Range read after each state, all five session pairs incl. NY PM -> next Asia; effect as % (own range held)."""
import sys, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/gh2/stats-kit'); from stats_kit import check, table
X = pd.read_pickle('states2.pkl').reset_index(drop=True).sort_values(['sym', 'k', 'day'])
X['avg'] = X.groupby(['sym', 'k']).rng.transform(lambda s: s.shift(1).rolling(20).mean()); X['rr'] = X.rng / X.avg
Y = X.set_index(['sym', 'day', 'k'])
days = {s: sorted(X[X.sym == s].day.unique()) for s in ('NQ', 'ES', 'RTY')}
nxd = {s: dict(zip(d[:-1], d[1:])) for s, d in days.items()}
nx = dict(A='L', L='N', N='P', U='P', P='A')
pairs = []
for r in X.itertuples():
    nk = nx[r.k]; dd = r.day
    if r.k == 'P':
        dd = nxd[r.sym].get(r.day)
        if dd is None or (dd - r.day).days > 4: continue
    key = (r.sym, dd, nk)
    if key in Y.index:
        n = Y.loc[key]; pairs.append(dict(sym=r.sym, day=r.day, k=r.k, st=r.st, rr=r.rr, nrr=n.rr, half=r.half))
Pq = pd.DataFrame(pairs).dropna(); Pq['date'] = Pq.day; Pq = Pq.set_index('date'); Pq['lnr'] = np.log(Pq.nrr); Pq['lr'] = np.log(Pq.rr)
rows = []
for k in 'ALNUP':
    for s_ in ('CON', 'EXP', 'RET', 'REV'):
        g = Pq[Pq.k == k].assign(isk=lambda d: (d.st == s_).astype(float))
        r = check(g, 'lnr ~ isk + lr', 'isk', test=f'{k}->{nx[k]} {s_}'); r['pct'] = round(100 * (np.exp(r['coef']) - 1), 1); rows.append(r)
print(table(rows)[['pct', 'p', 'n', '18-24', '25-26', 'ES', 'NQ', 'RTY', 'ok']].to_string())
