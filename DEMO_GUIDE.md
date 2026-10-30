# TransitVoice — Project Demonstration & Viva Guide 🚌

Use this guide step-by-step during your project demonstration to your teacher/examiner.

---

## 1. Quick 30-Second Elevator Pitch (What to Say First)

> *"Good morning/afternoon Ma'am/Sir. My project is **TransitVoice: AI-Powered Public Transport Feedback Analyzer**.
> Public transit authorities receive thousands of unstructured passenger grievances across buses and metros. Manually reviewing them is slow and prone to overlooking recurring issues.
> TransitVoice uses an end-to-end NLP pipeline to automatically clean feedback, classify it into 8 transport domains using TF-IDF and Logistic Regression, compute sentiment polarity using VADER, extract key phrases, and surface recurring operational bottlenecks through our USP feature called **TransitPulse**."*

---

## 2. Step-by-Step Live Demonstration Flow

### Step 1: Overview Dashboard (`📊 Overview`)
* **What to Show on Screen:**
  - Point to the **KPI Cards** at the top: Total Feedback (168 records), Negative Feedback (39.3%), Positive Feedback (36.9%), Top Reported Issue (Overcrowding).
  - Point to the **Sentiment Distribution (Donut Chart)**: Positive (green), Neutral (yellow), Negative (red).
  - Point to the **Feedback by Issue Category (Bar Chart)**: Show the realistic distribution — Overcrowding (38) and Cleanliness (34) are high, Delays (24) and Safety (21) are moderate.
* **What to Say:**
  > *"Here on the Overview Dashboard, the system provides high-level operational metrics. We can see sentiment breakdowns and identify that overcrowding and cleanliness represent the majority of passenger feedback."*

---

### Step 2: Live Feedback Analyzer (`🔍 Analyze Feedback`)
* **What to Show on Screen:**
  1. Type or paste a realistic complaint into the text area:
     > `"The bus was 30 minutes late and the driver was extremely rude to an elderly commuter."`
  2. Enter Route: `Route 12A`
  3. Click **"🔍 Analyze Feedback"**.
  4. Show the 3 result cards:
     - **Issue Category:** `Delays and Punctuality` / `Staff Behaviour` with confidence percentage.
     - **Sentiment:** `Negative` (with exact compound score e.g., `-0.65`).
     - **Key Phrases:** Extracted bigrams like `#extremely rude`, `#elderly commuter`.
  5. Expand the **"Category Probability Breakdown"** to show the model's confidence distribution across all 8 classes.
  6. Click **"Add this feedback to the session dashboard"** and show that it dynamically updates session records.
* **What to Say:**
  > *"In the Live Analyzer, commuters or operators can enter any unseen feedback. The NLP pipeline pre-processes the text, extracts TF-IDF n-grams, predicts the category with a probability distribution, calculates a VADER compound sentiment score, and extracts key complaint phrases—all locally in real time."*

---

### Step 3: TransitPulse (`📡 TransitPulse` — The Main USP ⭐)
* **What to Show on Screen:**
  - Show the **Negative Feedback Breakdown** and the **Top Recurring Words in Negative Feedback** (e.g., *crowded, dirty, delay, late, broken*).
  - Show the **Suggested Actions** cards with color-coded alerts (`🚨`, `🔴`, `🕐`, `🧹`, `🔒`).
* **What to Say:**
  > *"This is our USP: **TransitPulse**. Instead of just analyzing individual sentences, TransitPulse aggregates the entire dataset to detect systemic, recurring complaints. It mines recurring negative keywords and generates rule-based operational recommendations, such as auditing timetable adherence or increasing bus frequency during peak hours."*

---

### Step 4: Route Insights & Reports (`🗺️ Route Insights` & `📄 Reports`)
* **What to Show on Screen:**
  - Filter by a specific route (e.g., `Route 12A` or `Metro Line 3`) to see route-specific negative feedback.
  - Navigate to **Reports** and show the filtered feedback table and the **"Download Report as CSV"** button.
* **What to Say:**
  > *"Transit managers can filter grievances by route to spot localized problems and export the complete analyzed report as a CSV for administrative records."*

---

## 3. NLP Concepts Used & Where to Find Them in Code

When the teacher asks *"Which NLP techniques did you use and where are they in the code?"*, refer directly to this table:

| NLP Concept | How It Works in TransitVoice | Code Location |
|---|---|---|
| **1. Text Preprocessing & Sanitization** | Converts to lowercase, strips punctuation via regex, but **preserves apostrophes** so negations (`not`, `can't`, `never`) aren't lost. | `nlp_pipeline.py` $\rightarrow$ `preprocess()` (line 42) |
| **2. TF-IDF Feature Extraction** | Computes Term Frequency–Inverse Document Frequency using unigrams & bigrams `(1, 2)`, sublinear TF scaling, and max 5,000 features. | `nlp_pipeline.py` $\rightarrow$ `train_model()` (line 69) |
| **3. Supervised Text Classification** | Multi-class Logistic Regression with `class_weight='balanced'` to classify text into 8 transport categories with confidence scores. | `nlp_pipeline.py` $\rightarrow$ `train_model()` & `classify_feedback()` (line 77, 116) |
| **4. Lexicon-Based Sentiment Analysis** | Uses **VADER** (`SentimentIntensityAnalyzer`) on raw text to calculate Positive/Neutral/Negative labels and compound valence score ($-1$ to $+1$). | `nlp_pipeline.py` $\rightarrow$ `analyze_sentiment()` (line 134) |
| **5. N-Gram & Keyword Extraction** | Filters custom stopwords while extracting salient unigrams and negation bigrams (e.g., `"not clean"`, `"dangerously overcrowded"`). | `nlp_pipeline.py` $\rightarrow$ `extract_phrases()` (line 170) |
| **6. Pattern Mining & Aggregation** | Aggregates category complaint densities, recurring negative tokens, and rule-based insights for TransitPulse. | `data_analysis.py` $\rightarrow$ `get_transitpulse_insights()` (line 33) |

---

## 4. Expected Viva Questions & Best Answers

**Q1: Why did you use TF-IDF + Logistic Regression instead of deep learning (e.g. BERT/LSTM)?**
> *Answer:* *"For a lightweight, interpretable mini-project with a domain-specific dataset, TF-IDF with sublinear scaling and Logistic Regression provides fast, offline training and inference without requiring GPUs, cloud APIs, or heavy dependencies, making it explainable and easy to deploy on any local machine."*

**Q2: Why use VADER for sentiment analysis?**
> *Answer:* *"VADER is specifically designed for social and conversational feedback. It is valence-aware, meaning it handles punctuation (like exclamation marks), capitalization, and degree modifiers (like 'extremely late') without requiring a separate labeled sentiment training set."*

**Q3: Why are Category Classification and Sentiment Analysis separate?**
> *Answer:* *"A passenger can mention delays in a positive or neutral way—for example: 'The schedule change reduced my morning delay.' If category and sentiment were coupled, the system would mistakenly label all delay feedback as negative. Decoupling them allows true dual-axis evaluation."*

**Q4: How does the model handle negations?**
> *Answer:* *"In `preprocess()`, we keep apostrophes and don't aggressively drop stop words before sentiment analysis. Furthermore, we use bigrams `(1, 2)` in TF-IDF, so phrases like 'not clean' or 'never late' are treated as distinct features rather than just isolated words."*
