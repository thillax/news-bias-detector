import json
import glob
from collections import defaultdict
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

all_articles = []
for file in sorted(glob.glob('collected_articles/*.json')):
    with open(file, 'r', encoding='utf-8') as f:
        all_articles.extend(json.load(f))

print(f"Loaded: {len(all_articles)} articles")

def get_sentiment(text):
    if not text or len(text.strip()) < 5:
        return 'neutral'
    scores = analyzer.polarity_scores(text[:500])
    c = scores['compound']
    if c >= 0.05:    return 'positive'
    elif c <= -0.05: return 'negative'
    else:            return 'neutral'

# Group by date
date_sentiment = defaultdict(lambda: {'positive':0,'neutral':0,'negative':0,'total':0})

for a in all_articles:
    pub = a.get('published_date','')
    if not pub:
        continue
    try:
        date = str(pub)[:10]  # YYYY-MM-DD
        content = a.get('content','') or a.get('title','') or ''
        sent = get_sentiment(content)
        date_sentiment[date][sent] += 1
        date_sentiment[date]['total'] += 1
    except:
        continue

# Sort by date
sorted_dates = sorted(date_sentiment.keys())

print(f"\nDate range: {sorted_dates[0]} to {sorted_dates[-1]}")
print(f"Total dates: {len(sorted_dates)}")

print("\n📌 Sentiment Trends by Date:")
print(f"{'Date':<12} {'Total':>6} {'Pos%':>6} {'Neu%':>6} {'Neg%':>6}")
print("-"*45)

trends = []
for date in sorted_dates:
    d = date_sentiment[date]
    total = d['total']
    if total == 0:
        continue
    pos_pct = round(d['positive']/total*100,1)
    neu_pct = round(d['neutral']/total*100,1)
    neg_pct = round(d['negative']/total*100,1)
    print(f"{date:<12} {total:>6} {pos_pct:>5}% {neu_pct:>5}% {neg_pct:>5}%")
    trends.append({
        'date': date,
        'total': total,
        'positive': d['positive'],
        'neutral': d['neutral'],
        'negative': d['negative'],
        'pos_pct': pos_pct,
        'neu_pct': neu_pct,
        'neg_pct': neg_pct
    })

# Save
with open('sentiment_trends.json','w',encoding='utf-8') as f:
    json.dump(trends, f, indent=2)

print(f"\n✅ Saved to sentiment_trends.json!")
print(f"✅ {len(trends)} dates processed!")
