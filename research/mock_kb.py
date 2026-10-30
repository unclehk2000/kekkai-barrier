"""Kekkai Barrier v2 mock: session boxes, walls until taken, PDH / PD mid / PDL, sweep marks, the session card.
Values computed the way Kekkai_Barrier_Indicator.pine computes them, from 1-minute data (drawn as 5-minute candles).
python3 mock_kb.py OUTDIR SYM DAY 'HH:MM' desktop|mobile"""
import sys
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
plt.rcParams['font.family'] = 'DejaVu Sans'
OUT, SYM, DAY, HM, MODE = sys.argv[1:6]
MOB = MODE == 'mobile'
NOW = pd.Timestamp(f'{DAY} {HM}')
BG, MU, GRID, CHT = '#ffffff', '#9aa1b2', '#eef1f6', '#131722'
UPC, DNC = '#089981', '#f23645'
CB, CT, CS, CG = '#f4f6f9', '#131722', '#5d6476', '#d6dae3'       # card: Auto theme on a light chart
COL = ['#2962ff', '#f23645', '#089981', '#f9a825', '#e040fb']; NMS = ['ASIA', 'LNDN', 'NYAM', 'LUNCH', 'NYPM']
FN = ['Asia', 'London', 'NY AM', 'NY Lunch', 'NY PM']; NXN = ['LNDN', 'NYAM', 'NYPM', 'NYPM', 'ASIA']
SES = [(2000, 2400), (200, 500), (930, 1100), (1130, 1300), (1330, 1600)]
REF = [4, 0, 1, 2, 3]; HUNT = [1, 2, 4, 4, 0]
OH = [[25.3, 33.0, 41.8, 58.9, 63.5, 70.5, 77.6, 90.8], [48.3, 53.2, 65.5, 69.5, 80.8, 84.5, 90.3, 94.6], [19.8, 24.7, 33.9, 45.9, 60.3, 69.2, 80.3, 94.1],
      [31.3, 36.2, 43.8, 50.4, 62.4, 73.6, 83.4, 92.4], [11.8, 18.5, 23.9, 37.6, 44.4, 55.5, 70.4, 87.1], [14.3, 26.4, 30.8, 40.8, 51.1, 63.7, 79.2, 89.9]]
OL = [[92.0, 82.5, 67.4, 53.2, 51.1, 43.2, 32.5, 21.1], [93.8, 89.6, 81.4, 79.5, 70.4, 63.6, 55.2, 47.8], [92.0, 74.7, 66.4, 55.0, 45.0, 38.1, 26.7, 18.5],
      [93.0, 78.7, 66.4, 59.2, 50.7, 43.2, 34.4, 26.2], [83.9, 68.7, 56.3, 42.7, 33.7, 26.6, 19.7, 10.9], [89.3, 77.3, 59.8, 53.1, 45.2, 37.3, 23.5, 15.4]]
RC = [8.0, 6.0, 8.9, 7.0, 9.9]; RE = [-7.0, -6.0, -5.2, -5.5, -9.1]
lum = lambda h: 0.299 * int(h[1:3], 16) + 0.587 * int(h[3:5], 16) + 0.114 * int(h[5:7], 16)
hdrTx = lambda h: '#131722' if lum(h) > 165 else '#ffffff'
mix = lambda a, b, w: '#' + ''.join(f'{round(int(a[i:i + 2], 16) * w + int(b[i:i + 2], 16) * (1 - w)):02x}' for i in (1, 3, 5))
fmt = lambda v: f'{v:,.2f}'
hh = lambda t: f'{t:%H:%M}'
pct = lambda v: f'{round(v)}%'
ARR = lambda d: ' ▲' if d > 0 else ' ▼' if d < 0 else ''
stNm = lambda st, d: {1: 'EXPANSION', 3: 'REVERSAL', 2: 'RETRACEMENT', 0: 'CONSOLIDATION'}.get(st, '—') + (ARR(d) if st > 0 else '')
stSh = lambda st, d: {1: 'EXP', 3: 'REV', 2: 'RET', 0: 'CON'}.get(st, '—') + (ARR(d) if st > 0 else '')
stCol = lambda st, d: '#787b86' if st <= 0 else (UPC if d > 0 else DNC)


