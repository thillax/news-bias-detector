import json
from textblob import TextBlob
import glob

# Load all articles
all_articles = []
for file in sorted(glob.glob('collected_articles/*.json')):
    with open(file, 'r', encoding='utf-8') as f:
        all_articles.extend(json.load(f))

print(f"Loaded: {len(all_articles)} articles")

# Topic keywords (same as phase11)
TOPICS = {
    'Technology': ['tech','software','ai','cyber','digital','computer','internet','robot','data','cloud','hack','security','app','startup','innovation'],
    'Politics':   ['government','election','president','minister','parliament','policy','congress','senate','vote','political','party','democrat','republican','modi','trump','biden'],
    'Economics':  ['economy','gdp','inflation','market','stock','trade','finance','bank','investment','recession','budget','tax','price','growth'],
    'Health':     ['health','covid','vaccine','hospital','doctor','disease','medical','virus','cancer','drug','patient','treatment','mental'],
    'Climate':    ['climate','environment','carbon','emission','renewable','solar','pollution','temperature','flood','drought','wildfire','green'],
    'Sports':     ['cricket','football','tennis','basketball','olympic','match','tournament','player','team','score','championship','ipl','fifa'],
    'Entertainment': ['movie','film','music','actor','celebrity','award','oscar','grammy','netflix','streaming','song','album','concert'],
    'World':      ['war','conflict','military','army','nato','ukraine','russia','china','israel','iran','sanctions','nuclear','missile'],
    'Science':    ['science','research','space','nasa','discovery','experiment','study','physics','biology','chemistry','universe','planet'],
}

def get_topic(title, content):
    text = ((title or '') + ' ' + (content or '')).lower()
    for topic, keywords in TOPICS.items():
        if any(kw in text for kw in keywords):
            return topic
    return 'Other'

def get_sentiment(text):
    if not text or len(text.strip()) < 10:
        return 'neutral'
    blob = TextBlob(text[:300])
    p = blob.sentiment.polarity
    if p > 0.1:    return 'positive'
    elif p < -0.1: return 'negative'
    else:          return 'neutral'

# Build topic-sentiment counts
topic_counts = {t: {'total':0,'positive':0,'neutral':0,'negative':0} for t in list(TOPICS.keys())+['Other']}

for a in all_articles:
    title   = a.get('title','')
    content = a.get('content','') or a.get('description','') or ''
    topic   = get_topic(title, content)
    sent    = get_sentiment(content or title)
    topic_counts[topic]['total']    += 1
    topic_counts[topic][sent]       += 1

# Build results
topic_sentiment = []
for topic, counts in topic_counts.items():
    total = counts['total']
    if total == 0:
        continue
    topic_sentiment.append({
        'topic':    topic,
        'total':    total,
        'positive': counts['positive'],
        'neutral':  counts['neutral'],
        'negative': counts['negative'],
        'pos_%':    round(counts['positive']/total*100, 1),
        'neu_%':    round(counts['neutral']/total*100, 1),
        'neg_%':    round(counts['negative']/total*100, 1),
    })

# Sort by total
topic_sentiment.sort(key=lambda x: x['total'], reverse=True)

# topic_distribution for insights
topic_distribution = {t['topic']: t['total'] for t in topic_sentiment}

# Save updated phase11 results
result = {
    'total_articles':    len(all_articles),
    'total_topics':      len(topic_sentiment),
    'topic_distribution': topic_distribution,
    'topic_sentiment':   topic_sentiment,
    'topics_list':       [t['topic'] for t in topic_sentiment]
}

with open('phase11_topics_results.json','w',encoding='utf-8') as f:
    json.dump(result, f, indent=2)

print("\n✅ FIXED! Topic-Sentiment Results:")
print(f"{'Topic':<15} {'Total':>6} {'Pos%':>6} {'Neu%':>6} {'Neg%':>6}")
print("-"*45)
for t in topic_sentiment:
    print(f"{t['topic']:<15} {t['total']:>6} {t['pos_%']:>5}% {t['neu_%']:>5}% {t['neg_%']:>5}%")

print("\n✅ Saved to phase11_topics_results.json!")
