"""
data_analysis.py
Filtering, TransitPulse insights, route comparisons, and report preparation.
"""

import pandas as pd
from collections import Counter
import re

from nlp_pipeline import _STOPWORDS


# ─────────────────────────────────────────────────────────────────────────────
# Filtering
# ─────────────────────────────────────────────────────────────────────────────

def filter_data(
    df: pd.DataFrame,
    routes: list[str] | None = None,
    categories: list[str] | None = None,
    sentiments: list[str] | None = None,
) -> pd.DataFrame:
    filtered = df.copy()
    if routes:
        filtered = filtered[filtered["route"].isin(routes)]
    if categories:
        filtered = filtered[filtered["category"].isin(categories)]
    if sentiments:
        filtered = filtered[filtered["sentiment"].isin(sentiments)]
    return filtered


# ─────────────────────────────────────────────────────────────────────────────
# TransitPulse
# ─────────────────────────────────────────────────────────────────────────────

def get_transitpulse_insights(df: pd.DataFrame) -> dict:
    """
    Compute TransitPulse insights from the current dataset.
    All conclusions are labelled as dataset-relative.
    """
    insights = {}
    n = len(df)
    if n == 0:
        return insights

    # 1. Category frequency
    cat_counts = df["category"].value_counts()
    insights["category_counts"] = cat_counts
    insights["top_category"] = cat_counts.index[0] if len(cat_counts) else "N/A"
    insights["top_category_count"] = int(cat_counts.iloc[0]) if len(cat_counts) else 0

    # 2. Negative feedback breakdown
    if "sentiment" in df.columns:
        neg_df = df[df["sentiment"] == "Negative"]
        insights["neg_count"] = len(neg_df)
        insights["neg_pct"] = round(len(neg_df) / n * 100, 1)
        insights["neg_by_category"] = neg_df["category"].value_counts() if len(neg_df) else pd.Series(dtype=int)

        # 3. Recurring keywords in negative feedback
        if len(neg_df) > 0:
            all_text = " ".join(neg_df["feedback"].tolist()).lower()
            tokens = re.findall(r"\b[a-z']+\b", all_text)
            filtered_tokens = [t for t in tokens if t not in _STOPWORDS and len(t) > 3]
            insights["recurring_keywords"] = Counter(filtered_tokens).most_common(15)
        else:
            insights["recurring_keywords"] = []
    else:
        insights["neg_count"] = 0
        insights["neg_pct"] = 0.0
        insights["neg_by_category"] = pd.Series(dtype=int)
        insights["recurring_keywords"] = []

    # 4. Positive feedback
    if "sentiment" in df.columns:
        pos_df = df[df["sentiment"] == "Positive"]
        insights["pos_count"] = len(pos_df)
        insights["pos_pct"] = round(len(pos_df) / n * 100, 1)

    # 5. Temporal trend (if date available and enough data)
    insights["trend_available"] = False
    if "date" in df.columns:
        try:
            df_t = df.copy()
            df_t["date"] = pd.to_datetime(df_t["date"], errors="coerce")
            df_t = df_t.dropna(subset=["date"])
            df_t["week"] = df_t["date"].dt.to_period("W")
            weeks = sorted(df_t["week"].unique())
            if len(weeks) >= 2:
                w1 = df_t[df_t["week"] == weeks[0]]
                w2 = df_t[df_t["week"] == weeks[-1]]
                trend = {}
                for cat in df["category"].unique():
                    c1 = len(w1[w1["category"] == cat])
                    c2 = len(w2[w2["category"] == cat])
                    if c1 > 0 or c2 > 0:
                        trend[cat] = {"first_week": c1, "last_week": c2, "delta": c2 - c1}
                insights["trend"] = trend
                insights["trend_weeks"] = (str(weeks[0]), str(weeks[-1]))
                insights["trend_available"] = True
        except Exception:
            pass

    # 6. Rule-based recommendations
    insights["recommendations"] = _generate_recommendations(insights)
    return insights


def _generate_recommendations(insights: dict) -> list[str]:
    recs = []
    cat_counts = insights.get("category_counts", pd.Series(dtype=int))
    neg_by_cat = insights.get("neg_by_category", pd.Series(dtype=int))
    neg_pct = insights.get("neg_pct", 0)

    if neg_pct > 50:
        recs.append(
            f"[HIGH] Over half of all feedback in this dataset is negative ({neg_pct}%). "
            "A comprehensive service review is recommended."
        )

    if len(neg_by_cat) > 0:
        worst = neg_by_cat.index[0]
        recs.append(
            f"[ACTION] **{worst}** has the highest concentration of negative feedback "
            "in this dataset. Consider targeted investigation and improvement."
        )

    if "Delays and Punctuality" in cat_counts and cat_counts.get("Delays and Punctuality", 0) >= 5:
        recs.append(
            "[DELAYS] Repeated delay complaints detected. Review timetables, driver schedules, "
            "and real-time tracking accuracy."
        )

    if "Cleanliness" in cat_counts and cat_counts.get("Cleanliness", 0) >= 4:
        recs.append(
            "[CLEANLINESS] Multiple cleanliness complaints recorded. Audit cleaning frequency "
            "and standards, especially on high-volume routes."
        )

    if "Safety and Security" in cat_counts and cat_counts.get("Safety and Security", 0) >= 3:
        recs.append(
            "[SAFETY] Safety concerns reported. Review CCTV coverage, staff training, "
            "and security presence on affected routes."
        )

    if "Accessibility" in cat_counts and cat_counts.get("Accessibility", 0) >= 3:
        recs.append(
            "[ACCESS] Accessibility issues noted. Inspect ramps, lifts, audio systems, "
            "and tactile guidance at affected stops."
        )

    if "Staff Behaviour" in cat_counts and cat_counts.get("Staff Behaviour", 0) >= 3:
        recs.append(
            "[STAFF] Staff behaviour complaints present. Consider additional customer service "
            "training and review conduct policies."
        )

    if "Overcrowding" in cat_counts and cat_counts.get("Overcrowding", 0) >= 4:
        recs.append(
            "[CAPACITY] Overcrowding reported on multiple routes. Evaluate capacity on peak-hour "
            "services and consider frequency increases."
        )

    if not recs:
        recs.append("[OK] No critical patterns detected in the current dataset. Continue monitoring.")

    return recs


# ─────────────────────────────────────────────────────────────────────────────
# Route insights
# ─────────────────────────────────────────────────────────────────────────────

def get_route_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary DataFrame of issue counts and sentiment per route."""
    if df.empty or "route" not in df.columns:
        return pd.DataFrame()

    summary = (
        df.groupby("route")
        .agg(
            total=("feedback", "count"),
            negative=("sentiment", lambda x: (x == "Negative").sum()),
            positive=("sentiment", lambda x: (x == "Positive").sum()),
        )
        .reset_index()
    )
    summary["neg_pct"] = (summary["negative"] / summary["total"] * 100).round(1)
    summary = summary.sort_values("negative", ascending=False)
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# Report preparation
# ─────────────────────────────────────────────────────────────────────────────

def prepare_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return a clean export-ready dataframe."""
    cols = ["feedback", "route", "date", "category", "sentiment", "sentiment_score"]
    existing_cols = [c for c in cols if c in df.columns]
    report = df[existing_cols].copy()
    if "sentiment_score" in report.columns:
        report["sentiment_score"] = report["sentiment_score"].round(4)
    return report
