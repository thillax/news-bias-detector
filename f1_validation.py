from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.metrics import f1_score, precision_score, recall_score, classification_report
import json

analyzer = SentimentIntensityAnalyzer()

# Labeled test dataset (manual ground truth)
test_data = [
    # (text, true_label)
    ("The economy is growing strongly with record employment", "positive"),
    ("Deadly explosion kills dozens in city center", "negative"),
    ("Government releases annual budget report today", "neutral"),
    ("Scientists discover breakthrough cure for cancer", "positive"),
    ("Terrorist attack leaves many dead and injured", "negative"),
    ("Parliament session held to discuss new policies", "neutral"),
    ("Stock market reaches all time high record", "positive"),
    ("Floods destroy thousands of homes in disaster", "negative"),
    ("Weather forecast shows rain expected tomorrow", "neutral"),
    ("Olympic gold medal won by athlete in historic win", "positive"),
    ("War crimes committed in conflict zone investigation", "negative"),
    ("Trade deal signed between two countries today", "neutral"),
    ("Children rescued safely after being trapped", "positive"),
    ("Shooting leaves multiple victims dead at school", "negative"),
    ("Election results announced after counting votes", "neutral"),
    ("Vaccine saves millions of lives worldwide", "positive"),
    ("Hurricane devastates coastal towns killing many", "negative"),
    ("Central bank keeps interest rates unchanged", "neutral"),
    ("Team wins championship in thrilling final match", "positive"),
    ("Protest turns violent as police clash with crowd", "negative"),
    ("New law passed by parliament after debate", "neutral"),
    ("Space mission successfully lands on moon", "positive"),
    ("Toxic chemical spill poisons river water supply", "negative"),
    ("Annual inflation data published by statistics office", "neutral"),
    ("Hospital saves premature baby in miracle surgery", "positive"),
    ("Suicide bomber kills civilians in market attack", "negative"),
    ("Census data shows population growth slowing", "neutral"),
    ("Company reports record profits this quarter", "positive"),
    ("Earthquake destroys buildings trapping survivors", "negative"),
    ("Court hearing scheduled for next month", "neutral"),
    ("Student wins prestigious scholarship award", "positive"),
    ("Drug overdose deaths reach alarming new high", "negative"),
    ("Government minister attends international summit", "neutral"),
    ("Renewable energy project creates thousands of jobs", "positive"),
    ("Fire destroys historic building killing workers", "negative"),
    ("Police investigate robbery at downtown bank", "neutral"),
    ("Medical research shows promising results for treatment", "positive"),
    ("Mass shooting at concert kills dozens of fans", "negative"),
    ("City council votes on new budget proposal", "neutral"),
    ("Athlete breaks world record in stunning performance", "positive"),
]

print(f"Test dataset: {len(test_data)} labeled articles")

# Predict
y_true = []
y_pred = []

print("\nPrediction Results:")
print(f"{'Text':<55} {'True':>8} {'Pred':>8} {'Match':>6}")
print("-"*80)

correct = 0
for text, true_label in test_data:
    scores = analyzer.polarity_scores(text)
    compound = scores['compound']
    if compound >= 0.05:    pred = 'positive'
    elif compound <= -0.05: pred = 'negative'
    else:                   pred = 'neutral'
    
    y_true.append(true_label)
    y_pred.append(pred)
    
    match = '✅' if pred == true_label else '❌'
    if pred == true_label:
        correct += 1
    print(f"{text[:55]:<55} {true_label:>8} {pred:>8} {match:>6}")

# Calculate metrics
print("\n" + "="*60)
print("F1 SCORE RESULTS")
print("="*60)

accuracy = correct / len(test_data) * 100
f1_macro    = f1_score(y_true, y_pred, average='macro') * 100
f1_weighted = f1_score(y_true, y_pred, average='weighted') * 100
precision   = precision_score(y_true, y_pred, average='weighted') * 100
recall      = recall_score(y_true, y_pred, average='weighted') * 100

print(f"\n📊 Overall Metrics:")
print(f"  Accuracy:           {accuracy:.1f}%")
print(f"  F1 Score (macro):   {f1_macro:.1f}%")
print(f"  F1 Score (weighted):{f1_weighted:.1f}%")
print(f"  Precision:          {precision:.1f}%")
print(f"  Recall:             {recall:.1f}%")

print(f"\n📊 Classification Report:")
print(classification_report(y_true, y_pred, 
      target_names=['negative','neutral','positive']))

# Save results
results = {
    'model': 'VADER Sentiment Analyzer',
    'test_size': len(test_data),
    'correct': correct,
    'accuracy': round(accuracy,1),
    'f1_macro': round(f1_macro,1),
    'f1_weighted': round(f1_weighted,1),
    'precision': round(precision,1),
    'recall': round(recall,1)
}

with open('f1_validation_results.json','w') as f:
    json.dump(results, f, indent=2)

print(f"\n✅ Saved to f1_validation_results.json!")
print(f"✅ F1 Validation Complete!")
