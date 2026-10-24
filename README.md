# WebSystemSE

================================================================================
LEXIMETRIX: MULTILINGUAL NLP FEEDBACK EVALUATION ENGINE
COMPREHENSIVE THESIS TEAM GUIDE, SYSTEM FLOW & TECHNICAL DOCUMENTATION
================================================================================

1. EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
LexiMetrix is a web-based Multilingual Natural Language Processing (NLP) and
Aspect-Based Sentiment Analysis (ABSA) platform designed to evaluate bilingual
(English, Tagalog, and Taglish) student feedback within the Department of
Computing and Informatics (DCI), covering BSCS and BSIT programs.

Traditional student evaluations rely heavily on numerical Likert ratings while
leaving hundreds of open-ended narrative comments unanalyzed due to manual
reading bottlenecks and the linguistic complexity of code-switched Taglish
(such as prefixation, intensifiers, negations, and slang sarcasm like "eme" or
"charot"). LexiMetrix solves this by combining a transformer-based model
(cardiffnlp/twitter-xlm-roberta-base-sentiment) with a custom rule-based
Taglish lexical-morphological engine.

The system features two interconnected workspaces:
  1. Student Feedback & Community Portal (/student-portal): A participatory
     Town Hall forum and Formal Survey hub where students submit 100% anonymous
     evaluations, preview AI sentiment before posting, vote on peer concerns,
     and track official leadership resolutions.
  2. Quantitative Analytics & Oversight Dashboard (/dashboard): An executive
     command center that converts raw narratives into real-time KPIs, aspect
     bar charts, polarity doughnut charts, explainable word-weight logs ("Why
     Positive / Why Negative"), automated prescriptive alerts, batch CSV
     ingestion, and a 3x3 Confusion Matrix / F1-Score validation suite.


================================================================================
2. END-TO-END SYSTEM FLOW (HOW THE SYSTEM WORKS)
================================================================================

STEP 1: INSTITUTIONAL REGISTRATION & OTP AUTHENTICATION
  - Users register at /signup using an official institutional email address
    (@ccc.edu.ph), selecting their role (Student - Regular, Student - Officer,
    or Faculty) and degree program(s) (BSCS, BSIT).
  - Users must accept the RA 10173 Data Privacy Consent Notice before account
    creation.
  - The system generates a cryptographically secure 6-digit One-Time Passcode
    (OTP), hashes it using HMAC-SHA256 with the server secret key (10-minute
    expiry, max 5 attempts), and dispatches it via the Brevo HTTPS API.
  - Pre-seeded Developer accounts (hjraymundo, apmalacaman, msmorata) are
    provisioned automatically at startup using scrypt password hashes.

STEP 2: ROLE-BASED ROUTING & SESSION SECURITY
  - Upon login (/login), brute-force protection enforces a 10-minute lockout
    after 5 consecutive failed password attempts.
  - Successful logins are recorded in the audit table (user_login_logs) and
    routed based on role clearance:
      * Student - Regular & Student - Officer -> /student-portal
      * Faculty & Developer                   -> /dashboard (with seamless
        navigation to /student-portal and back via the floating dashboard pill)
  - Strict browser cache lockouts (no-store, no-cache, Clear-Site-Data on
    sign-out, and Back-Forward Cache ping guards) prevent unauthorized session
    restoration on shared laboratory PCs.

STEP 3: FEEDBACK INGESTION (3 DATA SOURCES)
  LexiMetrix ingests student narratives from three distinct sources:
  1. Portal Submissions (source="Portal"):
     - Town Hall Posts: Open community feedback posted to Campus-Wide or DCI
       channels. Students can toggle "Preview AI Analysis" (/api/inspect_preview)
       to inspect how the AI scores their text before publishing.
     - Formal Surveys: Structured evaluations created by Officers, Faculty, or
       Developers containing Likert (1-5) scales (with conditional follow-up
       elaboration boxes on low ratings), single-choice radio buttons,
       checkboxes, and open narrative prompts.
  2. Batch CSV Imports (source="CSV"):
     - Developers upload historical or external evaluation spreadsheets (.csv).
     - The importer auto-detects encoding (UTF-8 / CP1252), maps columns
       (Program, Academic_Year, Semester, Feedback) with smart fallback
       defaults, deduplicates rows, processes records in 40-row chunks, and
       supports 1-click batch rollback (/api/import/<batch_id>/rollback).
  3. Benchmark & Diagnostic Testing (source="Testing"):
     - Developers can run single-sentence diagnostic tests or seed the 30-item
       Taglish Gold Benchmark suite for model validation.

STEP 4: PRIVACY SCRUBBING & PROFANITY MASKING
  - Anonymity Decoupling: Survey submissions store completion flags in
    form_response_records (to enforce 1-response-per-student) while storing
    actual answers separately in form_anonymous_submissions with timestamps
    rounded to the hour/day to prevent timing-correlation attacks.
  - Automated PII Scrubbing (scrub_pii): Regex filters automatically mask
    emails ([email hidden]), Philippine mobile numbers ([number hidden]),
    student IDs ([ID hidden]), social handles ([handle hidden]), and
    self-introductions ("My name is...", "Ako po si..." -> [self-introduction
    hidden]).
  - Profanity Handling (mask_profanity): Leet-speak-aware regex detects English,
    Tagalog, and Cebuano profanity. The AI reads the raw profanity first as a
    1.5x emotional intensifier, then permanently masks the stored/displayed
    word (e.g., "p*******a") and flags has_profanity=True.

STEP 5: HYBRID NLP & ASPECT-BASED SENTIMENT ANALYSIS (ABSA) PIPELINE
  Every narrative comment passes through run_absa_pipeline():
  1. Preprocessing: Lowercases text, strips URLs and special symbols, and
     normalizes whitespace (up to 2,000 characters).
  2. Compound Clause Segmentation: Splits multi-thought sentences at punctuation
     and bilingual contrastive conjunctions ("but", "pero", "kaso", "kaso lang",
     "however", "although", "while", "yet") into up to 12 distinct clauses.
  3. Aspect Categorization: Maps each clause via keyword boundaries to one of
     four institutional dimensions:
       * Instructional Delivery & Pedagogy (lecture, turo, explain, pacing, quiz)
       * Faculty Demeanor & Approachability (mabait, approachable, sungit, prof)
       * Campus Facilities & Infrastructure (room, aircon, mainit, wifi, lab, pc)
       * General Academic Feedback (fallback category)
  4. Hybrid Clause Scoring (evaluate_clause):
     - Transformer Baseline: Queries cardiffnlp/twitter-xlm-roberta-base-sentiment.
     - Morphological Stemming: Strips Tagalog affixes (napaka-, pinaka-, nakaka-,
       nag-, mag-, ma-, -ng, -an, -han, -in) and English suffixes (-ing, -ed, -ly).
     - Lexical Token Scoring:
         * Positive match: +1.0 base score
         * Negative match: -1.0 base score
         * Intensifier ("sobrang", "napaka", "very", "super"): Sets a 1.5x
           multiplier on the next sentiment token.
         * Negator ("hindi", "di", "wala", "walang", "not", "never", "dont"):
           Inverts a following Positive token to negative (-1.0 or -1.5) and
           softens an inverted Negative token (+0.5).
         * Deprivation Rule: Existential negators ("walang wifi", "no aircon")
           without a following adjective resolve to -1.0 * intensifier.
         * Sarcasm Invalidator: Slang irony markers ("eme", "charot", "charing",
           "joke") immediately override clause and overall polarity to Negative
           (-1.5 lexical impact, >= 92% confidence).
  5. Document-Level Aggregation & Explainability:
     - Computes overall polarity by majority clause vote (breaking ties via net
       lexical score sum) and averages clause confidence scores.
     - Generates a human-readable "Why Positive / Why Negative / Why Neutral"
       explanation citing the exact trigger words, scores, and aspect category.

STEP 6: QUANTITATIVE SYNTHESIS, PRESCRIPTIVE ALERTS & VALIDATION
  - Dashboard KPIs & Charts: Computes total, positive, negative, and neutral
    counts, 3-class vs. binary (Pos vs. Neg Only) percentages, and renders
    high-DPI Matplotlib doughnut and aspect bar charts.
  - Prescriptive Action Alerts: If any aspect accumulates >= 3 mentions with a
    Negative ratio >= 40%, the system triggers a targeted alert:
      * Facilities >= 40% Neg  -> "Community Action Alert" (General Services)
      * Pedagogy >= 40% Neg    -> "Pedagogical Dialogue Request" (Syllabus Pacing)
      * Demeanor >= 40% Neg    -> "Student Welfare Advisory" (Faculty Rapport)
  - Ground-Truth Override & Confusion Matrix: Developers can confirm or override
    any record's AI sentiment, feeding the live 3x3 Confusion Matrix, Precision,
    Recall, Macro-F1, and Weighted-F1 evaluation modal.


================================================================================
3. COMPLETE FEATURE SUITE BY MODULE
================================================================================

A. ANALYTICS & OVERSIGHT DASHBOARD (/dashboard)
  - Toggleable Quick Workspace Sidebar (Alt + S): Slide-over navigation drawer
    with Pin/Unpin support so the main workspace stays 100% uncluttered.
  - Data Source Integrity Tabs: Switch between All Evaluated Sources, Portal
    Submissions, Imported CSVs, and Benchmark & Testing Logs.
  - Program & Polarity Filters: Filter by All Programs, BSCS, or BSIT (Faculty
    are automatically scoped to their assigned program), filter by sentiment,
    or toggle "Pos vs. Neg Only" (Actionable Binary Mode).
  - Total Summary of Evaluated Responses Card: Synthesizes an executive
    narrative paragraph and opens a full modal with breakdowns by Program,
    Aspect, Academic Term, plus an interactive Custom Summary Builder.
  - Explainable Feedback Logs Table: Highlights positive words in green,
    negative words in red, intensifiers in amber, and negators/sarcasm in
    violet right inside the sentence, paired with a "Why Positive / Negative"
    banner and a click-to-open AI Sentiment Inspector modal.
  - Recurring Lexicon Keyword Cloud: Extracts top bilingual vocabulary; clicking
    any word chip filters the feedback table immediately.
  - Dynamic Taglish Slang Manager: Allows Developers to add or delete positive,
    negative, intensifier, negation, or profanity terms live without redeployment.
  - AI Evaluation (F1 & Confusion Matrix) Modal: Computes live multi-class
    Accuracy, Macro Precision, Macro Recall, Macro F1, and Weighted F1 on
    Human-Verified records or the 30-item Taglish Gold Benchmark.

B. STUDENT FEEDBACK & COMMUNITY PORTAL (/student-portal)
  - Department Community Pulse: Live voice tally bar showing total voices,
    commendation %, grievance %, and active survey count.
  - Participatory Town Hall Feed: Supports Campus-Wide, Official Announcements,
    and DCI channels, image attachments (drag-and-drop or URL), reference links,
    upvote/downvote consensus scoring, and pre-flight AI Sentiment Preview.
  - Paginated Discussion Comments: Each post features a collapsible comment
    thread paginated at 5 comments per page (with Prev/Next and page numbers).
    Developers can moderate inappropriate comments, replacing them with
    "This comment has been deleted".
  - Duty-Bearer Resolution Tracking: Officers, Faculty, and Developers can mark
    student concerns as "Under Review" or "Action Taken" with an official note
    that students can react to (thumbs up/down).
  - Google-Forms-Style Survey Builder & Manager: Multi-question builder
    supporting Open Text, Likert (1-5) with conditional follow-up logic,
    Single Choice, and Checkboxes; custom theme colors, fonts, and header
    banners; cutoff deadlines, response quotas, shareable links (/s/<token>),
    and private per-survey analytics with CSV export.


================================================================================
4. ESSENTIAL INFORMATION FOR WRITING THE THESIS PAPER
================================================================================

A. MATHEMATICAL FORMULAS (FOR CHAPTER 3: METHODOLOGY)
  1. Effective Lexical Token Score (w_i):
       w_i = b_i * I_i * N_i
     Where:
       - b_i in {+1.0, -1.0, 0.0} is the base polarity of token i.
       - I_i = 1.5 if preceded by an intensifier token, else 1.0.
       - N_i = -1.0 if preceded by a negator before a positive token (or -0.5
         when softening a negative token), else 1.0.

  2. Clause Net Lexical Score (L_c):
       L_c = sum(w_i for i in clause) - (1.5 if sarcasm_detected else 0)

  3. Multi-Class Evaluation Metrics (for class c in {Positive, Neutral, Negative}):
       Accuracy        = (TP_pos + TP_neu + TP_neg) / N_total
       Precision_c     = TP_c / (TP_c + FP_c)
       Recall_c        = TP_c / (TP_c + FN_c)
       F1_c            = (2 * Precision_c * Recall_c) / (Precision_c + Recall_c)
       Macro_F1        = (F1_Pos + F1_Neu + F1_Neg) / 3
       Weighted_F1     = sum(Support_c * F1_c) / N_total

  4. Actionable Binary Share (Excluding Neutral Remarks):
       Binary_Pos_%    = (N_Pos / (N_Pos + N_Neg)) * 100
       Binary_Neg_%    = (N_Neg / (N_Pos + N_Neg)) * 100

B. DATABASE SCHEMA / ENTITY-RELATIONSHIP SUMMARY (14 TABLES)
  1. users                      : Institutional accounts, roles, scrypt/pbkdf2 hashes, OTP state, lockout timers, RA 10173 consent timestamp.
  2. user_login_logs            : Security audit trail (user_id, role, IP, user_agent, login_time).
  3. academic_years             : Registered school year cycles (e.g., 2024-2025, 2025-2026, 2026-2027).
  4. system_settings            : Key-value store for active_academic_year and active_semester.
  5. evaluation_forms           : Formal survey definitions, targeting (program/section/subject), quotas, deadlines, questions_json, theme_json, share_token.
  6. form_response_records      : Tracks which student_id completed which form_id (prevents duplicate submissions while keeping answers anonymous).
  7. form_anonymous_submissions : Decoupled JSON survey responses (answers_json) with zero foreign key to users.
  8. feedback_records           : Core ABSA table storing raw_text, cleaned_text, sentiment, ai_sentiment, human_sentiment, confidence, aspect_breakdown JSON, source, import_batch, has_profanity.
  9. import_batches             : Tracks CSV uploads (filename, SHA-256 hash, row counts, status) for 1-click rollback.
  10. community_posts           : Town Hall posts & pinned announcements, category, sentiment, score, resolution status, action_note.
  11. community_post_votes      : Upvote (+1) / Downvote (-1) records per user per post.
  12. community_resolution_votes: Student approval/disapproval reactions on official resolution notes.
  13. community_comments        : Anonymous discussion replies on Town Hall posts.
  14. lexicon_terms             : Dynamic Taglish dictionary words categorized as positive, negative, intensifiers, negations, or profanity.

C. DATA PRIVACY & SECURITY COMPLIANCE (RA 10173 / ISO 25010 SECURITY)
  - Informed Consent: Explicit RA 10173 modal and checkbox required at sign-up.
  - Identity Decoupling: Survey answers (form_anonymous_submissions) and
    sentiment records (feedback_records) store no student user_id.
  - k-Anonymity (Small-Group Suppression): When fewer than MIN_ANON_GROUP (default
    5) responses match a filter or survey, detailed results and CSV exports are
    automatically suppressed for non-Developer users so individual respondents
    cannot be deduced.
  - Automated PII & Profanity Scrubbing: Masks accidental self-identification
    and offensive language before storage/display.
  - Timestamp Coarsening: Survey feedback timestamps are rounded to the hour
    and attendance records to the day.

D. PROJECT FILE STRUCTURE
  - app.py                      : Main Flask application, SQLAlchemy models, Brevo OTP mailer, Hybrid XLM-RoBERTa + Taglish ABSA engine, Matplotlib chart generator, and REST APIs.
  - templates/auth.html         : Sliding Sign-In / Sign-Up portal, RA 10173 modal, 6-digit OTP verification, and Password Recovery UI.
  - templates/dashboard.html    : Quantitative Analytics Dashboard, Quick Workspace sidebar, Total Summary & Custom Summary Builder, AI Inspector, CSV Importer, Slang Manager, and F1 Confusion Matrix modal.
  - templates/student_portal.html: Student Voice Collective, Community Pulse, Town Hall feed, Formal Surveys hub, Survey Builder, and Binary Code-to-Logo SVG morph.
  - static/student_portal.js    : Frontend logic for Town Hall posts, AI preview, paginated comments, survey builder/renderer, theme customizer, and owner analytics.
  - static/student_portal.css   : Responsive dark/light glassmorphism stylesheet for the Student Portal.
  - static/tour.js & tour.css   : Interactive spotlight guided tour engine for both portals.
  - static/leximetrix-logo.svg  : Animated binary-green (0101) code-to-logo SVG crest.
================================================================================