def stOf(c, rH, rL, rO, rC, fH, fL):
    if rH is None or rH != rH: return -1, 0
    m = (rH + rL) / 2
    first = 0 if fH is None and fL is None else 1 if fL is None else -1 if fH is None else (1 if fH < fL else -1 if fL < fH else 2)
    if c > rH: return 1, 1
    if c < rL: return 1, -1
    if first == 1 and c < m: return 3, -1
    if first == -1 and c > m: return 3, 1
    if rC > rO and c < m: return 2, -1
    if rC < rO and c > m: return 2, 1
    return 0, 0


octOf = lambda c, h, l: int(min(7, np.floor((c - l) / (h - l) * 8))) if h > l else 3
b = pd.read_pickle(f'/home/claude/kyw/bars_{SYM}_all.pkl')
b = b[(b.ts >= pd.Timestamp(DAY) - pd.Timedelta(days=45)) & (b.ts < NOW)].set_index('ts')
tdays = sorted(b.tday.unique())
T = pd.Timestamp(DAY)
first = lambda m: m.index[m.values][0] if m.any() else None
# every session run (history for the 20-session averages)
runs = {}
for d in tdays:
    g = b[b.tday == d]
    for k, (a, z) in enumerate(SES):
        w = g[(g.hm >= a) & (g.hm < z)]
        if not len(w): continue
        live = w.index[-1] >= NOW - pd.Timedelta(minutes=1) and ((NOW.hour * 100 + NOW.minute) < z) and d == T
        runs[(d, k)] = dict(o=w.Open.iloc[0], h=w.High.max(), l=w.Low.min(), c=w.Close.iloc[-1], t0=w.index[0], t1=w.index[-1], th=w.High.idxmax(), tl=w.Low.idxmin(), w=w, live=live, day=d)
seq = sorted(runs, key=lambda x: runs[x]['t0'])
for i, key in enumerate(seq):
    r = runs[key]; d, k = key
    prev = [x for x in seq[:i] if x[1] == REF[k]]
    if prev and not (k == 0 and (d - prev[-1][0]).days > 4):
        p = runs[prev[-1]]; r.update(rH=p['h'], rL=p['l'], rO=p['o'], rC=p['c'])
        w = r['w']; r['fH'] = first(w.High > p['h']); r['fL'] = first(w.Low < p['l'])
        r['st'], r['dr'] = stOf(r['c'], p['h'], p['l'], p['o'], p['c'], r['fH'], r['fL'])
    else:
        r['st'], r['dr'] = -1, 0
    same = [x for x in seq[:i] if x[1] == k][-20:]
    r['avg'] = np.mean([runs[x]['h'] - runs[x]['l'] for x in same]) if len(same) == 20 else None
    after = b[(b.index > r['t1'])]
    r['tkH'] = None if r['live'] else first(after.High > r['h']); r['tkL'] = None if r['live'] else first(after.Low < r['l'])
    hk = HUNT[k]; hd = d if hk > k or k != 4 else None
    nxt = [x for x in seq[i + 1:] if x[1] == hk]
    r['closed'] = bool(nxt) and not runs[nxt[0]]['live'] and runs[nxt[0]]['t1'] < NOW
