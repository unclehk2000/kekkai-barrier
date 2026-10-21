# Kekkai Barrier

**Session walls, sweeps and shifts, with day / week / month levels**

TradingView indicator, Pine Script v6. Open source under the Mozilla Public License 2.0.

**Kekkai Barrier** draws each session's walls, the sweeps of those walls, and the structural shifts that follow.

*A confluence map: it draws walls, sweeps and shifts. The Model 4 trade statistics did not survive a re-test, so the indicator makes no trade calls.*

## What it draws

**Session walls:** each session builds the walls the next one hunts. Times are ET and every session is a setting.

| Session | Default time | Role |
|---|---|---|
| Asia | 20:00–00:00 | builds London's walls |
| London | 02:00–05:00 | hunts Asia's walls |
| NY AM | 09:30–11:00 | hunts London's walls |
| NY Lunch | 11:30–13:00 | builds NY PM's walls |
| NY PM | 13:30–16:00 | hunts Lunch's walls |

- Walls run to the last candle, or until their hunt session ends.
- Optional wall midpoints.
- A **compression flag** when a session's range is under 75% of its own 20-session average.

**Day, week and month levels** (exchange day, 18:00 ET start):
- PDH / PDL;
- each day's high / low this week;
- today's high / low so far;
- week and month to date;
- previous week and month.

**Sweeps** are marked on:
- session walls;
- PDH / PDL;
- earlier days this week;
- the previous week and month.

**Shifts:** two consecutive 30-minute blocks (the length is a setting) printing a higher high and higher low (bull), or a lower low and lower high (bear). Each is marked with the sweep that came before it.

**Day-of-week labels** run along the bottom.

## Settings

**View** sits at the top:
- theme;
- text size and colour;
- label date format;
- wall length;
- days to keep;
- how older days fade.

## Credits

- Concepts: ICT (Michael J. Huddleston).
- Written from scratch.

## Add it to TradingView

1. In TradingView, open the **Pine Editor** (bottom panel).
2. Copy the contents of `Kekkai_Barrier_Indicator.pine` into a new script.
3. **Save**, then **Add to chart**.

## License

Mozilla Public License 2.0, see [LICENSE](LICENSE). © Unclehk2000.

*Historical frequencies, not guarantees. Nothing here is financial advice.*
