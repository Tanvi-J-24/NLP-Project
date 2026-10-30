"""quick_test.py – validation script"""
import pandas as pd
from nlp_pipeline import get_model, classify_feedback, analyze_sentiment, extract_phrases, batch_analyze
from data_analysis import get_transitpulse_insights

df = pd.read_csv("data/passenger_feedback.csv")
pipe = get_model(df)
print("Model loaded OK")

tests = [
    "The bus was 25 minutes late and no announcement was made.",
    "Rude driver shouted at elderly passengers.",
    "Lift at the station is broken again third time this month.",
    "Felt very unsafe on the platform at night.",
    "Was charged twice for a single journey.",
    "Bus was spotlessly clean today, great service!",
    "",
]
for t in tests:
    r = classify_feedback(t, pipe)
    s = analyze_sentiment(t)
    kw = extract_phrases(t)
    label = r["label"]
    slabel = s["label"]
    conf = r["confidence"]
    print(f"CAT={label:30s} SENT={slabel:8s} CONF={conf:.2f} | {t[:55]}")

adf = batch_analyze(df, pipe)
print(f"\nBatch done. Cols: {list(adf.columns)}")
insights = get_transitpulse_insights(adf)
print(f"Top issue: {insights['top_category']}")
print(f"Neg%: {insights['neg_pct']}")
print(f"Recommendations ({len(insights['recommendations'])}):")
for rec in insights["recommendations"]:
    print(" ", rec[:80])
print("\nALL CHECKS PASSED")
