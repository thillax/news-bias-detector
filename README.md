# AI-Powered News Bias Detector

Flask dashboard that collects news from CNN, The Hindu, Al Jazeera and NPR (RSS), then analyses sentiment, topics and cross-source bias.

**Live demo:** https://news-bias-detector-u4pu.onrender.com

## Data
1,081 articles collected over several RSS runs, 248 unique after de-duplication by title (CNN 50, The Hindu 116, Al Jazeera 54, NPR 28).

## Features
- RSS collection with a "Collect Now" trigger
- VADER sentiment (polarity), keyword topic classes, LDA topic modelling (Gensim)
- NER, POS tagging and lemmatization (NLTK)
- Cross-source bias comparison, bias heatmap, sentiment shift detection (Welch t-test per source)
- Left/Center/Right and tone labelling (source ratings + keyword lexicon, not a trained classifier)
- CSV export, user feedback (thumbs up/down); dashboard filters are work in progress

## Results (sentiment classification on labelled headlines)
n = 207 headlines (93 negative, 81 neutral, 33 positive), labelled by: the author using AI assistance (Claude); labels not yet independently verified.
5 seeds x 5-fold stratified CV, macro F1:

| Model | Macro F1 |
|---|---|
| TF-IDF + Logistic Regression | 0.436 +/- 0.030 |
| VADER alone | 0.458 |
| TF-IDF + VADER score as a feature | 0.570 +/- 0.010 |

This is below the 0.85 target. Reasons: small labelled set, subjective headline labels, only 33 positive examples. An earlier 90% on 40 clear-cut test sentences was a sanity check, not a real-headline result.

## Limitations
- Sentiment shift detection found 0 statistically significant shifts: only a few days of data, 7-18 articles per source per day
- Political leaning labels use source ratings plus keywords, not a trained classifier
- BERT, SHAP, PostgreSQL, Docker and Celery are future work
- On Render's free tier the SQLite file resets on redeploy, and the hourly collector does not run (use Collect Now)

## Run locally
    pip install -r requirements.txt
    python phase12_mass_dark.py




## Label verification
The sentiment labels were produced with AI assistance. To check them, the author independently labelled a random sample of 40 headlines without seeing the AI label: agreement 88%, Cohen's kappa 0.81.
