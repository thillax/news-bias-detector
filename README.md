# AI-Powered News Bias Detector

Flask dashboard that collects news from CNN, The Hindu, Al Jazeera and NPR (RSS), then analyses sentiment, topics and cross-source bias.

## Features
- RSS collection (1,000+ articles) with a "Collect Now" trigger
- VADER sentiment (polarity), keyword topic classes, LDA topic modelling (Gensim)
- NER, POS tagging and lemmatization (NLTK)
- Cross-source bias comparison, bias heatmap, sentiment trends over time
- Left/Center/Right and tone labelling (source ratings + keyword lexicon)
- Filters, CSV export, user feedback (thumbs up/down)

## Validation
VADER scored 90% accuracy / macro F1 on a 40-sentence hand-labelled test set. This is an initial check, a larger labelled dataset is planned.

## Limitations
- Political leaning labels use source ratings plus keywords, not a trained classifier
- BERT, SHAP, PostgreSQL and Docker are future work

## Run locally
    pip install -r requirements.txt
    python phase12_mass_dark.py

**Live demo:** https://news-bias-detector-u4pu.onrender.com

**Live demo:** https://news-bias-detector-u4pu.onrender.com

## Results (sentiment classification on labelled headlines)

n = 207 headlines (93 negative, 81 neutral, 33 positive), labelled by: <WHO LABELLED>.
5 seeds x 5-fold stratified CV, macro F1:

| Model | Macro F1 |
|---|---|
| TF-IDF + Logistic Regression | 0.436 +/- 0.030 |
| VADER alone | 0.458 |
| TF-IDF + VADER score as a feature | 0.570 +/- 0.010 |

This is below the 0.85 target. Reasons: small labelled set, subjective headline labels, only 33 positive examples. Earlier 90% on 40 clear-cut test sentences was a sanity check, not a real-headline result.
Next: larger multi-annotator dataset, DistilBERT fine-tune, SHAP.
