"""Kekkai v2 research, step 1: session OHLC per trading day (ET): Asia 20:00-23:59, London 02:00-04:59, NY AM 09:30-10:59,
Lunch 11:30-12:59, NY PM 13:30-15:59; with the minute of each extreme, and the extremes of the windows that follow,
for 'taken by' outcomes. NQ / ES / RTY 1-minute 2018-26."""
import numpy as np, pandas as pd
S = dict(A=(2000, 2400), L=(200, 500), N=(930, 1100), U=(1130, 1300), P=(1330, 1600))
rows = []
for sym in ('NQ', 'ES', 'RTY'):
    b = pd.read_pickle(f'/home/claude/kyw/bars_{sym}_all.pkl')[['ts', 'Open', 'High', 'Low', 'Close', 'tday', 'hm', 'Contract']].reset_index(drop=True)
    O, H, L, C, hm, td = (b[c].to_numpy() for c in ('Open', 'High', 'Low', 'Close', 'hm', 'tday'))
    ct = b.Contract.to_numpy()
    ds = np.r_[0, np.flatnonzero(td[1:] != td[:-1]) + 1]; de = np.r_[ds[1:], len(b)]
    for s, e in zip(ds, de):
        h = hm[s:e]; o = dict(sym=sym, day=pd.Timestamp(td[s]), contract=ct[e - 1])
        if len(np.unique(ct[s:e])) > 1: o['roll'] = True
        ok = True
        for k, (a, z) in S.items():
            w = np.flatnonzero((h >= a) & (h < z)) + s
            if len(w) < 0.8 * ((z // 100 - a // 100) * 60 + (z % 100 - a % 100)):
                ok = False; break
            hh, ll = H[w], L[w]
            o.update({f'{k}o': O[w[0]], f'{k}h': hh.max(), f'{k}l': ll.min(), f'{k}c': C[w[-1]],
                      f'{k}th': int(h[w[hh.argmax()] - s]), f'{k}tl': int(h[w[ll.argmin()] - s]), f'{k}i0': w[0], f'{k}i1': w[-1]})
        if not ok: continue
        o['i0'], o['i1'] = s, e - 1
        rows.append(o)
    print(sym, len(rows))
D = pd.DataFrame(rows); D.to_pickle('sess.pkl'); print(D.shape)
