import csv, html, json, numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import f1_score, classification_report
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

rows = [r for r in csv.DictReader(open('label_me.csv', encoding='utf-8-sig'))
        if r['sentiment'].strip() and r['tone'].strip()]
X = [html.unescape(r['title'] + '. ' + r['snippet']) for r in rows]
y = [r['sentiment'].strip() for r in rows]
print('n =', len(rows), Counter(y))
k = min(5, min(Counter(y).values()))
print('folds =', k)

clf = make_pipeline(TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True),
                    LogisticRegression(max_iter=2000, class_weight='balanced'))
cv = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
pred = cross_val_predict(clf, X, y, cv=cv)
print('\nTF-IDF + LogReg (CV macro F1): %.3f' % f1_score(y, pred, average='macro'))
print(classification_report(y, pred, zero_division=0))

an = SentimentIntensityAnalyzer()
def vader(t):
    c = an.polarity_scores(t)['compound']
    return 'positive' if c >= 0.05 else 'negative' if c <= -0.05 else 'neutral'
vp = [vader(t) for t in X]
print('VADER on the same hand labels (macro F1): %.3f' % f1_score(y, vp, average='macro'))

clf.fit(X, y)
vec, lr = clf.steps[0][1], clf.steps[1][1]
names = np.array(vec.get_feature_names_out())
top = {c: names[np.argsort(lr.coef_[i])[-8:][::-1]].tolist() for i, c in enumerate(lr.classes_)}
print('\nTop words per class (model explanation):')
for c, w in top.items():
    print(' ', c, w)

json.dump({'n': len(rows), 'folds': k,
           'logreg_cv_macro_f1': round(f1_score(y, pred, average='macro'), 3),
           'vader_macro_f1': round(f1_score(y, vp, average='macro'), 3),
           'top_words': top}, open('model_results.json', 'w'), indent=2)
