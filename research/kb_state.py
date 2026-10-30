"""Kekkai v2 research, step 2: the price-delivery state of each session against the session before it, and what follows.
State of session S against its reference P (P's high PH, low PL, mid PM, open Po, close Pc):
  EXPANSION   S closes beyond P's high (▲) or low (▼)
  REVERSAL    S takes one side of P first, then closes back inside P past PM, away from that side
  RETRACEMENT S closes inside P, on the other side of PM from P's own direction (P up -> S closes below PM)
  CONSOLIDATION everything else (closes inside P on the side of P's direction, swept or not)
Outcomes: S's high / low taken from S's end to the end of the next session (the hunter), the hunter's direction."""
import numpy as np, pandas as pd, sys
D = pd.read_pickle('sess.pkl')
REF = dict(A='P-1', L='A', N='L', U='N', P=sys.argv[1] if len(sys.argv) > 1 else 'U')
NXT = dict(A='L', L='N', N='P', U='P', P='A+1')
out = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['Open', 'High', 'Low', 'Close']]
    H, L, C = b.High.to_numpy(), b.Low.to_numpy(), b.Close.to_numpy()
    d = D[D.sym == sym].sort_values('day').reset_index(drop=True)
    for i, r in d.iterrows():
        pv = d.iloc[i - 1] if i > 0 and (r.day - d.day[i - 1]).days <= 4 else None
        nx = d.iloc[i + 1] if i + 1 < len(d) and (d.day[i + 1] - r.day).days <= 4 else None
        for k in 'ALNUP':
            rf = REF[k]
            if rf == 'P-1':
                if pv is None or pv.contract != r.contract: continue
                PH, PL, Po, Pc = pv.Ph, pv.Pl, pv.Po, pv.Pc
            else:
                PH, PL, Po, Pc = r[rf + 'h'], r[rf + 'l'], r[rf + 'o'], r[rf + 'c']
            i0, i1 = int(r[k + 'i0']), int(r[k + 'i1'])
            hh, ll = H[i0:i1 + 1], L[i0:i1 + 1]
            c = C[i1]; PM = (PH + PL) / 2
            fh = np.flatnonzero(hh > PH); fl = np.flatnonzero(ll < PL)
            th = fh[0] if len(fh) else 10 ** 9; tl = fl[0] if len(fl) else 10 ** 9
            first = 0 if th == tl == 10 ** 9 else (1 if th < tl else -1 if tl < th else 2)
            dP = np.sign(Pc - Po)
            if c > PH: st, dr = 'EXP', 1
            elif c < PL: st, dr = 'EXP', -1
            elif first == 1 and c < PM: st, dr = 'REV', -1
            elif first == -1 and c > PM: st, dr = 'REV', 1
            elif dP > 0 and c < PM: st, dr = 'RET', -1
            elif dP < 0 and c > PM: st, dr = 'RET', 1
            else: st, dr = 'CON', 0
            nk = NXT[k]
            if nk == 'A+1':
                if nx is None or nx.contract != r.contract: continue
                j1 = int(nx.Ai1); No, Nc = nx.Ao, nx.Ac
            else:
                j1 = int(r[nk + 'i1']); No, Nc = r[nk + 'o'], r[nk + 'c']
            sH, sL = hh.max(), ll.min()
            hT = bool((H[i1 + 1:j1 + 1] > sH).any()); lT = bool((L[i1 + 1:j1 + 1] < sL).any())
            out.append(dict(sym=sym, day=r.day, k=k, st=st, dr=dr, first=first, took=int(th < 10 ** 9) + int(tl < 10 ** 9),
                            rng=sH - sL, pr=PH - PL, hT=hT, lT=lT, ndir=np.sign(Nc - No), mv=np.sign(C[j1] - c)))
X = pd.DataFrame(out); X['half'] = np.where(X.day.dt.year >= 2025, '25-26', '18-24'); X.to_pickle('states.pkl')
print(X.shape)
print(pd.crosstab(X.k, X.st, normalize='index').round(3))
print(pd.crosstab([X.k, X.st], X.dr).head(40))