latest = {k: max([x for x in seq if x[1] == k], key=lambda x: runs[x]['t0']) for k in range(5)}
# previous day (chart side) and today
dd = {d: b[b.tday == d] for d in tdays}
ti = tdays.index(T); P1, P2 = dd[tdays[ti - 1]], dd[tdays[ti - 2]]; TD = dd[T]
pdH, pdL, pdO, pdC = P1.High.max(), P1.Low.min(), P1.Open.iloc[0], P1.Close.iloc[-1]
pdSt, pdDr = stOf(pdC, P2.High.max(), P2.Low.min(), P2.Open.iloc[0], P2.Close.iloc[-1], first(P1.High > P2.High.max()), first(P1.Low < P2.Low.min()))
dfH, dfL = first(TD.High > pdH), first(TD.Low < pdL)
tdSt, tdDr = stOf(TD.Close.iloc[-1], pdH, pdL, pdO, pdC, dfH, dfL)
px = TD.Close.iloc[-1]; tL = TD.index[-1]
for k in range(5):
    r = runs[latest[k]]; print(NMS[k], r['day'].date(), 'live' if r['live'] else '', stNm(r['st'], r['dr']), fmt(r['h'] - r['l']), r['tkH'], r['tkL'], r['closed'])
print('PD', stNm(pdSt, pdDr), 'TODAY', stNm(tdSt, tdDr), dfH, dfL)

# ── chart: previous 18:00 → now, drawn as 5-minute candles
x0 = pd.Timestamp(T) - pd.Timedelta(hours=6) if not MOB else NOW - pd.Timedelta(hours=9)
c5 = b[b.index >= x0][['Open', 'High', 'Low', 'Close']].resample('5min').agg(dict(Open='first', High='max', Low='min', Close='last')).dropna()
if MOB:
    W, H, DPI, FS = 4.1, 8.6, 200, 7.0
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=BG); ax = fig.add_axes([0.0, 0.10, 0.84, 0.80])
else:
    W, H, DPI, FS = 18, 10.4, 100, 8.0
    fig = plt.figure(figsize=(W, H), dpi=DPI, facecolor=BG); ax = fig.add_axes([0.01, 0.05, 0.93, 0.86])
for sp in ax.spines.values(): sp.set_visible(False)
ax.set_facecolor(BG); ax.yaxis.tick_right(); ax.tick_params(axis='y', colors=MU, labelsize=FS - 1); ax.tick_params(axis='x', length=0); ax.grid(color=GRID, lw=0.7, zorder=0)
xs = lambda t: (t - x0).total_seconds() / 300
for t, q in c5.iterrows():
    i = xs(t); c = UPC if q.Close >= q.Open else DNC
    ax.plot([i + 0.5, i + 0.5], [q.Low, q.High], color=c, lw=0.6, zorder=4)
    ax.add_patch(Rectangle((i + 0.15, min(q.Open, q.Close)), 0.7, max(abs(q.Close - q.Open), 0.25), fc=c, ec=c, lw=0.2, zorder=5))
xe = xs(tL) + 1
lab = lambda xx, y, t, c, va='center', ha='left': ax.text(xx, y, t, color=c, fontsize=FS - 1.6, va=va, ha=ha, clip_on=True, zorder=8)
for key in seq:
    r = runs[key]; d, k = key
    if r['t1'] < x0: continue
    c = COL[k]; a, z = xs(r['t0']), xs(r['t1']) + 1
    ax.add_patch(Rectangle((a, r['l']), z - a, r['h'] - r['l'], fc=c, alpha=0.18, ec=mix(c, '#ffffff', 0.6), lw=1, zorder=2))
    lab(a, r['h'], ' ' + NMS[k] + ' · ' + stNm(r['st'], r['dr']) + (' …' if r['live'] else ''), c, va='bottom')
    if not r['live']:   # walls until taken
        for y, t0, tk, nm in ((r['h'], r['th'], r['tkH'], 'High'), (r['l'], r['tl'], r['tkL'], 'Low')):
            if t0 < x0: continue
            e = xs(tk) + 0.5 if tk is not None else xe
            ax.plot([xs(t0) + 0.5, e], [y, y], color=c, lw=1, zorder=3); lab(e + 0.3, y, f'{NMS[k]} {nm}', c)
