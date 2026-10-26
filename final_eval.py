import csv, html, json, numpy as np
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

rows = [r for r in csv.DictReader(open('label_me.csv', encoding='utf-8-sig')) if r['sentiment'].strip()]
X = [html.unescape(r['title'] + '. ' + r['snippet']) for r in rows]
y = np.array([r['sentiment'].strip() for r in rows])
an = SentimentIntensityAnalyzer()
comp = np.array([an.polarity_scores(t)['compound'] for t in X])
v = comp.reshape(-1, 1)

def run(use_v, seed):
    pred = np.empty(len(y), dtype=object)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=seed).split(X, y):
        vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words='english' if use_v else None)
        Xtr, Xte = vec.fit_transform([X[i] for i in tr]), vec.transform([X[i] for i in te])
        if use_v:
            Xtr, Xte = hstack([Xtr, csr_matrix(v[tr])]), hstack([Xte, csr_matrix(v[te])])
        pred[te] = LogisticRegression(max_iter=2000, class_weight='balanced').fit(Xtr, y[tr]).predict(Xte)
    return f1_score(y, pred, average='macro')

res = {}
for name, flag in [('tfidf_logreg', False), ('tfidf_plus_vader_feature', True)]:
    s = [run(flag, sd) for sd in range(5)]
    res[name] = {'mean': round(float(np.mean(s)), 3), 'std': round(float(np.std(s)), 3)}
vp = np.where(comp >= 0.05, 'positive', np.where(comp <= -0.05, 'negative', 'neutral'))
res['vader_alone'] = round(float(f1_score(y, vp, average='macro')), 3)
res['n'] = len(y)
print(json.dumps(res, indent=2))
json.dump(res, open('model_results.json', 'w'), indent=2)
