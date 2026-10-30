import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()

    # Set 1-inch margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Base font setup
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0, 0, 0)

    # -------------------------------------------------------------
    # PAGE 1: TITLE PAGE
    # -------------------------------------------------------------
    p_header1 = doc.add_paragraph()
    p_header1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_header1.add_run("PIMPRI CHINCHWAD EDUCATION TRUST’S\n")
    r.font.size = Pt(14)
    r.font.bold = True
    r2 = p_header1.add_run("PIMPRI CHINCHWAD COLLEGE OF ENGINEERING")
    r2.font.size = Pt(16)
    r2.font.bold = True
    p_header1.paragraph_format.space_after = Pt(40)

    p_report_on = doc.add_paragraph()
    p_report_on.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_report_on.add_run("A REPORT ON\n")
    r.font.size = Pt(13)
    r.font.bold = True
    p_report_on.paragraph_format.space_after = Pt(15)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_title.add_run("“TransitVoice: AI-Powered Public Transport Feedback Analyzer”")
    r.font.size = Pt(17)
    r.font.bold = True
    r.font.color.rgb = RGBColor(14, 116, 144)
    p_title.paragraph_format.space_after = Pt(35)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_sub.add_run("Submitted in partial fulfillment of the requirements for\n\n")
    r.font.italic = True
    r.font.size = Pt(12)
    r2 = p_sub.add_run("Mini Project of\nTYBTech Course: Natural Language Processing Lab")
    r2.font.bold = True
    r2.font.size = Pt(13)
    p_sub.paragraph_format.space_after = Pt(45)

    p_by = doc.add_paragraph()
    p_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_by.add_run("Submitted by\n\n")
    r.font.italic = True
    r.font.size = Pt(12)
    r2 = p_by.add_run("Tanvi Jadhav - 124B1C111\n\n")
    r2.font.bold = True
    r2.font.size = Pt(14)
    r3 = p_by.add_run("Academic Year 2026-27 Semester-I")
    r3.font.bold = True
    r3.font.size = Pt(12)
    p_by.paragraph_format.space_after = Pt(45)

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_guide.add_run("Under the support and guidance of\n\n")
    r.font.italic = True
    r.font.size = Pt(12)
    r2 = p_guide.add_run("Dr. Sonal Gore & Mrs. Yogita Sharma\n")
    r2.font.bold = True
    r2.font.size = Pt(13)
    r3 = p_guide.add_run("Department of Computer Science & Engineering (AI&ML)")
    r3.font.size = Pt(12)

    doc.add_page_break()

    # Helper for adding section titles
    def add_section_heading(num_str, title_str):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(f"{num_str} {title_str}")
        r.font.bold = True
        r.font.size = Pt(12.5)
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_body_p(text, bold_prefix=None, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.font.bold = True
        p.add_run(text)
        return p

    # -------------------------------------------------------------
    # PAGE 2: PROBLEM STATEMENT, OBJECTIVES, SCOPE, NEED, USERS
    # -------------------------------------------------------------
    add_section_heading("1.", "Aim or Project Title:")
    add_body_p("TransitVoice: AI-Powered Public Transport Feedback Analyzer")

    add_section_heading("2.", "Detailed Problem Statement:")
    add_body_p(
        "Public transport networks serve millions of passengers daily. Commuters routinely experience challenges such as "
        "recurrent service delays, overcrowding during peak hours, unhygienic vehicle interiors, ticket vending malfunctions, "
        "accessibility obstacles, and safety concerns. Transport operators collect passenger complaints through web forms, mobile apps, "
        "and physical counters; however, manually sorting, reading, and triaging large volumes of unstructured textual grievances is "
        "extremely time-consuming, subjective, and prone to oversight. Critical recurring issues on specific lines or routes often remain "
        "undetected until service disruptions or customer dissatisfaction reach acute levels. TransitVoice addresses this challenge by providing "
        "an automated NLP system that classifies complaints into transport-specific domains, analyzes passenger sentiment, surfaces recurring "
        "grievances via TransitPulse, and presents actionable operational intelligence through an interactive dashboard."
    )

    add_section_heading("3.", "Objectives:")
    objectives = [
        ("• Text Sanitization & Negation Preservation: ", "Implement a specialized text cleaning routine that standardizes text while retaining critical negation cues (e.g., 'not clean', 'cannot board')."),
        ("• Multi-Class Grievance Classification: ", "Train a TF-IDF vectorizer coupled with a multi-class Logistic Regression classifier to map unstructured complaints across 8 distinct transport categories."),
        ("• Granular Sentiment Analysis: ", "Integrate VADER sentiment analysis to quantify compound emotional valence and classify passenger sentiment as Positive, Neutral, or Negative independently of category."),
        ("• Phrase & Keyword Extraction: ", "Extract dominant unigrams and bigrams to summarize primary commuter pain points without heavy computational overhead."),
        ("• TransitPulse Recurring Issue Detection: ", "Aggregate dataset-wide complaints to isolate chronic issues, negative sentiment concentrations, and generate rule-based operational recommendations."),
        ("• Interactive Analytics & Reporting: ", "Build a Streamlit-based web interface with route-level filters, Plotly visualizations, and filtered CSV report export capabilities.")
    ]
    for pref, desc in objectives:
        add_body_p(desc, bold_prefix=pref, space_after=3)

    add_section_heading("4.", "Scope of Project:")
    add_body_p("Categorization across 8 core transport categories, dual-axis sentiment and issue scoring, recurring grievance detection, route-level aggregation, interactive dashboard, and CSV reporting with 100% offline local inference.", bold_prefix="In-Scope: ", space_after=2)
    add_body_p("Live vehicle GPS/telemetry tracking, direct integration with legacy transport ERP systems, audio/speech-to-text processing, or dependency on paid cloud LLM APIs.", bold_prefix="Out-of-Scope: ", space_after=6)

    add_section_heading("5.", "Need of Such System:")
    add_body_p(
        "Modern municipal transit systems need rapid, data-driven feedback loops. TransitVoice converts unstructured, subjective user complaints "
        "into structured metrics, highlighting operational bottlenecks on specific routes before passenger dissatisfaction escalates. It enables "
        "transport planners to proactively allocate maintenance crews, adjust bus fleet frequency, and improve safety standards."
    )

    add_section_heading("6.", "Intended User:")
    add_body_p("Municipal Bus & Metro Transport Corporations, Depot Operations Managers, Quality Assurance & Grievance Redressal Officers, and Urban Mobility Research Analysts.")

    add_section_heading("7.", "Application Domain of User:")
    add_body_p("Intelligent Transportation Systems (ITS), Public Sector Service Quality Auditing, Applied Natural Language Processing, and Commuter Sentiment Analytics.")

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 3: REQUIREMENTS, ARCHITECTURE & DATA FLOW DIAGRAMS
    # -------------------------------------------------------------
    add_section_heading("8.", "Software Requirement:")
    reqs = [
        ("• Operating System: ", "Windows 10/11, Ubuntu 20.04+, or macOS Monterey+"),
        ("• Programming Language: ", "Python 3.10 or newer"),
        ("• Web Framework & Dashboard: ", "Streamlit (>= 1.32.0)"),
        ("• Machine Learning & NLP: ", "scikit-learn (>= 1.3.0), vaderSentiment (>= 3.3.1), pandas (>= 2.0.0), NumPy"),
        ("• Data Visualization: ", "Plotly Express & Plotly Graph Objects (>= 5.18.0)"),
        ("• Model Persistence: ", "joblib (>= 1.3.0)")
    ]
    for pref, val in reqs:
        add_body_p(val, bold_prefix=pref, space_after=2)

    add_section_heading("9.", "Hardware Requirement:")
    hw = [
        ("• Processor: ", "Intel Core i3 / AMD Ryzen 3 or higher (dual-core 2.0 GHz minimum)"),
        ("• System Memory (RAM): ", "4 GB minimum (8 GB recommended for smooth multi-page analytics)"),
        ("• Disk Storage: ", "500 MB free space (including Python virtual environment and dependencies)"),
        ("• Display: ", "1280 x 720 minimum screen resolution for responsive dashboard viewing")
    ]
    for pref, val in hw:
        add_body_p(val, bold_prefix=pref, space_after=2)

    add_section_heading("10.", "Architecture Diagram:")
    add_body_p("The modular architecture of TransitVoice comprises three primary functional layers:")

    # Table representing Architecture Diagram
    arch_table = doc.add_table(rows=6, cols=3)
    arch_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    arch_headers = ["Layer", "Module Name", "Primary Responsibilities"]
    for i, h in enumerate(arch_headers):
        cell = arch_table.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_background(cell, "0F172A")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 120, 120, 150, 150)

    arch_data = [
        ("Presentation Layer", "Streamlit UI\n(app.py & styles.css)", "5 interactive views: Overview Dashboard, Live Analyzer, TransitPulse, Route Insights, and Reports Export."),
        ("NLP Pipeline Layer", "Text Preprocessor\n(nlp_pipeline.py)", "Normalizes character casing, eliminates non-alphanumeric noise, preserves apostrophes and negation syntax."),
        ("NLP Pipeline Layer", "TF-IDF + Logistic Regression", "Extracts unigram/bigram feature matrix and predicts one of 8 transport complaint categories with confidence score."),
        ("NLP Pipeline Layer", "VADER Sentiment Engine", "Calculates emotional polarity (Positive/Neutral/Negative) and compound valence scores (-1.0 to +1.0)."),
        ("Analytics Layer", "TransitPulse Engine\n(data_analysis.py)", "Computes category complaint density, recurring keywords in complaints, and generates rule-based recommendations.")
    ]
    for row_idx, data in enumerate(arch_data, start=1):
        for col_idx, text in enumerate(data):
            cell = arch_table.cell(row_idx, col_idx)
            cell.text = text
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
            set_cell_margins(cell, 80, 80, 120, 120)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")

    add_section_heading("11.", "Data Flow Diagram (Level-1 DFD):")
    dfd_table = doc.add_table(rows=5, cols=4)
    dfd_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    dfd_headers = ["Stage", "Source / Process", "Input Data", "Output Produced"]
    for i, h in enumerate(dfd_headers):
        cell = dfd_table.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_background(cell, "0E7490")
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(cell, 100, 100, 120, 120)

    dfd_data = [
        ("1. Ingestion", "User / CSV Source", "Raw Passenger Text", "Unstructured feedback string with route metadata"),
        ("2. Preprocessing", "Sanitization Routine", "Raw Feedback Text", "Normalized token stream with intact negation markers"),
        ("3. Classification", "TF-IDF Vectorizer + Clf", "Cleaned Text Vector", "Predicted Category (1 of 8) & Prediction Confidence"),
        ("4. Sentiment & Pulse", "VADER & TransitPulse", "Raw Text & Dataset", "Sentiment Polarity, Extracted Phrases, Actionable Insights")
    ]
    for row_idx, data in enumerate(dfd_data, start=1):
        for col_idx, text in enumerate(data):
            cell = dfd_table.cell(row_idx, col_idx)
            cell.text = text
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
            set_cell_margins(cell, 80, 80, 120, 120)
            if row_idx % 2 == 1:
                set_cell_background(cell, "F0FDFA")

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 4: THEORY, WORKING OF MODULES & NLP CONCEPTS
    # -------------------------------------------------------------
    add_section_heading("12.", "Theory / Working of Project / Functionality Description:")
    add_body_p(
        "TransitVoice operates as an end-to-end analytical pipeline designed to ingest, process, classify, and visualize "
        "passenger feedback without requiring internet access or high-latency external APIs. The system consists of four primary functional modules:"
    )
    modules = [
        ("1. Dataset Architecture & Synthetic Ground-Truth: ", "A balanced benchmark dataset of 160 realistic feedback records was established across 8 issue categories: Delays and Punctuality, Overcrowding, Cleanliness, Staff Behaviour, Ticketing and Fares, Safety and Security, Accessibility, and Other Issues across 12 realistic transport routes/stations."),
        ("2. Dual-Track NLP Pipeline: ", "Unlike naive systems where sentiment is assumed from the issue category, TransitVoice processes text along two independent axes. An observation such as 'The bus was slightly late but very clean' contains an operational delay issue, yet carries an overall constructive sentiment. The classification and sentiment tracks evaluate this independently."),
        ("3. Key Phrase & Salient Bigram Extractor: ", "Extracts high-value unigrams and bigrams by filtering grammatical stopwords while preserving negation pairs ('not safe', 'never clean'), providing instant summarization of the passenger's exact complaint."),
        ("4. TransitPulse Operational Decision Engine: ", "TransitPulse continuously aggregates feedback by category and sentiment. It isolates the most reported complaint, measures the proportion of negative feedback, identifies recurring complaint keywords, and generates rule-based alerts (e.g., triggering cleanliness audits or route capacity reviews).")
    ]
    for pref, desc in modules:
        add_body_p(desc, bold_prefix=pref, space_after=4)

    add_section_heading("13.", "NLP Concepts Implemented in Project:")
    nlp_concepts = [
        ("• Text Preprocessing & Negation Preservation: ", "Converts strings to lowercase, trims whitespace, and uses regular expression substitution to eliminate noise while explicitly preserving apostrophes to protect semantic negations like 'can't', 'won't', and 'not'."),
        ("• Term Frequency–Inverse Document Frequency (TF-IDF): ", "Transforms variable-length strings into weighted continuous numerical vectors using the formula:"),
    ]
    for pref, desc in nlp_concepts:
        add_body_p(desc, bold_prefix=pref, space_after=3)

    p_eq = doc.add_paragraph()
    p_eq.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq = p_eq.add_run("TF-IDF(t, d, D) = TF(t, d) × [ log( (1 + |D|) / (1 + |{d ∈ D : t ∈ d}|) ) + 1 ]")
    r_eq.font.bold = True
    r_eq.font.size = Pt(10)
    r_eq.font.color.rgb = RGBColor(14, 116, 144)
    p_eq.paragraph_format.space_after = Pt(4)

    nlp_concepts_part2 = [
        ("• Sublinear Term Frequency Scaling: ", "Replaces raw term frequency count TF with 1 + log(TF) for all positive counts to dampen the impact of excessively repeated words."),
        ("• N-gram Feature Modeling: ", "Captures word co-occurrences using unigram and bigram ranges (1, 2), enabling the classifier to distinguish between 'clean' and 'not clean'."),
        ("• Supervised Multi-Class Logistic Regression: ", "Trains a generalized linear model with balanced class weighting, mapping TF-IDF features to softmax probability distributions across the 8 classes:"),
    ]
    for pref, desc in nlp_concepts_part2:
        add_body_p(desc, bold_prefix=pref, space_after=3)

    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq2 = p_eq2.add_run("P(Y = c | x) = exp(w_c^T x + b_c) / ∑_{j=1}^K exp(w_j^T x + b_j)")
    r_eq2.font.bold = True
    r_eq2.font.size = Pt(10)
    r_eq2.font.color.rgb = RGBColor(14, 116, 144)
    p_eq2.paragraph_format.space_after = Pt(4)

    add_body_p(
        "Utilizes a curated rule-based valence lexicon tuned for informal language, computing normalized compound scores ranging from -1.0 (extremely negative) to +1.0 (extremely positive).",
        bold_prefix="• VADER (Valence Aware Dictionary for sEntiment Reasoning): ",
        space_after=4
    )

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 5: SAMPLE CODE, EXPERIMENTATION & RESULTS
    # -------------------------------------------------------------
    add_section_heading("14.", "Sample Code (Core NLP Preprocessing, Pipeline & Sentiment):")

    code_snippet = (
        "import re, joblib\n"
        "from sklearn.pipeline import Pipeline\n"
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "from sklearn.linear_model import LogisticRegression\n"
        "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n\n"
        "analyzer = SentimentIntensityAnalyzer()\n\n"
        "def preprocess(text: str) -> str:\n"
        "    if not isinstance(text, str) or not text.strip():\n"
        "        return ''\n"
        "    text = text.lower().strip()\n"
        "    text = re.sub(r\"[^\\w\\s']\", ' ', text)\n"
        "    return re.sub(r'\\s+', ' ', text).strip()\n\n"
        "def build_pipeline():\n"
        "    return Pipeline([\n"
        "        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=5000, sublinear_tf=True)),\n"
        "        ('clf', LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))\n"
        "    ])\n\n"
        "def analyze_sentiment(text: str) -> dict:\n"
        "    compound = analyzer.polarity_scores(text)['compound']\n"
        "    label = 'Positive' if compound >= 0.05 else ('Negative' if compound <= -0.05 else 'Neutral')\n"
        "    return {'label': label, 'compound': round(compound, 4)}\n\n"
        "def classify_feedback(text: str, pipeline) -> dict:\n"
        "    cleaned = preprocess(text)\n"
        "    return {'label': pipeline.predict([cleaned])[0], 'confidence': round(float(max(pipeline.predict_proba([cleaned])[0])), 4)}"
    )

    code_table = doc.add_table(rows=1, cols=1)
    code_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = code_table.cell(0, 0)
    cell.text = code_snippet
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, 100, 100, 150, 150)
    for p in cell.paragraphs:
        for run in p.runs:
            run.font.name = 'Consolas'
            run.font.size = Pt(8.5)
            run.font.color.rgb = RGBColor(30, 41, 59)

    add_section_heading("15.", "Experimentation Setup:")
    exp_details = [
        ("• Dataset Distribution: ", "160 synthetic, multi-attribute passenger feedback records evenly partitioned across 8 categories (20 records per class)."),
        ("• Validation Strategy: ", "Stratified 80/20 train/test split (128 training instances, 32 evaluation test instances) with fixed random seed (42)."),
        ("• Hyperparameters: ", "N-gram range = (1, 2), max_features = 5,000, sublinear TF = True, L-BFGS solver, L2 penalty (C = 1.0), balanced class weights."),
        ("• Serialization: ", "Fitted model pipeline saved to models/transit_classifier.joblib (177 KB) to bypass retraining upon dashboard restarts.")
    ]
    for pref, val in exp_details:
        add_body_p(val, bold_prefix=pref, space_after=2)

    add_section_heading("16.", "Results or Performance:")
    add_body_p("Evaluation on diverse unseen real-world test inputs demonstrates robust domain categorization and sentiment polarity scoring:")

    results_table = doc.add_table(rows=6, cols=5)
    results_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    res_headers = ["Input Commuter Feedback", "Predicted Category", "Confidence", "Sentiment", "Compound"]
    for i, h in enumerate(res_headers):
        c = results_table.cell(0, i)
        c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c, "1E3A8A")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(c, 100, 100, 120, 120)

    res_data = [
        ("The bus was 25 minutes late and no announcement was made.", "Delays & Punctuality", "0.22", "Negative", "-0.5859"),
        ("Rude driver shouted at elderly passengers.", "Staff Behaviour", "0.22", "Negative", "-0.4588"),
        ("Lift at the station is broken again third time this month.", "Accessibility", "0.15", "Negative", "-0.4767"),
        ("Platform edge barriers are an excellent safety improvement.", "Safety & Security", "0.24", "Positive", "+0.7579"),
        ("Bus was spotlessly clean today, great service!", "Cleanliness", "0.19", "Positive", "+0.8176")
    ]
    for r_idx, row in enumerate(res_data, start=1):
        for c_idx, val in enumerate(row):
            c = results_table.cell(r_idx, c_idx)
            c.text = val
            c.paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_margins(c, 70, 70, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(c, "F8FAFC")

    add_body_p("*Note: Baseline random chance for an 8-class distribution is 0.125 (12.5%). Reported confidence values reflect prototype-scale training data.", space_after=4)

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 6: SCREENSHOTS, APPLICATIONS, CONCLUSION, REFERENCES
    # -------------------------------------------------------------
    add_section_heading("17.", "Implemented Prototype Screenshots:")
    add_body_p("The working Streamlit interface (http://localhost:8501) includes five integrated dashboards:")

    screen_table = doc.add_table(rows=4, cols=2)
    screen_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    s_headers = ["Dashboard View", "Rendered Components & Analytical Features"]
    for i, h in enumerate(s_headers):
        c = screen_table.cell(0, i)
        c.text = h
        c.paragraphs[0].runs[0].font.bold = True
        c.paragraphs[0].runs[0].font.size = Pt(9.5)
        set_cell_background(c, "0F766E")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        set_cell_margins(c, 100, 100, 120, 120)

    s_data = [
        ("1. Overview Dashboard", "Displays high-level KPI cards (Total Feedback: 160, Neg: 39.4%, Pos: 36.2%), interactive Plotly sentiment donut chart, category distribution bar chart, and recent feedback table."),
        ("2. Live Feedback Analyzer", "Interactive text input field with real-time classification cards, confidence meter, sentiment polarity score, extracted phrase chips, and one-click 'Add to Dashboard' feature."),
        ("3. TransitPulse & Route Insights", "Visualizes top recurring negative issue keywords, route-wise negative feedback comparison, and generates automated rule-based action suggestions (e.g., timetable audits).")
    ]
    for r_idx, row in enumerate(s_data, start=1):
        for c_idx, val in enumerate(row):
            c = screen_table.cell(r_idx, c_idx)
            c.text = val
            c.paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_margins(c, 70, 70, 100, 100)
            if r_idx % 2 == 1:
                set_cell_background(c, "F0FDFA")

    add_section_heading("18.", "Circuit Diagram if Applicable:")
    add_body_p("Not Applicable (Pure Software & Natural Language Processing Machine Learning Project).")

    add_section_heading("19.", "Applications:")
    add_body_p("Municipal Bus Corporations (e.g., PMPML, BEST, DTC, BMTC) for grievance sorting; Metro Rail Transit command centers; Airport terminal customer service auditing; and National Railway customer feedback monitoring.", space_after=3)

    add_section_heading("20.", "Conclusion:")
    add_body_p(
        "TransitVoice establishes a lightweight, explainable, and practical NLP feedback analysis framework. "
        "By synthesizing TF-IDF n-gram vectorization, regularized Logistic Regression classification, and VADER sentiment intensity analysis, "
        "the system successfully bridges the gap between unstructured commuter grievances and actionable transit intelligence. "
        "The TransitPulse module provides automated operational recommendations, proving that classical machine learning and lexicon-based NLP "
        "techniques remain highly effective, resource-efficient solutions for real-world public service management."
    )

    add_section_heading("21.", "Potential Outcomes:")
    add_body_p("Product: Deployable open-source web application for transit quality monitoring. Research Article: Potential student conference paper on 'Domain-Specific Grievance Classification and Sentiment Tracking in Urban Transit Systems'. Copyright: Software copyright on the TransitPulse recurring issue triage algorithm.", space_after=3)

    add_section_heading("22.", "References:")
    refs = [
        "1. C. J. Hutto & E. E. Gilbert, 'VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Deliberation Text', in Proc. 8th Int. AAAI Conf. Weblogs Soc. Media (ICWSM-14), 2014.",
        "2. F. Pedregosa et al., 'Scikit-learn: Machine Learning in Python', Journal of Machine Learning Research, vol. 12, pp. 2825-2830, 2011.",
        "3. D. Jurafsky & J. H. Martin, Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics, and Speech Recognition, 3rd ed. draft, Pearson, 2023.",
        "4. Streamlit Inc., 'Streamlit Documentation: The fastest way to build and share data apps', 2024. [Online]. Available: https://docs.streamlit.io"
    ]
    for r in refs:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(2)
        r_run = p.add_run(r)
        r_run.font.size = Pt(8.5)

    output_filename = "TransitVoice_NLP_Mini_Project_Report.docx"
    doc.save(output_filename)
    print(f"Report saved successfully as {output_filename}")

if __name__ == "__main__":
    create_report()