# PDH / PD mid / PDL (from the extreme's candle, run to the last candle; dashed once taken)
pt = lambda t: max(xs(t), 0)
for y, t0, nm, tk in ((pdH, P1.High.idxmax(), 'PDH', dfH), ((pdH + pdL) / 2, min(P1.High.idxmax(), P1.Low.idxmin()), 'PDM', None), (pdL, P1.Low.idxmin(), 'PDL', dfL)):
    ax.plot([pt(t0), xe], [y, y], color='#2962ff' if nm != 'PDM' else '#6f8ff9', lw=1, ls=':' if nm == 'PDM' else ('--' if tk is not None else '-'), zorder=3)
    lab(xe + 0.3, y, f'{P1.index[0] + pd.Timedelta(hours=6):%m/%d} {nm}', '#2962ff')
# sweep marks: Asia walls in London, London walls in NY AM, Lunch walls in NY PM; PDH / PDL
def mark(t, y, txt, c, up):
    ax.annotate(txt, (xs(t) + 0.5, y), xytext=(0, 8 if up else -8), textcoords='offset points', fontsize=FS - 2, ha='center', va='bottom' if up else 'top', color=CHT, bbox=dict(fc=c, alpha=0.2, ec='none', boxstyle='round,pad=0.25'), zorder=9, annotation_clip=True)
for hk, kk, nm in ((1, 0, 'Asia'), (2, 1, 'London'), (4, 3, 'Lunch')):
    keyH = (T, hk)
    if keyH in runs and kk in latest:
        src = runs[(T, kk)] if (T, kk) in runs and not runs[(T, kk)]['live'] else None
        if src is None: continue
        w = runs[keyH]['w']
        for y, side, up in ((src['h'], 'H', True), (src['l'], 'L', False)):
            t = first(w.High > y) if up else first(w.Low < y)
            if t is not None: mark(t, w.loc[t, 'High'] if up else w.loc[t, 'Low'], f'{nm} {side} swept {hh(t)}', COL[kk], up)
sess_of = lambda t: next((' · ' + FN[k] for k, (a, z) in enumerate(SES) if a <= t.hour * 100 + t.minute < z), '')
for y, t, nm, up in ((pdH, dfH, 'PDH', True), (pdL, dfL, 'PDL', False)):
    if t is not None: mark(t, TD.loc[t, 'High'] if up else TD.loc[t, 'Low'], f'{nm} swept {hh(t)}{sess_of(t)}', '#2962ff', up)
ticks = [xs(t) for t in c5.index if t.minute == 0 and t.hour % (3 if not MOB else 3) == 0]
ax.set_xticks(ticks); ax.set_xticklabels([f'{(x0 + pd.Timedelta(minutes=300 * v / 60 * 1)):%H:%M}' for v in ticks], color=MU, fontsize=FS - 1)
ax.set_xticklabels([hh(x0 + pd.Timedelta(seconds=300 * v)) for v in ticks])
vis = b[b.index >= x0]; lo, hi = min(vis.Low.min(), pdL), max(vis.High.max(), pdH)
ax.set_xlim(-1, xe / (0.62 if MOB else 0.72)); ax.set_ylim(lo - (hi - lo) * 0.05, hi + (hi - lo) * 0.05)
fig.canvas.draw(); bb = ax.get_window_extent()

