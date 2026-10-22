import json
import glob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Known source bias (from MediaBiasFactCheck)
SOURCE_BIAS = {
    'CNN':        {'political': 'Left-Center',  'score': -1},
    'NPR':        {'political': 'Left-Center',  'score': -0.5},
    'Al Jazeera': {'political': 'Center',       'score': 0},
    'The Hindu':  {'political': 'Center-Left',  'score': -0.3},
}

# Enhanced keyword lexicons
LEFT_KEYWORDS = [
    'climate crisis', 'systemic', 'marginalized', 'equity', 'diverse',
    'inclusive', 'progressive', 'activist', 'protest', 'reform',
    'rights', 'social', 'community', 'vulnerable', 'discrimination',
    'inequality', 'poverty', 'healthcare access', 'gun violence',
    'reproductive', 'lgbtq', 'trans', 'immigrant', 'refugee'
]

RIGHT_KEYWORDS = [
    'border', 'illegal', 'freedom', 'liberty', 'patriot',
    'constitution', 'traditional', 'family values', 'law and order',
    'second amendment', 'pro-life', 'free market', 'tax', 'military',
    'national security', 'sovereignty', 'elite', 'mainstream media',
    'radical left', 'socialist', 'communist', 'maga', 'trump'
]

EMOTIONAL_KEYWORDS = [
    'shocking', 'outrageous', 'horrifying', 'devastating', 'explosive',
    'bombshell', 'catastrophe', 'alarming', 'terrifying', 'scandalous',
    'breaking', 'urgent', 'chaos', 'crisis', 'tragedy', 'nightmare'
]

LOADED_KEYWORDS = [
    'regime', 'invasion', 'radical', 'extreme', 'corrupt', 'propaganda',
    'agenda', 'conspiracy', 'puppet', 'weaponized', 'rigged', 'hoax',
    'fake', 'deep state', 'elites', 'globalist', 'indoctrination'
]

def classify_bias(text, source):
    text_lower = (text or '').lower()

    # Keyword scoring
    left_score  = sum(2 for kw in LEFT_KEYWORDS  if kw in text_lower)
    right_score = sum(2 for kw in RIGHT_KEYWORDS if kw in text_lower)
    emo_score   = sum(1 for kw in EMOTIONAL_KEYWORDS if kw in text_lower)
    load_score  = sum(1 for kw in LOADED_KEYWORDS    if kw in text_lower)

    # Add source bias score
    src_bias = SOURCE_BIAS.get(source, {'score': 0})
    left_score  += max(0, -src_bias['score'] * 3)
    right_score += max(0,  src_bias['score'] * 3)

    # VADER sentiment influence
    scores   = analyzer.polarity_scores(text[:300])
    compound = scores['compound']

    # Political classification
    diff = left_score - right_score
    if diff > 2:      political = 'Left'
    elif diff > 0:    political = 'Left-Center'
    elif diff == 0:   political = 'Center'
    elif diff > -2:   political = 'Right-Center'
    else:             political = 'Right'

    # Tone classification
    if emo_score >= 2:   tone = 'Emotional'
    elif load_score >= 2: tone = 'Loaded'
    elif compound < -0.3: tone = 'Negative-Loaded'
    else:                 tone = 'Neutral'

    return political, tone, left_score, right_score, emo_score, load_score

# Load articles
all_articles = []
for file in sorted(glob.glob('collected_articles/*.json')):
    with open(file,'r',encoding='utf-8') as f:
        all_articles.extend(json.load(f))

print(f"Loaded: {len(all_articles)} articles")

# Analyze
bias_counts  = {'Left':0,'Left-Center':0,'Center':0,'Right-Center':0,'Right':0}
tone_counts  = {'Neutral':0,'Emotional':0,'Loaded':0,'Negative-Loaded':0}
source_bias  = {}
results      = []

for a in all_articles:
    text = (a.get('title','') or '') + ' ' + (a.get('content','') or '')[:500]
    src  = a.get('source','Unknown')

    political, tone, ls, rs, es, lo = classify_bias(text, src)

    bias_counts[political] = bias_counts.get(political,0) + 1
    tone_counts[tone]      = tone_counts.get(tone,0)      + 1

    if src not in source_bias:
        source_bias[src] = {'Left':0,'Left-Center':0,'Center':0,'Right-Center':0,'Right':0,'total':0}
    source_bias[src][political] = source_bias[src].get(political,0) + 1
    source_bias[src]['total']   += 1

    results.append({
        'title':          (a.get('title','') or '')[:80],
        'source':         src,
        'political_bias': political,
        'tone_bias':      tone,
        'left_score':     ls,
        'right_score':    rs
    })

# Print
print("\n" + "="*65)
print("ENHANCED BIAS CLASSIFICATION RESULTS")
print("="*65)

total = len(results)
print(f"\n📌 Political Bias Distribution:")
for bias, count in bias_counts.items():
    pct = round(count/total*100,1)
    bar = '█' * min(count//10,25)
    print(f"  {bias:<15} {count:>5} ({pct:>5}%)  {bar}")

print(f"\n📌 Tone Classification:")
for tone, count in tone_counts.items():
    pct = round(count/total*100,1)
    bar = '█' * min(count//10,25)
    print(f"  {tone:<18} {count:>5} ({pct:>5}%)  {bar}")

print(f"\n📌 Political Bias by Source:")
print(f"{'Source':<15} {'Total':>5} {'Left%':>6} {'L-C%':>6} {'Ctr%':>6} {'R-C%':>6} {'Right%':>7}")
print("-"*60)
for src, data in source_bias.items():
    t = data['total']
    if t == 0: continue
    print(f"{src:<15} {t:>5} "
          f"{round(data.get('Left',0)/t*100,1):>5}% "
          f"{round(data.get('Left-Center',0)/t*100,1):>5}% "
          f"{round(data.get('Center',0)/t*100,1):>5}% "
          f"{round(data.get('Right-Center',0)/t*100,1):>5}% "
          f"{round(data.get('Right',0)/t*100,1):>6}%")

# Save
output = {
    'total_articles':  total,
    'political_bias':  bias_counts,
    'tone_bias':       tone_counts,
    'source_bias':     source_bias,
    'methodology':     'Keyword lexicon + MediaBiasFactCheck source ratings + VADER sentiment',
    'articles':        results[:200]
}

with open('bias_classification_results.json','w',encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Saved to bias_classification_results.json!")
print(f"✅ Enhanced bias classification complete!")
