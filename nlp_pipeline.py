import json
import glob
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.chunk import ne_chunk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from collections import Counter
import re

nltk.download('punkt_tab', quiet=True)
nltk.download('averaged_perceptron_tagger_eng', quiet=True)
nltk.download('maxent_ne_chunker_tab', quiet=True)
nltk.download('words', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('stopwords', quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# Load articles
all_articles = []
for file in sorted(glob.glob('collected_articles/*.json')):
    with open(file, 'r', encoding='utf-8') as f:
        all_articles.extend(json.load(f))

print(f"Loaded: {len(all_articles)} articles")
print("Processing NLP pipeline... (this takes 1-2 mins)")

sample = all_articles[:200]

all_entities  = []
all_pos_tags  = []
all_lemmas    = []
entity_types  = Counter()
pos_counts    = Counter()

for i, article in enumerate(sample):
    if i % 50 == 0:
        print(f"  Processing {i}/{len(sample)}...")
    
    title   = article.get('title','') or ''
    content = article.get('content','') or article.get('description','') or ''
    text    = title + ' ' + content[:500]
    if not text.strip():
        continue

    # Clean
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)

    try:
        # Tokenize
        tokens  = word_tokenize(text)

        # POS
        pos_tags = pos_tag(tokens)
        for word, tag in pos_tags:
            pos_counts[tag] += 1

        # NER
        chunks = ne_chunk(pos_tags)
        for chunk in chunks:
            if hasattr(chunk, 'label'):
                entity = ' '.join(c[0] for c in chunk)
                label  = chunk.label()
                all_entities.append((entity, label))
                entity_types[label] += 1

        # Lemmatization
        lemmas = [
            lemmatizer.lemmatize(w.lower())
            for w, t in pos_tags
            if w.lower() not in stop_words
            and len(w) > 3
            and w.isalpha()
        ]
        all_lemmas.extend(lemmas)

    except Exception as e:
        continue

print(f"\nDone! Processed {len(sample)} articles")

# Results
print("\n" + "="*60)
print("NLP PIPELINE RESULTS (200 articles)")
print("="*60)

print("\n📌 NER - Named Entity Types:")
for etype, count in entity_types.most_common():
    bar = '█' * min(count//5, 30)
    print(f"  {etype:<20} {count:>4}  {bar}")

print("\n📌 Top 25 Named Entities:")
entity_counter = Counter([e[0] for e in all_entities])
for entity, count in entity_counter.most_common(25):
    etype = next((t for e,t in all_entities if e==entity), '?')
    print(f"  {entity:<25} {count:>3}x  [{etype}]")

print("\n📌 POS Distribution:")
pos_map = {
    'NN':'Noun','NNS':'Noun(plural)','NNP':'Proper Noun','NNPS':'Proper Noun(pl)',
    'VB':'Verb','VBD':'Verb(past)','VBG':'Verb(gerund)','VBZ':'Verb(3rd)',
    'JJ':'Adjective','JJR':'Adj(comparative)','RB':'Adverb',
    'IN':'Preposition','DT':'Determiner','PRP':'Pronoun','CC':'Conjunction'
}
for tag, name in pos_map.items():
    count = pos_counts.get(tag, 0)
    bar   = '█' * min(count//20, 30)
    print(f"  {name:<22} {count:>5}  {bar}")

print("\n📌 Top 25 Lemmas (keywords):")
lemma_counter = Counter(all_lemmas)
for lemma, count in lemma_counter.most_common(25):
    bar = '█' * min(count//3, 20)
    print(f"  {lemma:<20} {count:>4}x  {bar}")

# Save
results = {
    'total_processed': len(sample),
    'ner': {
        'entity_types':  dict(entity_types),
        'top_entities':  [(e,c) for e,c in entity_counter.most_common(50)]
    },
    'pos': {
        'distribution': dict(pos_counts.most_common(20))
    },
    'lemmas': {
        'top_keywords': [(l,c) for l,c in lemma_counter.most_common(50)]
    }
}

with open('nlp_analysis_results.json','w',encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print("\n✅ Saved to nlp_analysis_results.json!")
print("✅ NER + POS + Lemmatization COMPLETE!")