# ── the card (Pine table: columns sized to their text, top right, 6 px in)
lst = max([k for k in range(5) if not runs[latest[k]]['live']], key=lambda k: runs[latest[k]]['t1'])
act = next((k for k in range(5) if runs[latest[k]]['live']), -1)
ps = runs[latest[act]] if act >= 0 else runs[latest[lst]]
pill = (stSh if MOB else stNm)(ps['st'], ps['dr']) + (' …' if act >= 0 else ''); pc = stCol(ps['st'], ps['dr'])
where = (NMS[act] + ('' if MOB else ' live')) if act >= 0 else (('' if MOB else 'after ') + NMS[lst])
rows = []   # (cells, colours, backgrounds)
nc = 4 if MOB else 5
hdr = ['', 'STATE', 'HIGH', 'LOW'] if MOB else ['', 'RANGE', 'STATE', 'HIGH', 'LOW']
rows.append((hdr, [CS] * nc, [CB] * nc))
for k in range(5):
    r = runs[latest[k]]; c = COL[k]; stale = r['day'] < T and not r['live']
    o = octOf(r['c'], r['h'], r['l']); rng = r['h'] - r['l']
    cells, cols, bgs = [NMS[k]], [hdrTx(c)], [mix(c, CB, 0.55) if stale else c]
    if not MOB:
        big = (not r['live']) and r['avg'] is not None and rng >= r['avg']
        cells.append(fmt(rng) + (' …' if r['live'] else '')); cols.append(CT); bgs.append(mix(c, CB, 0.30) if big else CB)
    cells.append((stSh if MOB else stNm)(r['st'], r['dr']) + (' …' if r['live'] else '')); cols.append(stCol(r['st'], r['dr'])); bgs.append(CB)
    for hi_, tk, tab in ((True, r['tkH'], OH), (False, r['tkL'], OL)):
        if r['live']: v, vc, vb = '—', CT, CB
        elif tk is not None: v, vc, vb = '✓ ' + hh(tk), CT, mix(c, CB, 0.35)
        elif r['closed']: v, vc, vb = '✗', CS, CB
        else: v, vc, vb = pct(tab[k][o]), CT, CB
        cells.append(v); cols.append(vc); bgs.append(vb)
    rows.append((cells, cols, bgs))
oP = octOf(pdC, pdH, pdL)
cells, cols, bgs = ['PD'], ['#ffffff'], ['#2196f3']
if not MOB: cells.append(fmt(pdH - pdL)); cols.append(CT); bgs.append(CB)
cells.append((stSh if MOB else stNm)(pdSt, pdDr)); cols.append(stCol(pdSt, pdDr)); bgs.append(CB)
for tk, tab in ((dfH, OH), (dfL, OL)):
    cells.append('✓ ' + hh(tk) if tk is not None else pct(tab[5][oP])); cols.append(CT); bgs.append(mix('#2196f3', CB, 0.35) if tk is not None else CB)
rows.append((cells, cols, bgs))
if not MOB:
    rows.append((['TODAY', fmt(TD.High.max() - TD.Low.min()) + ' …', stNm(tdSt, tdDr) + ' …', '', ''], [CT, CT, stCol(tdSt, tdDr), CT, CT], [mix('#787b86', CB, 0.4), CB, CB, CB, CB]))
lsr = runs[latest[lst]]; ef = RC[lst] if lsr['st'] == 0 else RE[lst] if lsr['st'] == 1 else None
efT = ('no read' if MOB else 'no tested range read') if ef is None else NXN[lst] + (' ' if MOB else ' range ') + ('+' if ef > 0 else '−') + f'{abs(ef):.0f}%'
read = NMS[lst] + ' ' + (stSh if MOB else stNm)(lsr['st'], lsr['dr']) + ' → ' + efT
px_pt = DPI / 72; cw = 0.602 * FS * px_pt; lh = 1.9 * FS * px_pt; pad = 1.2 * cw
head = ['KEKKAI' if MOB else '◆ KEKKAI', where + ' · ' + hh(tL) + ('' if MOB else ' ET'), pill]
ws = [max(len(r_[0][j]) for r_ in rows) * cw + pad for j in range(nc)]
ws[0] = max(ws[0], len(head[0]) * cw + pad, len('READ') * cw + pad)
need1 = len(head[1]) * cw + pad; span1 = ws[1] + (0 if MOB else ws[2])
if need1 > span1: ws[1] += need1 - span1
needP = len(pill) * cw + pad; spanP = ws[nc - 2] + ws[nc - 1]
if needP > spanP: ws[nc - 1] += needP - spanP
needR = len(read) * cw + pad; spanR = sum(ws[1:])
if needR > spanR: ws[nc - 1] += needR - spanR
Wt = sum(ws); Ht = lh * (len(rows) + 2)
xL = bb.x1 - 6 - Wt; yT = bb.y1 - 6
Tf = fig.transFigure.inverted()
def rect(x_, y_, w_, h_, fc, ec=CG):
    (a0, b0), (a1, b1) = Tf.transform([(x_, y_), (x_ + w_, y_ + h_)])
    fig.patches.append(Rectangle((a0, b0), a1 - a0, b1 - b0, transform=fig.transFigure, fc=fc, ec=ec, lw=0.8, zorder=10))
