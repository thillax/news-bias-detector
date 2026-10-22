import json
import glob
import re
from collections import defaultdict
from gensim import corpora, models
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer
import nltk

nltk.download('wordnet', quiet=True)
lemmatizer = WordNetLemmatizer()

# Load articles
all_articles = []
for file in sorted(glob.glob('collected_articles/*.json')):
    with open(file,'r',encoding='utf-8') as f:
        all_articles.extend(json.load(f))

print(f"Loaded: {len(all_articles)} articles")

# Preprocess text
def preprocess(text):
    if not text:
        return []
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(t) for t in tokens
              if t not in STOPWORDS
              and len(t) > 3
              and t.isalpha()]
    return tokens

print("Preprocessing texts...")
texts = []
for a in all_articles:
    content = (a.get('title','') or '') + ' ' + (a.get('content','') or '')[:300]
    tokens = preprocess(content)
    if tokens:
        texts.append(tokens)

print(f"Processed: {len(texts)} documents")

# Build dictionary and corpus
dictionary = corpora.Dictionary(texts)
dictionary.filter_extremes(no_below=3, no_above=0.7)
corpus = [dictionary.doc2bow(text) for text in texts]

print(f"Dictionary size: {len(dictionary)}")
print(f"Corpus size: {len(corpus)}")

# Train LDA
print("\nTraining LDA model (this takes 1-2 mins)...")
NUM_TOPICS = 10
lda_model = models.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=NUM_TOPICS,
    random_state=42,
    passes=10,
    alpha='auto',
    eta='auto'
)

print("\n✅ LDA Model Trained!")
print("\n📌 LDA Topics Discovered:")
print("="*60)

topics_result = []
for idx, topic in lda_model.print_topics(num_words=8):
    # Extract keywords
    keywords = [w.split('*')[1].strip().strip('"') 
                for w in topic.split('+')]
    keywords_str = ', '.join(keywords)
    print(f"\nTopic {idx+1}: {keywords_str}")
    topics_result.append({
        'topic_id': idx+1,
        'keywords': keywords,
        'representation': topic
    })

# Assign topics to articles
print("\n📌 Assigning topics to articles...")
topic_names = {
    0: 'Politics & Government',
    1: 'Technology & Innovation',
    2: 'World Affairs',
    3: 'Economy & Finance',
    4: 'Health & Science',
    5: 'Sports & Entertainment',
    6: 'Environment & Climate',
    7: 'Social Issues',
    8: 'Crime & Justice',
    9: 'Business & Industry'
}

article_topics = []
topic_counts = defaultdict(int)

for i, (text, bow) in enumerate(zip(texts, corpus)):
    topic_dist = lda_model.get_document_topics(bow)
    if topic_dist:
        dominant = max(topic_dist, key=lambda x: x[1])
        topic_id = dominant[0]
        topic_prob = dominant[1]
        topic_name = topic_names.get(topic_id, f'Topic {topic_id+1}')
        topic_counts[topic_name] += 1
        article_topics.append({
            'topic_id': topic_id,
            'topic_name': topic_name,
            'probability': round(topic_prob, 3)
        })

print("\n📌 Topic Distribution:")
total = len(article_topics)
for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
    pct = round(count/total*100, 1)
    bar = '█' * min(count//10, 25)
    print(f"  {topic:<30} {count:>5} ({pct}%)  {bar}")

# Save results
results = {
    'model': 'LDA (Latent Dirichlet Allocation)',
    'num_topics': NUM_TOPICS,
    'total_articles': len(all_articles),
    'processed_articles': len(texts),
    'topics': topics_result,
    'topic_distribution': dict(topic_counts),
    'topic_names': topic_names
}

with open('lda_results.json','w',encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved to lda_results.json!")
print(f"✅ LDA Topic Modeling COMPLETE!")
