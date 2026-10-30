"""Kekkai v2: odds the next session takes a session's high / low, by where the session closed in its own range (octant).
Also the previous exchange day (18:00-16:59): PDH / PDL taken today by 16:59, by where the day closed in its range."""
import sys, json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/gh2/stats-kit'); from stats_kit import check, table
X = pd.read_pickle('states2.pkl')
# previous day rows
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['High', 'Low', 'Close', 'Open', 'tday', 'Contract']]
    g = b.groupby('tday').agg(o=('Open', 'first'), h=('High', 'max'), l=('Low', 'min'), c=('Close', 'last'), ct=('Contract', 'last'), n=('Close', 'size'))
    g = g[g.n >= 1000]
    for i in range(2, len(g)):
        p2, p, t = g.iloc[i - 2], g.iloc[i - 1], g.iloc[i]
        if (g.index[i] - g.index[i - 1]).days > 4 or p.ct != t.ct or p2.ct != p.ct: continue
        PM = (p2.h + p2.l) / 2
        rows.append(dict(sym=sym, day=g.index[i], k='D', pos=(p.c - p.l) / (p.h - p.l), y_h=float(t.h > p.h), y_l=float(t.l < p.l),
                         st='EXP' if (p.c > p2.h or p.c < p2.l) else 'X', rng=p.h - p.l))
PDx = pd.DataFrame(rows); PDx['half'] = np.where(PDx.day.dt.year >= 2025, '25-26', '18-24'); PDx['date'] = PDx.day; PDx = PDx.set_index('date')
X = pd.concat([X[['sym', 'day', 'k', 'pos', 'y_h', 'y_l', 'half', 'st', 'dr']], PDx[['sym', 'day', 'k', 'pos', 'y_h', 'y_l', 'half']]])
X['oct'] = np.minimum(7, np.floor(X.pos * 8)).astype(int)
out, rr = {}, []
for k in 'ALNUPD':
    g = X[X.k == k]
    t = g.groupby('oct')[['y_h', 'y_l']].mean() * 100
    t2 = g[g.half == '25-26'].groupby('oct')[['y_h', 'y_l']].mean() * 100
    print(f'== {k}  n {len(g)}  base H {100 * g.y_h.mean():.1f}  L {100 * g.y_l.mean():.1f}')
    print(pd.concat([t.round(1), t2.round(1).add_suffix('_2526'), g.groupby('oct').size().rename('n')], axis=1).T.to_string())
    out[k] = dict(h=t.y_h.round(1).tolist(), l=t.y_l.round(1).tolist(), bh=round(100 * g.y_h.mean(), 1), bl=round(100 * g.y_l.mean(), 1), n=len(g))
    g = g.assign(c=g.pos - 0.5)
    rr += [check(g, 'y_h ~ c', 'c', test=f'{k} high taken ~ close position'), check(g, 'y_l ~ c', 'c', test=f'{k} low taken ~ close position')]
print(table(rr)[['coef', 'p', 'n', '18-24', '25-26', 'ES', 'NQ', 'RTY', 'ok']].to_string())
json.dump(out, open('oct.json', 'w'), indent=1)
