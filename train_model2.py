import csv, html, numpy as np
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
v = np.array([[an.polarity_scores(t)['compound']] for t in X])

pred = np.empty(len(y), dtype=object)
for tr, te in StratifiedKFold(5, shuffle=True, random_state=42).split(X, y):
    vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words='english')
    Xtr = hstack([vec.fit_transform([X[i] for i in tr]), csr_matrix(v[tr])])
    Xte = hstack([vec.transform([X[i] for i in te]), csr_matrix(v[te])])
    pred[te] = LogisticRegression(max_iter=2000, class_weight='balanced').fit(Xtr, y[tr]).predict(Xte)
print('TF-IDF + VADER feature, macro F1: %.3f' % f1_score(y, pred, average='macro'))
