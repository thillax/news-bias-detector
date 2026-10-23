import sqlite3, json, re, math
from collections import defaultdict
from datetime import date
from statistics import mean
from scipy import stats

MIN_N, MIN_DIFF, ALPHA, MAX_GAP = 5, 0.10, 0.05, 7

conn = sqlite3.connect('news_bias_new.db')
rows = conn.execute("SELECT title, source, published_date, polarity FROM articles").fetchall()
conn.close()

def parse_day(s):
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(s or ''))
    if not m:
        return None
    try:
        return date(int(m[1]), int(m[2]), int(m[3]))
    except ValueError:
        return None

def welch(a, b):
    if len(a) < 2 or len(b) < 2:
        return 1.0
    p = stats.ttest_ind(b, a, equal_var=False)[1]
    return 1.0 if math.isnan(p) else float(p)

seen, by = set(), defaultdict(lambda: defaultdict(list))
for title, src, pub, pol in rows:
    k = (title or '').strip().lower()
    d = parse_day(pub)
    if not k or k in seen or d is None or pol is None:
        continue
    seen.add(k)
    by[src][d].append(float(pol))
    by['ALL'][d].append(float(pol))
print('unique articles with usable date:', len(seen))

series, shifts = {}, []
for src, days in by.items():
    good = sorted(d for d, v in days.items() if len(v) >= MIN_N)
    series[src] = [{'date': d.isoformat(), 'n': len(days[d]),
                    'mean': round(mean(days[d]), 3)} for d in good]
    for prev, cur in zip(good, good[1:]):
        gap = (cur - prev).days
        diff = mean(days[cur]) - mean(days[prev])
        p = welch(days[prev], days[cur])
        if gap <= MAX_GAP:
            shifts.append({'source': src, 'from': prev.isoformat(), 'to': cur.isoformat(),
                           'change': round(diff, 3), 'p': round(p, 4),
                           'direction': 'more positive' if diff > 0 else 'more negative', 'n_from': len(days[prev]), 'n_to': len(days[cur]), 'significant': bool(abs(diff) >= MIN_DIFF and p < ALPHA)})

srcs = [s for s in by if s != 'ALL']
gaps = []
for d in sorted({d for s in srcs for d in by[s]}):
    ok = [s for s in srcs if len(by[s].get(d, [])) >= MIN_N]
    for i in range(len(ok)):
        for j in range(i + 1, len(ok)):
            a, b = by[ok[i]][d], by[ok[j]][d]
            diff, p = mean(b) - mean(a), welch(a, b)
            if abs(diff) >= MIN_DIFF and p < ALPHA:
                gaps.append({'date': d.isoformat(), 'a': ok[i], 'b': ok[j],
                             'diff': round(diff, 3), 'p': round(p, 4)})

out = {'params': {'min_n': MIN_N, 'min_diff': MIN_DIFF, 'alpha': ALPHA, 'max_gap_days': MAX_GAP},
       'series': series, 'shifts': shifts, 'source_gaps': gaps}
json.dump(out, open('sentiment_shifts.json', 'w', encoding='utf-8'), indent=2)

print('\nSERIES (days with >=%d articles):' % MIN_N)
for s, pts in series.items():
    print(' ', s, [(p['date'], p['n'], p['mean']) for p in pts])
print('\nDAY-TO-DAY MOVES:', len(shifts), '| significant:', sum(x['significant'] for x in shifts))
for x in shifts:
    print(' ', x)
print('\nSOURCE GAPS (same day):', len(gaps))
for x in gaps[:15]:
    print(' ', x)
