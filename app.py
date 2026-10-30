"""
app.py – TransitVoice: AI-Powered Public Transport Feedback Analyzer
Run with: streamlit run app.py
"""

import os
import io
import re
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Ensure project root is on path ─────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from generate_dataset import generate_dataset
from nlp_pipeline import (
    get_model, batch_analyze, classify_feedback,
    analyze_sentiment, extract_phrases, retrain_model,
)
from data_analysis import (
    filter_data, get_transitpulse_insights,
    get_route_summary, prepare_report,
)

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TransitVoice – Public Transport Feedback Analyzer",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ───────────────────────────────────────────────────────────────
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ── Color palette ────────────────────────────────────────────────────────────
SENTIMENT_COLORS = {
    "Positive": "#22c55e",
    "Neutral":  "#f59e0b",
    "Negative": "#ef4444",
}
CATEGORY_COLORS = [
    "#0891b2", "#0e7490", "#0f766e", "#065f46",
    "#1e40af", "#4f46e5", "#7c3aed", "#be185d",
]

# ── Data loading ─────────────────────────────────────────────────────────────
DATA_PATH = "data/passenger_feedback.csv"

def load_base_data() -> pd.DataFrame:
    if not os.path.exists(DATA_PATH):
        generate_dataset(DATA_PATH)
    return pd.read_csv(DATA_PATH)

@st.cache_resource(show_spinner=False)
def load_pipeline(df_hash: int):
    """Cache the trained pipeline by dataset hash."""
    df = load_base_data()
    return get_model(df)

def get_full_df() -> pd.DataFrame:
    """Merge base data with any session-added feedback."""
    base = load_base_data()
    added = st.session_state.get("added_feedback", [])
    if added:
        extra = pd.DataFrame(added)
        return pd.concat([base, extra], ignore_index=True)
    return base

def get_analyzed_df() -> pd.DataFrame:
    df = get_full_df()
    pipeline = load_pipeline(len(df))
    return batch_analyze(df, pipeline)

# ── Session state init ───────────────────────────────────────────────────────
if "added_feedback" not in st.session_state:
    st.session_state["added_feedback"] = []
