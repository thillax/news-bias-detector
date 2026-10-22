import json
import glob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Load all articles
all_articles = []
for file in sorted(glob.glob('collected_articles/*.json')):
    with open(file, 'r', encoding='utf-8') as f:
        all_articles.extend(json.load(f))

print(f"Loaded: {len(all_articles)} articles")

# Topics to compare
TOPICS = {
    'AI/Technology': ['ai','artificial intelligence','robot','tech','software','cyber','digital'],
    'Politics/Trump': ['trump','biden','election','democrat','republican','congress','senate'],
    'War/Conflict':  ['war','attack','missile','military','conflict','strike','bomb','kill'],
    'Economy':       ['economy','inflation','gdp','market','stock','trade','recession'],
    'Climate':       ['climate','environment','carbon','emission','flood','wildfire'],
}

def get_sentiment(text):
    if not text or len(text.strip()) < 5:
        return 'neutral', 0.0
    scores = analyzer.polarity_scores(text[:500])
    c = scores['compound']
    if c >= 0.05:    return 'positive', round(c,3)
    elif c <= -0.05: return 'negative', round(c,3)
    else:            return 'neutral',  round(c,3)

def get_topic(title, content):
    text = ((title or '') + ' ' + (content or '')).lower()
    for topic, keywords in TOPICS.items():
        if any(kw in text for kw in keywords):
            return topic
    return None

# Build source-topic-sentiment matrix
sources = ['CNN', 'The Hindu', 'Al Jazeera', 'NPR']
matrix = {}

for topic in TOPICS:
    matrix[topic] = {}
    for src in sources:
        matrix[topic][src] = {'positive':0,'neutral':0,'negative':0,'total':0,'avg_polarity':0,'polarities':[]}

for a in all_articles:
    src     = a.get('source','')
    if src not in sources:
        continue
    title   = a.get('title','') or ''
    content = a.get('content','') or a.get('description','') or ''
    topic   = get_topic(title, content)
    if not topic:
        continue
    sent, polarity = get_sentiment(content or title)
    matrix[topic][src][sent]    += 1
    matrix[topic][src]['total'] += 1
    matrix[topic][src]['polarities'].append(polarity)

# Calculate averages and bias scores
results = {}
for topic in TOPICS:
    results[topic] = {}
    for src in sources:
        data  = matrix[topic][src]
        total = data['total']
        if total == 0:
            results[topic][src] = None
            continue
        avg_pol = round(sum(data['polarities'])/len(data['polarities']),3)
        results[topic][src] = {
            'total':    total,
            'positive': data['positive'],
            'neutral':  data['neutral'],
            'negative': data['negative'],
            'pos_pct':  round(data['positive']/total*100,1),
            'neu_pct':  round(data['neutral']/total*100,1),
            'neg_pct':  round(data['negative']/total*100,1),
            'avg_polarity': avg_pol
        }

# Print results
print("\n" + "="*70)
print("CROSS-SOURCE BIAS ANALYSIS RESULTS")
print("="*70)

for topic in TOPICS:
    print(f"\n📌 Topic: {topic}")
    print(f"{'Source':<15} {'Total':>6} {'Pos%':>6} {'Neu%':>6} {'Neg%':>6} {'Avg Pol':>8} {'Bias'}")
    print("-"*60)
    
    topic_results = []
    for src in sources:
        r = results[topic][src]
        if r is None or r['total'] < 3:
            print(f"{src:<15} {'(insufficient data)':>40}")
            continue
        
        # Bias label
        if r['avg_polarity'] > 0.1:    bias = '🟢 Positive bias'
        elif r['avg_polarity'] < -0.1: bias = '🔴 Negative bias'
        elif r['avg_polarity'] > 0:    bias = '🟡 Slightly positive'
        else:                          bias = '🟠 Slightly negative'
        
        print(f"{src:<15} {r['total']:>6} {r['pos_pct']:>5}% {r['neu_pct']:>5}% {r['neg_pct']:>5}% {r['avg_polarity']:>8} {bias}")
        topic_results.append((src, r['avg_polarity'], r['total']))
    
    # Most biased source
    valid = [(s,p,t) for s,p,t in topic_results if t >= 3]
    if len(valid) >= 2:
        most_neg = min(valid, key=lambda x: x[1])
        most_pos = max(valid, key=lambda x: x[1])
        print(f"\n  → Most NEGATIVE: {most_neg[0]} ({most_neg[1]})")
        print(f"  → Most POSITIVE: {most_pos[0]} ({most_pos[1]})")

# Save results
with open('bias_analysis_results.json','w',encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("\n✅ Saved to bias_analysis_results.json!")
print("✅ Cross-source bias analysis complete!")
