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
