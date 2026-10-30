"""
nlp_pipeline.py
NLP pipeline for TransitVoice: preprocessing, classification, sentiment, phrase extraction.
"""

import os
import re
import string
import joblib
import pandas as pd
from collections import Counter

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

MODEL_PATH = "models/transit_classifier.joblib"
CATEGORIES = [
    "Delays and Punctuality",
    "Overcrowding",
    "Cleanliness",
    "Staff Behaviour",
    "Ticketing and Fares",
    "Safety and Security",
    "Accessibility",
    "Other Issues",
]

_analyzer = SentimentIntensityAnalyzer()
_pipeline = None


# ─────────────────────────────────────────────────────────────────────────────
# Text preprocessing
# ─────────────────────────────────────────────────────────────────────────────

def preprocess(text: str) -> str:
    """
    Clean text for TF-IDF: lowercase, strip extra whitespace,
    remove punctuation (keeping apostrophes for negations like "can't").
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s']", " ", text)   # keep word chars + apostrophes
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Model training / loading
# ─────────────────────────────────────────────────────────────────────────────

def train_model(df: pd.DataFrame) -> dict:
    """
    Train a TF-IDF + Logistic Regression pipeline.
    Returns the pipeline and evaluation metrics.
    """
    os.makedirs("models", exist_ok=True)

    X = df["feedback"].apply(preprocess)
    y = df["category"]

    # Attempt stratified split; fall back if too few samples per class
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True,
            min_df=1,
        )),
        ("clf", LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight="balanced",
            C=1.0,
        )),
    ])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)

    joblib.dump(pipe, MODEL_PATH)
    return {"pipeline": pipe, "report": report, "test_size": len(X_test)}


def load_or_train(df: pd.DataFrame):
    """Load saved model; retrain if missing or dataset changed."""
    global _pipeline
    if _pipeline is not None:
        return _pipeline

    if os.path.exists(MODEL_PATH):
        try:
            _pipeline = joblib.load(MODEL_PATH)
            return _pipeline
        except Exception:
            pass

    result = train_model(df)
    _pipeline = result["pipeline"]
    return _pipeline


def get_model(df: pd.DataFrame):
    return load_or_train(df)


def retrain_model(df: pd.DataFrame) -> dict:
    """Force retrain and return metrics."""
    global _pipeline
    result = train_model(df)
    _pipeline = result["pipeline"]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Classification
# ─────────────────────────────────────────────────────────────────────────────

def classify_feedback(text: str, pipeline) -> dict:
    """
    Predict the transport issue category.
    Returns label, confidence, and all class probabilities.
    """
    cleaned = preprocess(text)
    if not cleaned:
        return {"label": "Unknown", "confidence": 0.0, "probabilities": {}}

    label = pipeline.predict([cleaned])[0]
    proba = pipeline.predict_proba([cleaned])[0]
    classes = pipeline.classes_
    prob_dict = {c: round(float(p), 4) for c, p in zip(classes, proba)}
    confidence = round(float(max(proba)), 4)

    return {"label": label, "confidence": confidence, "probabilities": prob_dict}


# ─────────────────────────────────────────────────────────────────────────────
# Sentiment analysis (VADER)
# ─────────────────────────────────────────────────────────────────────────────

def analyze_sentiment(text: str) -> dict:
    """
    Run VADER on the original (non-preprocessed) text to preserve negations.
    Returns label, compound score, and raw scores.
    """
    if not isinstance(text, str) or not text.strip():
        return {"label": "Neutral", "compound": 0.0, "pos": 0.0, "neu": 1.0, "neg": 0.0}

    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "Positive"
    elif compound <= -0.05:
        label = "Negative"
    else:
        label = "Neutral"

    return {
        "label": label,
        "compound": round(compound, 4),
        "pos": round(scores["pos"], 4),
        "neu": round(scores["neu"], 4),
        "neg": round(scores["neg"], 4),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Phrase / keyword extraction
# ─────────────────────────────────────────────────────────────────────────────

_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "was", "were", "are", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "i", "my", "me",
    "we", "our", "you", "your", "it", "its", "this", "that", "there",
    "their", "they", "he", "she", "his", "her", "so", "very", "just",
    "not", "no", "if", "when", "as", "up", "out", "about", "who",
    "which", "what", "all", "also", "s", "re", "ll", "ve", "t",
}


def extract_phrases(text: str, top_n: int = 5) -> list[str]:
    """
    Extract meaningful keywords/bigrams from user feedback using TF-inspired
    token frequency. Keeps negation bigrams like 'not clean'.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Generate unigrams
    tokens = re.findall(r"\b[a-z']+\b", text.lower())
    unigrams = [t for t in tokens if t not in _STOPWORDS and len(t) > 2]

    # Generate bigrams (keep even if one part is a stopword for negations)
    raw_tokens = re.findall(r"\b[a-z']+\b", text.lower())
    bigrams = []
    for i in range(len(raw_tokens) - 1):
        a, b = raw_tokens[i], raw_tokens[i + 1]
        # Keep bigrams where at least one word is content-bearing
        if (a not in _STOPWORDS or b not in _STOPWORDS) and len(a) > 1 and len(b) > 1:
            if a in ("not", "no", "never", "cannot", "can't") or (a not in _STOPWORDS and b not in _STOPWORDS):
                bigrams.append(f"{a} {b}")

    counts = Counter(unigrams + bigrams)
    # Return top N by frequency
    return [phrase for phrase, _ in counts.most_common(top_n)]


# ─────────────────────────────────────────────────────────────────────────────
# Batch analysis for the full dataset
# ─────────────────────────────────────────────────────────────────────────────

def batch_analyze(df: pd.DataFrame, pipeline) -> pd.DataFrame:
    """
    Adds sentiment columns to the dataframe.
    """
    sentiments = df["feedback"].apply(analyze_sentiment)
    df = df.copy()
    df["sentiment"] = sentiments.apply(lambda x: x["label"])
    df["sentiment_score"] = sentiments.apply(lambda x: x["compound"])
    return df
