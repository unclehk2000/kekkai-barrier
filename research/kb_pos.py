"""Does the state add anything to where the session closed in its own range? hT/lT ~ pos (+ state)."""
import sys, numpy as np, pandas as pd, statsmodels.formula.api as smf, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '/home/claude/gh2/stats-kit'); from stats_kit import check, table
X = pd.read_pickle('states.pkl'); D = pd.read_pickle('sess.pkl')
D = D.set_index(['sym', 'day'])
pos = []
for r in X.itertuples():
    d = D.loc[(r.sym, r.day)]
    h, l, c = d[r.k + 'h'], d[r.k + 'l'], d[r.k + 'c']
    pos.append((c - l) / (h - l) if h > l else 0.5)
X['pos'] = pos; X['date'] = X.day; X = X.set_index('date')
X['y_h'] = X.hT.astype(float); X['y_l'] = X.lT.astype(float)
X['sd'] = X.st + np.where(X.dr > 0, 'u', np.where(X.dr < 0, 'd', ''))
X.to_pickle('states2.pkl')
cols = ['coef', 'p', 'n', '18-24', '25-26', 'ES', 'NQ', 'RTY', 'ok']
rows = []
for k in 'ALNUP':
    g = X[X.k == k]
    tr, te = g[g.half == '18-24'], g[g.half == '25-26'].copy()
    for y in ('y_h', 'y_l'):
        b0 = np.mean((te[y] - tr[y].mean()) ** 2)
        m1 = smf.logit(f'{y} ~ pos', tr).fit(disp=0); p1 = np.mean((m1.predict(te) - te[y]) ** 2)
        m2 = smf.logit(f'{y} ~ pos + C(sd)', tr).fit(disp=0); p2 = np.mean((m2.predict(te) - te[y]) ** 2)
        print(f'{k} {y}: base {b0:.4f}  pos {p1:.4f}  pos+state {p2:.4f}')
    for s_ in ('EXPu', 'EXPd', 'REVu', 'REVd', 'RETu', 'RETd'):
        gg = g.assign(isS=(g.sd == s_).astype(float))
        for y in ('y_h', 'y_l'):
            rows.append(check(gg, f'{y} ~ pos + isS', 'isS', test=f'{k} {y} | {s_} beyond close position'))
T = table(rows)[cols]
print(T[T.ok == '✓'].to_string()); print(len(T), 'tests,', (T.ok == '✓').sum(), 'pass')
