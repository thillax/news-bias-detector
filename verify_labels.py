import csv, random, json
from sklearn.metrics import cohen_kappa_score
rows = [r for r in csv.DictReader(open('label_me.csv', encoding='utf-8-sig')) if r['sentiment'].strip()]
random.seed(7)
sample = random.sample(rows, 40)
M = {'1': 'positive', '2': 'neutral', '3': 'negative'}
mine, theirs = [], []
for i, r in enumerate(sample, 1):
    print('\n[%d/40] %s' % (i, r['source']))
    print(r['title'])
    if r['snippet']:
        print('   ' + r['snippet'][:200])
    s = ''
    while s not in M:
        s = input('your sentiment 1=positive 2=neutral 3=negative > ').strip()
    mine.append(M[s]); theirs.append(r['sentiment'].strip())
agree = sum(a == b for a, b in zip(mine, theirs)) / 40
kappa = cohen_kappa_score(mine, theirs)
print('\nagreement: %.0f%%   Cohen kappa: %.2f' % (agree * 100, kappa))
json.dump({'n_verified': 40, 'agreement': round(agree, 3), 'kappa': round(kappa, 3)}, open('verify_results.json', 'w'), indent=2)
