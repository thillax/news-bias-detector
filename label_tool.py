import csv
FILE = 'label_me.csv'
FIELDS = ['id', 'source', 'title', 'snippet', 'sentiment', 'tone']
SM = {'1': 'positive', '2': 'neutral', '3': 'negative'}
TM = {'': 'neutral', 'e': 'emotional', 'l': 'loaded'}

rows = list(csv.DictReader(open(FILE, encoding='utf-8-sig')))

def save():
    with open(FILE, 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

todo = [r for r in rows if not (r['sentiment'].strip() and r['tone'].strip())]
print(len(todo), 'rows left. Type q any time to quit (progress is saved).')

done_now = 0
for r in todo:
    print('\n[' + r['id'] + '] ' + r['source'])
    print(r['title'])
    if r['snippet']:
        print('   ' + r['snippet'][:200])
    s = ''
    while s not in SM and s != 'q':
        s = input('sentiment  1=positive 2=neutral 3=negative q=quit > ').strip().lower()
    if s == 'q':
        break
    t = None
    while t not in TM and t != 'q':
        t = input('tone  Enter=neutral e=emotional l=loaded q=quit > ').strip().lower()
    if t == 'q':
        break
    r['sentiment'] = SM[s]
    r['tone'] = TM[t]
    save()
    done_now += 1

print('\nlabelled this session:', done_now)