if "page" not in st.session_state:
    st.session_state["page"] = "Overview"

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:16px 0 8px 0; text-align:center;">
          <div style="font-size:2.4rem;">🚌</div>
          <div style="font-size:1.2rem; font-weight:700; color:#e2e8f0;">TransitVoice</div>
          <div style="font-size:0.78rem; color:#94a3b8; margin-top:2px;">AI Feedback Analyzer</div>
        </div>
        <hr style="border-color:#334155; margin:12px 0;">
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigate",
        ["📊 Overview", "🔍 Analyze Feedback", "📡 TransitPulse", "🗺️ Route Insights", "📄 Reports"],
        key="nav",
    )
    page_name = page.split(" ", 1)[1]  # strip emoji

    st.markdown("<hr style='border-color:#334155; margin:20px 0 12px;'>", unsafe_allow_html=True)

    df_full = get_analyzed_df()
    st.markdown(
        f"""
        <div style="font-size:0.8rem; color:#94a3b8; padding:0 4px;">
          <b style="color:#e2e8f0;">Dataset</b><br>
          {len(df_full)} feedback records<br>
          {df_full['route'].nunique()} routes · {df_full['category'].nunique()} categories
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state["added_feedback"]:
        st.markdown(
            f"<div style='font-size:0.78rem;color:#6ee7b7;margin-top:6px;'>+"
            f"{len(st.session_state['added_feedback'])} added this session</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    if st.button("🔄 Retrain Model", help="Force retrain the classifier"):
        with st.spinner("Retraining…"):
            df_base = load_base_data()
            metrics = retrain_model(df_base)
            load_pipeline.clear()
        st.success("Model retrained!")


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 – Overview Dashboard
# ════════════════════════════════════════════════════════════════════════════

def page_overview():
    df = get_analyzed_df()

    st.markdown(
        """
        <div class="page-title">📊 Overview Dashboard</div>
        <div class="page-subtitle">
          Overview of passenger feedback across all routes and categories.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI row
    total = len(df)
    neg_pct = round((df["sentiment"] == "Negative").sum() / max(total, 1) * 100, 1)
    pos_pct = round((df["sentiment"] == "Positive").sum() / max(total, 1) * 100, 1)
    top_issue = df["category"].value_counts().index[0] if total else "N/A"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Feedback", total, help="All records including session additions")
    c2.metric("Negative Feedback", f"{neg_pct}%", delta=None)
    c3.metric("Positive Feedback", f"{pos_pct}%")
    c4.metric("Top Reported Issue", top_issue)

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Sentiment donut
    with col_l:
        sent_counts = df["sentiment"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_donut = px.pie(
            sent_counts, names="Sentiment", values="Count",
            hole=0.52,
            color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            title="Sentiment Distribution",
        )
        fig_donut.update_traces(textinfo="percent+label", pull=[0.03] * len(sent_counts))
        fig_donut.update_layout(
            showlegend=True,
            margin=dict(t=50, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"),
            title_font=dict(size=16, family="Inter"),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Category bar
    with col_r:
        cat_counts = df["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig_bar = px.bar(
            cat_counts.sort_values("Count"),
            x="Count", y="Category",
            orientation="h",
            title="Feedback by Issue Category",
            color="Count",
            color_continuous_scale=["#bae6fd", "#0891b2", "#0e4f6b"],
        )
        fig_bar.update_layout(
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(t=50, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis_title="",
            xaxis_title="Number of Feedback Records",
            font=dict(family="Inter"),
            title_font=dict(size=16, family="Inter"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Recent feedback table
    st.markdown("### 📋 Recent Feedback")
    recent = df.tail(15)[["feedback", "route", "date", "category", "sentiment"]].copy()
    recent["sentiment"] = recent["sentiment"].apply(
        lambda s: f"🟢 {s}" if s == "Positive" else (f"🔴 {s}" if s == "Negative" else f"🟡 {s}")
    )
    st.dataframe(recent[::-1], use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 – Analyze Feedback
# ════════════════════════════════════════════════════════════════════════════

def page_analyze():
    st.markdown(
        """
        <div class="page-title">🔍 Analyze Feedback</div>
        <div class="page-subtitle">
          Enter passenger feedback below to get instant NLP analysis.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("feedback_form", clear_on_submit=False):
        user_text = st.text_area(
            "Passenger Feedback",
            placeholder="e.g. The bus was 20 minutes late and smelled terrible. Very disappointed.",
            height=130,
        )
        route_input = st.text_input(
            "Route / Location (optional)",
            placeholder="e.g. Route 12A, Central Station",
        )
        submitted = st.form_submit_button("🔍 Analyze Feedback", use_container_width=True)

    if submitted:
        if not user_text or not user_text.strip():
            st.error("⚠️ Please enter some feedback text before analyzing.")
            return

        pipeline = load_pipeline(len(get_full_df()))

        with st.spinner("Analyzing…"):
            cls_result  = classify_feedback(user_text, pipeline)
            sent_result = analyze_sentiment(user_text)
            phrases     = extract_phrases(user_text, top_n=6)

        # ── Result cards
        st.markdown("---")
        st.markdown("#### 📊 Analysis Results")

        r1, r2, r3 = st.columns(3)

        with r1:
            conf_pct = round(cls_result["confidence"] * 100, 1)
            conf_bar = "█" * int(conf_pct / 10) + "░" * (10 - int(conf_pct / 10))
            st.markdown(
                f"""
                <div class="tv-card">
                  <div style="font-size:0.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">Issue Category</div>
                  <div style="font-size:1.25rem;font-weight:700;color:#0f172a;">{cls_result['label']}</div>
                  <div style="margin-top:10px;">
                    <span class="badge-category">Confidence: {conf_pct}%</span>
                  </div>
                  <div style="font-size:0.75rem;color:#94a3b8;margin-top:8px;font-family:monospace;">{conf_bar}</div>
                  <div style="font-size:0.72rem;color:#94a3b8;margin-top:4px;font-style:italic;">
                    Prototype classifier — confidence is indicative only
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with r2:
            sent_label = sent_result["label"]
            sent_color = {"Positive":"#22c55e","Negative":"#ef4444","Neutral":"#f59e0b"}[sent_label]
            badge_cls  = f"badge-{sent_label.lower()}"
            compound   = sent_result["compound"]
            st.markdown(
                f"""
                <div class="tv-card">
                  <div style="font-size:0.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">Sentiment</div>
                  <div style="font-size:1.25rem;font-weight:700;color:{sent_color};">{sent_label}</div>
                  <div style="margin-top:10px;">
                    <span class="{badge_cls}">Compound: {compound:+.3f}</span>
                  </div>
                  <div style="font-size:0.78rem;color:#64748b;margin-top:8px;">
                    Pos: {sent_result['pos']:.2f} &nbsp;|&nbsp;
                    Neu: {sent_result['neu']:.2f} &nbsp;|&nbsp;
                    Neg: {sent_result['neg']:.2f}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with r3:
            chips = " ".join([f'<span class="chip">#{p}</span>' for p in phrases]) if phrases else "<em style='color:#94a3b8'>No distinctive phrases found.</em>"
            st.markdown(
                f"""
                <div class="tv-card">
                  <div style="font-size:0.78rem;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:6px;">Key Phrases</div>
                  <div style="margin-top:6px;">{chips}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ── Interpretation
        interp = _interpret(cls_result, sent_result)
        st.info(f"💬 **Interpretation:** {interp}")

        # ── Top category probabilities
        with st.expander("📈 Category Probability Breakdown"):
            probs = cls_result.get("probabilities", {})
            if probs:
                prob_df = pd.DataFrame(
                    sorted(probs.items(), key=lambda x: -x[1]),
                    columns=["Category", "Probability"]
                )
                fig_prob = px.bar(
                    prob_df, x="Probability", y="Category",
                    orientation="h",
                    color="Probability",
                    color_continuous_scale=["#bae6fd","#0891b2","#0e4f6b"],
                    range_x=[0, 1],
                )
                fig_prob.update_layout(
                    coloraxis_showscale=False,
                    yaxis_title="", margin=dict(t=20,b=20,l=10,r=10),
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Inter"),
                )
                st.plotly_chart(fig_prob, use_container_width=True)

        # ── Add to dashboard
        st.markdown("---")
        st.markdown("#### ➕ Add to Dashboard")
        if st.button("Add this feedback to the session dashboard"):
            # Check for duplicate (same text already added this session)
            already = any(
                r.get("feedback") == user_text.strip()
                for r in st.session_state["added_feedback"]
            )
            if already:
                st.warning("This feedback has already been added to the session.")
            else:
                from datetime import date
                st.session_state["added_feedback"].append({
                    "feedback": user_text.strip(),
                    "route": route_input.strip() if route_input else "Unknown",
                    "date": str(date.today()),
                    "category": cls_result["label"],
                    "sentiment": sent_result["label"],
                    "sentiment_score": sent_result["compound"],
                })
                st.success("✅ Feedback added to the current session dashboard.")


def _interpret(cls_result: dict, sent_result: dict) -> str:
    cat   = cls_result["label"]
    sent  = sent_result["label"]
    conf  = cls_result["confidence"]

    conf_qualifier = "high" if conf > 0.7 else ("moderate" if conf > 0.4 else "low")

    if sent == "Positive":
        return (f"This feedback reads as a positive comment regarding **{cat}**. "
                f"Category classified with {conf_qualifier} confidence ({conf*100:.0f}%). "
                "Positive feedback is valuable for identifying what is working well.")
    elif sent == "Negative":
        return (f"This appears to be a **complaint about {cat}**. "
                f"The classifier assigned this with {conf_qualifier} confidence ({conf*100:.0f}%). "
                "Recommend logging this for follow-up and investigation.")
    else:
        return (f"This feedback is **neutral** in tone and relates to **{cat}**. "
                f"Classified with {conf_qualifier} confidence ({conf*100:.0f}%). "
                "Neutral feedback often contains factual observations worth tracking.")


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 – TransitPulse
# ════════════════════════════════════════════════════════════════════════════

def page_transitpulse():
    df = get_analyzed_df()

    st.markdown(
        """
        <div class="pulse-header">
          <h2>📡 TransitPulse</h2>
          <p>Recurring Issue Detection · Trend Analysis · Actionable Insights</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    insights = get_transitpulse_insights(df)

    if not insights:
        st.warning("Not enough data to compute TransitPulse insights.")
        return

    # ── KPI row
    k1, k2, k3 = st.columns(3)
    k1.metric("Most Reported Issue", insights.get("top_category", "N/A"),
              help=f"{insights.get('top_category_count', 0)} records in dataset")
    k2.metric("Negative Feedback", f"{insights.get('neg_pct', 0)}%",
              help=f"{insights.get('neg_count', 0)} negative records")
    k3.metric("Positive Feedback", f"{insights.get('pos_pct', 0)}%")

    st.markdown("---")
    col1, col2 = st.columns(2)

    # Category frequency chart
    with col1:
        st.markdown("#### 📊 Issue Category Frequency")
        cat_df = insights["category_counts"].reset_index()
        cat_df.columns = ["Category", "Count"]
        fig = px.bar(
            cat_df.sort_values("Count"),
            x="Count", y="Category", orientation="h",
            color="Count",
            color_continuous_scale=["#bae6fd","#0891b2","#0e4f6b"],
            title="All Issues — Frequency",
        )
        fig.update_layout(
            coloraxis_showscale=False, yaxis_title="",
            margin=dict(t=40,b=20,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"), title_font=dict(size=14, family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Negative breakdown chart
    with col2:
        st.markdown("#### 🔴 Negative Feedback Breakdown")
        neg_df = insights["neg_by_category"]
        if len(neg_df) > 0:
            neg_chart = neg_df.reset_index()
            neg_chart.columns = ["Category", "Negative Count"]
            fig2 = px.bar(
                neg_chart.sort_values("Negative Count"),
                x="Negative Count", y="Category", orientation="h",
                color="Negative Count",
                color_continuous_scale=["#fecaca","#ef4444","#991b1b"],
                title="Negative Feedback by Category",
            )
            fig2.update_layout(
                coloraxis_showscale=False, yaxis_title="",
                margin=dict(t=40,b=20,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"), title_font=dict(size=14, family="Inter"),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No negative feedback found in current dataset.")

    # Recurring keywords
    st.markdown("#### 🔑 Recurring Keywords in Negative Feedback")
    kws = insights.get("recurring_keywords", [])
    if kws:
        kw_df = pd.DataFrame(kws, columns=["Keyword", "Frequency"])
        fig3 = px.bar(
            kw_df.sort_values("Frequency"),
            x="Frequency", y="Keyword", orientation="h",
            color="Frequency",
            color_continuous_scale=["#fde68a","#f59e0b","#b45309"],
            title="Top Recurring Words in Negative Feedback",
        )
        fig3.update_layout(
            coloraxis_showscale=False, yaxis_title="",
            margin=dict(t=40,b=20,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"), title_font=dict(size=14, family="Inter"),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No recurring keywords identified.")

    # Trend comparison
    st.markdown("#### 📈 Trend Comparison (First vs Last Week)")
    if insights.get("trend_available"):
        w1_label, w2_label = insights["trend_weeks"]
        trend = insights["trend"]
        trend_rows = []
        for cat, vals in trend.items():
            direction = "↑" if vals["delta"] > 0 else ("↓" if vals["delta"] < 0 else "→")
            trend_rows.append({
                "Category": cat,
                f"First Week ({w1_label})": vals["first_week"],
                f"Last Week ({w2_label})": vals["last_week"],
                "Change": f"{direction} {abs(vals['delta'])}",
            })
        if trend_rows:
            st.dataframe(pd.DataFrame(trend_rows), use_container_width=True, hide_index=True)
    else:
        st.info(
            "ℹ️ Temporal trend comparison requires at least two distinct weeks of dated data. "
            "Not enough variation in the current dataset to compute a meaningful trend."
        )

    # Recommendations
    st.markdown("---")
    st.markdown("#### 💡 Suggested Actions")
    tag_map = {
        "[HIGH]":        ("🚨", "#dc2626"),
        "[ACTION]":      ("🔴", "#ef4444"),
        "[DELAYS]":      ("🕐", "#0891b2"),
        "[CLEANLINESS]": ("🧹", "#0e7490"),
        "[SAFETY]":      ("🔒", "#7c3aed"),
        "[ACCESS]":      ("♿", "#0f766e"),
        "[STAFF]":       ("👥", "#be185d"),
        "[CAPACITY]":    ("🚌", "#1e40af"),
        "[OK]":          ("✅", "#16a34a"),
    }
    for rec in insights.get("recommendations", []):
        icon = "💡"
        color = "#0891b2"
        display_rec = rec
        for tag, (t_icon, t_color) in tag_map.items():
            if rec.startswith(tag):
                icon = t_icon
                color = t_color
                display_rec = rec[len(tag):].strip()
                break
        st.markdown(
            f"<div class='tv-card' style='border-left:4px solid {color};'>"
            f"<span style='font-size:1.15rem;margin-right:8px;'>{icon}</span>"
            f"{display_rec}</div>",
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 – Route Insights
# ════════════════════════════════════════════════════════════════════════════

def page_route_insights():
    df = get_analyzed_df()

    st.markdown(
        """
        <div class="page-title">🗺️ Route & Service Insights</div>
        <div class="page-subtitle">
          Filter and compare passenger feedback across routes, categories, and sentiment.
          <em>Sample data only — not live transport tracking.</em>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Filters
    all_routes = sorted(df["route"].dropna().unique().tolist())
    all_cats   = sorted(df["category"].dropna().unique().tolist())
    all_sents  = ["Positive", "Neutral", "Negative"]

    with st.expander("🔽 Filters", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        sel_routes = fc1.multiselect("Route / Location", all_routes, placeholder="All routes")
        sel_cats   = fc2.multiselect("Issue Category",   all_cats,   placeholder="All categories")
        sel_sents  = fc3.multiselect("Sentiment",        all_sents,  placeholder="All sentiments")

    filtered = filter_data(
        df,
        routes=sel_routes or None,
        categories=sel_cats or None,
        sentiments=sel_sents or None,
    )

    if filtered.empty:
        st.warning("No feedback matches the selected filters. Try adjusting or clearing the filters.")
        return

    st.markdown(f"**{len(filtered)}** records match the current filters.")
    st.markdown("---")

    col1, col2 = st.columns(2)

    # Route-wise negative feedback comparison
    with col1:
        route_summary = get_route_summary(filtered)
        if not route_summary.empty:
            fig = px.bar(
                route_summary.sort_values("negative"),
                x="negative", y="route", orientation="h",
                color="neg_pct",
                color_continuous_scale=["#bbf7d0","#ef4444","#7f1d1d"],
                hover_data={"total": True, "negative": True, "neg_pct": True},
                labels={"negative": "Negative Reports", "route": "Route", "neg_pct": "% Negative"},
                title="Negative Feedback by Route",
            )
            fig.update_layout(
                coloraxis_colorbar_title="% Neg",
                margin=dict(t=50,b=20,l=10,r=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter"), title_font=dict(size=14, family="Inter"),
            )
            st.plotly_chart(fig, use_container_width=True)

    # Category distribution for filtered set
    with col2:
        cat_counts = filtered["category"].value_counts().reset_index()
        cat_counts.columns = ["Category", "Count"]
        fig2 = px.pie(
            cat_counts, names="Category", values="Count",
            hole=0.4,
            color_discrete_sequence=CATEGORY_COLORS,
            title="Issue Categories (Filtered)",
        )
        fig2.update_traces(textinfo="percent+label")
        fig2.update_layout(
            margin=dict(t=50,b=20,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter"), title_font=dict(size=14, family="Inter"),
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Filtered feedback table
    st.markdown("#### 📋 Filtered Feedback")
    display_cols = [c for c in ["feedback","route","date","category","sentiment","sentiment_score"] if c in filtered.columns]
    st.dataframe(filtered[display_cols].reset_index(drop=True), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 – Reports
# ════════════════════════════════════════════════════════════════════════════

def page_reports():
    df = get_analyzed_df()

    st.markdown(
        """
        <div class="page-title">📄 Reports & Export</div>
        <div class="page-subtitle">
          Download analyzed feedback as a CSV file for further review.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Filters
    all_routes = sorted(df["route"].dropna().unique().tolist())
    all_cats   = sorted(df["category"].dropna().unique().tolist())
    all_sents  = ["Positive", "Neutral", "Negative"]

    with st.expander("🔽 Filter Report", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        sel_routes = fc1.multiselect("Route / Location", all_routes, placeholder="All routes", key="rep_routes")
        sel_cats   = fc2.multiselect("Issue Category",   all_cats,   placeholder="All categories", key="rep_cats")
        sel_sents  = fc3.multiselect("Sentiment",        all_sents,  placeholder="All sentiments", key="rep_sents")

    filtered = filter_data(
        df,
        routes=sel_routes or None,
        categories=sel_cats or None,
        sentiments=sel_sents or None,
    )

    if filtered.empty:
        st.warning("No records match the selected filters.")
        return

    report_df = prepare_report(filtered)
    st.markdown(f"**{len(report_df)}** records in report.")
    st.dataframe(report_df.reset_index(drop=True), use_container_width=True, hide_index=True)

    # ── CSV download
    csv_buffer = io.StringIO()
    report_df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue().encode("utf-8")

    st.download_button(
        label="⬇️ Download Report as CSV",
        data=csv_bytes,
        file_name="transitvoice_report.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown(
        """
        <div style="font-size:0.8rem;color:#94a3b8;margin-top:8px;">
          ⚠️ This report contains synthetic/illustrative data only.
          Session-added feedback is included if you added any this session.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ════════════════════════════════════════════════════════════════════════════
# Router
# ════════════════════════════════════════════════════════════════════════════

# Ensure dataset and model exist on first run
with st.spinner("Loading TransitVoice…"):
    _df_init = load_base_data()
    load_pipeline(len(_df_init))

if page_name == "Overview":
    page_overview()
elif page_name == "Analyze Feedback":
    page_analyze()
elif page_name == "TransitPulse":
    page_transitpulse()
elif page_name == "Route Insights":
    page_route_insights()
elif page_name == "Reports":
    page_reports()