def txt(x_, y_, s_, c, ha='left'):
    a0, b0 = Tf.transform((x_, y_)); fig.text(a0, b0, s_, family='DejaVu Sans Mono', fontsize=FS, va='center', ha=ha, color=c, zorder=12)
# header: title | where (spans 1–2 on desktop) | pill (spans the last two)
y = yT - lh
rect(xL, y, ws[0], lh, CB); txt(xL + 4, y + lh / 2, head[0], CT)
w1 = ws[1] if MOB else ws[1] + ws[2]
rect(xL + ws[0], y, w1, lh, CB); txt(xL + ws[0] + 4, y + lh / 2, head[1], CT)
xp = xL + ws[0] + w1; wp = Wt - ws[0] - w1
rect(xp, y, wp, lh, pc); txt(xp + wp / 2, y + lh / 2, pill, hdrTx(pc), ha='center')
for i, (cells, cols, bgs) in enumerate(rows):
    y = yT - lh * (i + 2); xx = xL
    for j in range(nc):
        rect(xx, y, ws[j], lh, bgs[j])
        left = j == 0 or (j == (1 if MOB else 2))
        txt(xx + 4 if left else xx + ws[j] - 4, y + lh / 2, cells[j], cols[j], ha='left' if left else 'right')
        xx += ws[j]
y = yT - lh * (len(rows) + 2)
rect(xL, y, ws[0], lh, CB); txt(xL + 4, y + lh / 2, 'READ', CS)
rect(xL + ws[0], y, Wt - ws[0], lh, CB); txt(xL + ws[0] + 4, y + lh / 2, read, CT)
print('card', round(Wt), 'x', round(Ht + lh), 'px =', round(100 * Wt / bb.width), '% of the pane width')
if MOB:
    fig.text(0.04, 0.965, f'{SYM}1! · 1m', color=CHT, fontsize=9, weight='bold'); fig.text(0.04, 0.94, f'Kekkai Barrier · Layout: Mobile · {NOW:%a %-d %b %H:%M} ET', color=CS, fontsize=6.4)
    fig.text(0.04, 0.03, 'Mock-up from 1-minute data (drawn as 5-minute candles). TradingView will differ.', color=CS, fontsize=5.6)
else:
    fig.text(0.01, 0.955, f'Kekkai Barrier · session boxes, walls and price delivery · {SYM} 1-minute, {NOW:%a %-d %b %Y %H:%M} ET', color=CHT, fontsize=13, weight='bold')
    fig.text(0.01, 0.928, 'Boxes with each session\'s state against the one before it; walls run until taken; PDH / PD mid / PDL; the card top right. Mock-up from 1-minute data, drawn as 5-minute candles; TradingView will differ.', color=CS, fontsize=9)
f = f'{OUT}/Kekkai_{MODE}_{SYM}_{DAY}_{NOW:%H%M}.png'; plt.savefig(f, dpi=DPI, facecolor=BG); plt.close(fig); print('saved', f, '| READ:', read)
