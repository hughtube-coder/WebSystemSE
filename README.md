================================================================================
LEXIMETRIX: MULTILINGUAL NLP FEEDBACK EVALUATION ENGINE
UPDATED THESIS TEAM GUIDE, SYSTEM FLOW & TECHNICAL DOCUMENTATION
================================================================================

1. EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
LexiMetrix (Multilingual NLP Feedback Evaluation Engine) is a full-stack,
cloud-deployed Aspect-Based Sentiment Analysis (ABSA) platform engineered to
evaluate bilingual (English, Tagalog, and code-switched Taglish) student
feedback within the Department of Computing and Informatics (DCI), covering the
Bachelor of Science in Computer Science (BSCS) and Bachelor of Science in
Information Technology (BSIT) programs.

Traditional academic evaluation instruments rely heavily on numerical Likert
scales while leaving hundreds of open-ended qualitative student comments
unanalyzed due to manual reading bottlenecks and the linguistic complexity of
Taglish (including Tagalog affixation, intensifiers, negations, existential
deprivation phrases like "walang wifi", and slang irony markers like "eme" or
"charot"). LexiMetrix resolves this gap by pairing a multilingual transformer
baseline (cardiffnlp/twitter-xlm-roberta-base-sentiment) with an expanded
350+ term rule-based Taglish Lexical-Morphological Engine.

To guarantee a conflict-free, student-owned environment without fear of
retaliation, LexiMetrix operates on a pure 3-tier Student-Centric Role-Based
Access Control (RBAC) architecture (Student - Regular, Student - Officer, and
Developer) across two interconnected workspaces:
  1. Student Feedback & Community Portal (/student-portal): A 100% anonymous
     participatory Town Hall forum and Formal Survey hub where students share
     feedback, preview AI sentiment before publishing, vote on peer concerns,
     join paginated discussion threads (5 comments per page), and track
     official student leadership resolutions.
  2. Quantitative Analytics & Oversight Dashboard (/dashboard): An executive
     command center accessible to Student Officers (scoped strictly to their
     enrolled BSCS or BSIT program for peer representation) and System
     Developers (full cross-program clearance). It transforms raw narratives
     into real-time KPIs, high-DPI Matplotlib doughnut and aspect bar charts,
     explainable word-highlighted logs ("Why Positive / Why Negative"),
     customizable data summaries, automated prescriptive action alerts, chunked
     batch CSV imports with 1-click undo, and a live $3 \times 3$ Confusion
     Matrix & F1-Score validation suite.


================================================================================
2. SUMMARY OF LATEST SYSTEM UPGRADES (CURRENT SOURCE OF TRUTH)
================================================================================

  1. 100% Student-Centric 3-Tier Role Clearance:
     - Removed the "Faculty" login role across the entire codebase (auth.html,
       app.py, dashboard.html, student_portal.html, student_portal.js) to
       eliminate conflict of interest (since two core ABSA dimensions evaluate
       instructors' pedagogy and demeanor directly).
     - Enforces three distinct roles:
         * Student (Regular) [Student - Regular] : Accesses /student-portal only.
         * Student Officer / Rep [Student - Officer] : Accesses /student-portal
           (with announcement, resolution, and survey creation tools) AND
           accesses /dashboard strictly scoped to their enrolled program
           (BSCS or BSIT) to represent their peers.
         * System Developer [Developer] : Pre-seeded accounts (hjraymundo,
           apmalacaman, msmorata) with full cross-program (ALL, BSCS, BSIT)
           analytics, CSV batch upload/rollback, Slang Manager, Ground-Truth
           Override, F1 Confusion Matrix, and moderation clearance.
     - Startup Auto-Migration: Automatically converts any legacy "Faculty" test
       accounts in PostgreSQL to "Student - Officer" and demotes any non-team
       accounts that were accidentally assigned "Developer" back to
       "Student - Regular".

  2. Upgraded 350+ Word Taglish ABSA Engine & Startup Neutral Auto-Rescorer:
     - Expanded DEFAULT_LEXICON to 350+ English, Tagalog, and Taglish terms.
     - Added bilingual prefix/suffix stemming (napaka-, pinaka-, nakaka-, nag-,
       mag-, ma-, un-, in-, dis-, -ng, -an, -han, -in, -ing, -ed, -ly).
     - Added apostrophe-stripped contraction negators (dont, isnt, cant, wont)
       and existential deprivation rules ("walang wifi", "no aircon" $\rightarrow$
       Negative score of $-1.0 \times I_i$).
     - Added context-aware speed disambiguation ("mabilis/fast" scores Positive
       for wifi/computers/internet and Negative for rushed lecture pacing).
     - Added rescore_neutral_records() on startup to automatically re-evaluate
       existing Town Hall posts and unverified Feedback rows that were stuck
       as Neutral.

  3. Paginated Discussion Threads (5 Comments Per Page):
     - Town Hall post comment threads paginate at 5 comments per page with
       numbered navigation buttons ("< Prev 1 2 3 Next >") and a "Showing X-Y
       of Z comments" counter, automatically jumping to the newest page when a
       user submits a reply.

  4. Full Content, Comment & Survey Moderation Suite:
     - Post Deletion: Post authors and Developers can delete Town Hall posts
       from the Edit Post modal or post card (automatically deleting the synced
       Portal row in feedback_records). Developers can also delete inappropriate
       records directly from the Dashboard's AI Sentiment Inspector modal.
     - Comment Tombstone Moderation: Developers can click "Delete" on any
       inappropriate comment inside a discussion thread to permanently overwrite
       its database text and display with "This comment has been deleted".
     - Survey Deletion: Survey creators (Student Officers & Developers) and
       Developers see "Results", "Edit", "Link", and "Delete" buttons on survey
       cards and inside the Edit Survey modal, with the choice to either hide
       the survey or permanently purge all of its collected responses.

  5. Clean Navigation & 1-Click Defense Reset:
     - Consolidated the return link on /student-portal into a single bottom-left
       floating "Back to Analytics Dashboard" pill for Student Officers and
       Developers.
     - Added a 1-click "Clear All Test Posts & Logs" button under Developer
       Controls in the Dashboard sidebar to wipe test posts, comments, votes,
       and logs before a live defense while preserving user accounts and the
       Taglish lexicon.


================================================================================
3. END-TO-END SYSTEM FLOW (6-STAGE PIPELINE)
================================================================================

STAGE 1: INSTITUTIONAL REGISTRATION & BREVO HTTPS OTP VERIFICATION
  - Users register at /signup with an official @ccc.edu.ph email address,
    select their role (Student - Regular or Student - Officer) and degree
    program (BSCS or BSIT), and check the mandatory RA 10173 Data Privacy
    Informed Consent box.
  - The server generates a 6-digit OTP, hashes it with HMAC-SHA256 using the
    application secret key (10-minute expiration, max 5 verification attempts),
    and dispatches it via the Brevo HTTPS API (https://api.brevo.com/v3/smtp/email)
    to bypass cloud outbound SMTP port blocks.
  - Pre-seeded Developer accounts (hjraymundo, apmalacaman, msmorata) are
    provisioned at startup using scrypt password hashes.

STAGE 2: ROLE-BASED ROUTING & SESSION HARDENING
  - Login (/login) enforces a 5-attempt / 10-minute brute-force lockout and
    logs every authenticated sign-in to user_login_logs.
  - Routing upon authentication:
      * Student - Regular -> /student-portal
      * Student - Officer -> /dashboard (program-scoped to BSCS or BSIT, with
        full access to /student-portal to lead community initiatives)
      * Developer         -> /dashboard (full cross-program & admin clearance)
  - Security headers (Cache-Control: no-store, Clear-Site-Data on logout, and
    BFCache /api/session_ping verification) prevent back-button session leaks
    on shared laboratory computers.

STAGE 3: MULTI-SOURCE FEEDBACK INGESTION
  LexiMetrix ingests student narratives from three distinct channels:
  1. Portal Submissions (source="Portal"):
     - Town Hall Posts: Open feedback posted to Campus-Wide or DCI channels.
       Students can toggle "Preview AI Analysis" (/api/inspect_preview) to see
       their sentiment polarity, confidence score, and clause breakdown before
       publishing.
     - Formal Surveys: Structured evaluations created by Student Officers or
       Developers featuring Likert (1-5) ratings (with conditional follow-up
       elaboration boxes on low scores), single-choice radio buttons,
       checkboxes, and open narrative inquiries.
  2. Batch CSV Imports (source="CSV"):
     - Developers upload historical or external evaluation CSV files (up to
       2,000 rows per batch).
     - The 2-step importer previews the file, auto-detects encoding (UTF-8 /
       CP1252), maps columns (Program, Academic_Year, Semester, Feedback) with
       smart fallback defaults for single-column files, filters duplicates via
       SHA-256 and row keys, processes records in 40-row chunks, and supports
       1-click batch undo (/api/import/<batch_id>/rollback).
  3. Benchmark & Diagnostic Testing (source="Testing"):
     - Developers can test custom sentences in the single-sentence sandbox or
       seed the 30-item Taglish Gold Benchmark suite.

STAGE 4: ANONYMITY DECOUPLING, PII SCRUBBING & PROFANITY MASKING
  - Strict Identity Decoupling: Survey completion is logged in
    form_response_records (with date-coarsened timestamps) to enforce one
    submission per student, while actual survey answers are stored in
    form_anonymous_submissions with zero foreign key or reference to users.id.
  - Automated PII Scrubbing (scrub_pii): Regex filters automatically redact
    emails ([email hidden]), Philippine mobile numbers ([number hidden]),
    student IDs ([ID hidden]), social handles ([handle hidden]), and
    self-introductions ("My name is...", "Ako po si..." $\rightarrow$
    [self-introduction hidden]).
  - Profanity Filter (mask_profanity): Leet-speak-tolerant regex detects
    English, Tagalog, and Cebuano profanity. The AI scores raw profanity first
    as a $1.5\times$ emotional intensifier, then permanently masks the stored
    and displayed word with asterisks (e.g., "p*******a") and sets
    has_profanity=True.

STAGE 5: HYBRID XLM-ROBERTA + TAGLISH LEXICAL ABSA PIPELINE
  Every narrative comment passes through run_absa_pipeline():
  1. Preprocessing (preprocess_taglish_text): Lowercases text, removes URLs and
     control symbols, and normalizes whitespace (up to 2,000 characters).
  2. Compound Clause Segmentation (segment_compound_text): Splits multi-thought
     sentences at sentence punctuation (., !, ?) and bilingual contrastive
     conjunctions ("but", "pero", "kaso", "kaso lang", "however", "although",
     "while", "yet") into up to 12 independent clauses.
  3. Aspect Categorization (detect_aspect): Maps each clause via whole-word
     regex boundaries to one of four institutional dimensions:
       * Instructional Delivery & Pedagogy
       * Faculty Demeanor & Approachability
       * Campus Facilities & Infrastructure
       * General Academic Feedback (fallback category)
  4. Hybrid Clause Evaluation (evaluate_clause):
     - Queries cardiffnlp/twitter-xlm-roberta-base-sentiment for baseline
       polarity and confidence.
     - Stems Tagalog and English affixes and scores each token against the
       350+ word lexicon_terms table using intensifier multipliers ($1.5\times$),
       negation inversions, deprivation rules, and sarcasm invalidators ("eme",
       "charot", "charing", "joke").
  5. Document Aggregation & Explainable AI (_build_why_explanation):
     - Determines overall polarity by majority clause vote (breaking ties by
       summed lexical score $\sum L_c$) and generates a plain-English
       "Why Positive / Why Negative / Why Neutral" banner citing the exact
       trigger words, numerical weights, and primary aspect.

STAGE 6: QUANTITATIVE SYNTHESIS, PRESCRIPTIVE ALERTS & MODEL VALIDATION
  - Dashboard KPIs & High-DPI Charts: Computes 3-class and binary (Pos vs. Neg
    Only) shares and renders cached 200-DPI Matplotlib doughnut and aspect
    stacked bar charts.
  - Prescriptive Action Alerts (compute_prescriptive_insights): Automatically
    triggers targeted alerts when an aspect has $\ge 3$ mentions and a negative
    ratio $\ge 40\%$:
      * Campus Facilities & Infrastructure $\ge 40\%$ Neg $\rightarrow$
        "Community Action Alert" (Student Council report to General Services)
      * Instructional Delivery & Pedagogy $\ge 40\%$ Neg $\rightarrow$
        "Pedagogical Dialogue Request" (Consultative forum on syllabus pacing)
      * Faculty Demeanor & Approachability $\ge 40\%$ Neg $\rightarrow$
        "Student Welfare Advisory" (Student-faculty rapport initiatives)
  - Ground-Truth Override & $3 \times 3$ Confusion Matrix: Developers confirm
    or override AI labels to compute live Accuracy, Precision, Recall,
    $\text{Macro-}F1$, and $\text{Weighted-}F1$.


================================================================================
4. 3-TIER STUDENT-CENTRIC ROLE-BASED ACCESS CONTROL (RBAC) MATRIX
================================================================================

  1. STUDENT (REGULAR) [Role: "Student - Regular"]
     - Default Landing : /student-portal
     - Allowed         : Post 100% anonymous Town Hall feedback; toggle
                         Pre-Flight AI Sentiment Preview; upvote/downvote posts;
                         reply in paginated discussion threads (5/page); edit or
                         delete own Town Hall posts; answer Formal Surveys.
     - Restricted From : Cannot access /dashboard; cannot broadcast Official
                         Announcements; cannot create Formal Surveys; cannot
                         access Developer tools.

  2. STUDENT OFFICER / REPRESENTATIVE [Role: "Student - Officer"]
     - Default Landing : /dashboard (Program-Scoped) & /student-portal
     - Allowed         : All Regular Student capabilities PLUS:
                         * Broadcast pinned Official Announcements (with
                           optional auto-expiration date/time).
                         * Log official Duty-Bearer Resolutions ("Under Review"
                           or "Action Taken").
                         * Create, customize themes, edit, share (/s/<token>),
                           view private analytics, export CSV, and delete own
                           Formal Surveys.
                         * View /dashboard KPIs, charts, Total Summary, Custom
                           Summary Builder, and Export CSV strictly scoped to
                           their enrolled program (BSCS or BSIT), protected by
                           $k$-anonymity ($k = 5$).
     - Restricted From : Cannot view cross-program (ALL) data outside their
                         enrolled program; cannot upload/rollback system-wide
                         CSV batches; cannot edit Taglish Slang Lexicon; cannot
                         open F1 Confusion Matrix or override AI labels.

  3. SYSTEM DEVELOPER [Role: "Developer" — hjraymundo, apmalacaman, msmorata]
     - Default Landing : /dashboard (Full System-Wide Clearance)
     - Allowed         : Full cross-program analytics (ALL, BSCS, BSIT) &
                         Actionable Binary Mode (Pos vs. Neg Only); Batch CSV
                         Upload, Template Download, & 1-Click Batch Undo;
                         Dynamic Taglish Slang Manager; Set Active Institutional
                         Term & Add Academic Year; Ground-Truth Label Override
                         & $3 \times 3$ Confusion Matrix / F1 Validation Suite;
                         Full Moderation (delete any inappropriate post, record,
                         survey, or replace comment with "This comment has been
                         deleted"); 1-click "Clear All Test Posts & Logs" reset.
     - Restricted From : None (Full System & Moderation Clearance).


================================================================================
5. COMPLETE FEATURE SUITE BY MODULE
================================================================================

A. QUANTITATIVE ANALYTICS & OVERSIGHT DASHBOARD (/dashboard)
  - Toggleable Quick Workspace Sidebar (Alt + S): Slide-over command drawer
    with Pin/Unpin toggle so the main dashboard keeps 100% screen width.
  - Data Source Integrity Tabs: Switch between All Evaluated Sources, Portal
    Submissions, Imported CSVs, and Benchmark & Testing Logs.
  - Program, Polarity & Actionable Binary Mode Filters: Filter by All Programs,
    BSCS, or BSIT (Student Officers are automatically locked to their enrolled
    program), filter by sentiment, or click "Pos vs. Neg Only" to compare
    Positive vs. Negative directly with Neutral remarks excluded.
  - Interactive Total Summary Card & Custom Summary Builder: Synthesizes an
    executive narrative paragraph and opens a full modal with breakdowns by
    Program, Aspect, and Semester, plus a multi-chip Custom Summary Builder
    (/api/analytics/custom_summary).
  - Explainable Feedback Logs ("Why Positive / Why Negative"): Highlights
    positive words in green (.hl-pos), negative words in red (.hl-neg),
    intensifiers in amber (.hl-amp), and negators/sarcasm in violet (.hl-inv)
    directly inside each comment, paired with a plain-English reason banner.
  - AI Sentiment Inspector, Ground-Truth Override & Record Delete: Clicking any
    row opens #algorithmModal showing word weights, clause breakdowns, and
    recommended actions. Developers can confirm/override the polarity label or
    permanently delete inappropriate records.
  - Recurring Lexicon Keyword Cloud: Displays top recurring bilingual terms;
    clicking any chip filters the feedback logs table immediately.
  - Dynamic Taglish Slang Manager: Allows Developers to register or remove
    positive, negative, intensifier, negation, or profanity terms in real time.
  - $3 \times 3$ Confusion Matrix & F1 Validation Modal (#modelEvalModal):
    Computes multi-class Accuracy, Macro Precision, Macro Recall, Macro F1,
    Weighted F1, per-class TP/FP/FN counts, and a misclassification log across
    Human-Verified records or the 30-item Taglish Gold Benchmark.

B. STUDENT FEEDBACK & COMMUNITY PORTAL (/student-portal)
  - Animated Binary-Green Code-to-Logo SVG Morph: Splash screen and header
    crest where cascading green binary streams (0101) scan and crystallize into
    the LexiMetrix { ||| } emblem.
  - Department Community Pulse: Real-time voice tally bar showing total voices,
    commendation %, grievance %, active survey count, and tri-color meter.
  - Participatory Town Hall & Pre-Flight AI Check: Supports Campus-Wide,
    Official Announcements, and DCI channels, image drag-and-drop, reference
    links, upvote/downvote consensus scoring, and pre-flight AI preview.
  - Post Edit & Deletion: Authors and Developers can edit or permanently delete
    Town Hall posts (with a confirmation modal) and sync analytics automatically.
  - Paginated Discussion Threads & Tombstone Moderation: Comments paginate at
    5 per page with numbered buttons; Developers can replace inappropriate
    comments with "This comment has been deleted".
  - Google-Forms-Style Survey Builder, Custom Theme Studio & Survey Deletion:
    Supports Open Text, Likert (1-5) with conditional follow-up prompts on low
    scores, Single Choice, and Checkboxes; custom theme colors, fonts, and
    banner images; deadlines, quotas, shareable /s/<token> links, private CSV
    exports, and owner/Developer survey deletion.
  - Single Consolidated Return Pill: Student Officers and Developers have a
    single floating "Back to Analytics Dashboard" pill in the bottom-left corner.


================================================================================
6. ESSENTIAL REFERENCE FOR WRITING THE THESIS MANUSCRIPT
================================================================================

A. MATHEMATICAL EQUATIONS (CHAPTER 3: METHODOLOGY & STATISTICAL TREATMENT)

  1. Effective Lexical Token Weight ($w_i$):
     $$w_i = b_i \times I_i \times N_i$$
     Where:
       - $b_i \in \{+1.0, -1.0, 0.0\}$ is the base polarity of token $i$.
       - $I_i = 1.5$ if preceded by an intensifier token (e.g., "sobrang",
         "napaka", "very", "super", or masked profanity), else $1.0$.
       - $N_i = -1.0$ if preceded by a negator ("hindi", "di", "wala", "walang",
         "not", "dont") before a positive token, $-0.5$ when softening a
         negative token ("hindi masungit" $\rightarrow +0.5$), else $1.0$.

  2. Clause Net Lexical Score ($L_c$):
     $$L_c = \sum_{i=1}^{m} w_i - S_c$$
     Where $S_c = 1.5$ if a slang sarcasm invalidator ("eme", "charot",
     "charing", "joke") is detected in the clause, else $0.0$. Unresolved
     existential deprivation phrases ("walang wifi", "no aircon") resolve to
     $L_c = -1.0 \times I_i$.

  3. Multi-Class Classification Metrics (for class $c \in \{\text{Positive}, \text{Neutral}, \text{Negative}\}$):
     $$\text{Accuracy} = \frac{TP_{\text{Pos}} + TP_{\text{Neu}} + TP_{\text{Neg}}}{N_{\text{total}}} \times 100$$
     $$\text{Precision}_c = \frac{TP_c}{TP_c + FP_c} \times 100, \quad \text{Recall}_c = \frac{TP_c}{TP_c + FN_c} \times 100$$
     $$F1_c = \frac{2 \times \text{Precision}_c \times \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$
     $$\text{Macro-}F1 = \frac{F1_{\text{Pos}} + F1_{\text{Neu}} + F1_{\text{Neg}}}{3}, \quad \text{Weighted-}F1 = \frac{\sum_{c \in C} \left(\text{Support}_c \times F1_c\right)}{N_{\text{total}}}$$

  4. Actionable Binary Sentiment Share (Pos vs. Neg Only Mode):
     $$\text{Binary\_Pos\_\%} = \frac{N_{\text{Pos}}}{N_{\text{Pos}} + N_{\text{Neg}}} \times 100, \quad \text{Binary\_Neg\_\%} = \frac{N_{\text{Neg}}}{N_{\text{Pos}} + N_{\text{Neg}}} \times 100$$

  5. Weighted Arithmetic Mean (WAM) for ISO/IEC 25010:2023 System Evaluation:
     $$\text{WAM} = \frac{\sum (f \times w)}{N}$$
     Where $f$ is the frequency of responses per scale point, $w \in \{1, 2, 3, 4\}$
     is the assigned weight on the 4-point Likert scale, and $N$ is the total
     number of respondents.

B. ASPECT CATEGORIZATION TAXONOMY (ASPECT_CATEGORIES)
  1. Instructional Delivery & Pedagogy:
     lecture, turo, explain, speak, speaks, discussion, mabilis, fast, slow,
     teaching, lesson, clear, malinaw, linaw, confusing, exam, quiz, task,
     activity, galing, magaling.
  2. Faculty Demeanor & Approachability:
     talk, approachable, mabait, bait, attitude, sungit, masungit, easy,
     friendly, accommodating, strict, patient, galit, snob, ugali, pakikitungo,
     demeanor, prof, maam, sir.
  3. Campus Facilities & Infrastructure:
     room, classroom, fan, electric fan, aircon, mainit, init, hot, computer,
     wifi, internet, projector, lab, laboratory, chair, upuan.
  4. General Academic Feedback:
     Default fallback dimension when no specific aspect keyword is triggered.

C. 14-TABLE POSTGRESQL DATABASE SCHEMA DICTIONARY
  1. users                      : Institutional @ccc.edu.ph accounts, roles
                                  (Student - Regular, Student - Officer,
                                  Developer), scrypt/pbkdf2 password hashes,
                                  HMAC-SHA256 OTP state, lockout timers, and
                                  RA 10173 privacy_consent_at timestamp.
  2. user_login_logs            : Security audit log (user_id, username, role,
                                  ip_address, user_agent, login_time).
  3. academic_years             : Registered academic cycles (e.g., 2024-2025,
                                  2025-2026, 2026-2027).
  4. system_settings            : Key-value store for active_academic_year and
                                  active_semester.
  5. evaluation_forms           : Formal survey definitions, targeting rules,
                                  quotas, deadlines, questions_json, theme_json,
                                  header_image, share_token, is_active.
  6. form_response_records      : Tracks (form_id, student_id) completion with
                                  date-coarsened timestamps to enforce 1
                                  submission per student.
  7. form_anonymous_submissions : Decoupled JSON survey responses (answers_json)
                                  with zero foreign key to users.
  8. feedback_records           : Core ABSA analytics table (raw_text,
                                  cleaned_text, sentiment, ai_sentiment,
                                  human_sentiment, verified_by, confidence,
                                  aspect_breakdown JSON, source, import_batch,
                                  has_profanity, timestamp).
  9. import_batches             : CSV upload ledger (id, filename, file_sha256,
                                  total_rows, imported, skipped, duplicates,
                                  status) supporting 1-click rollback.
  10. community_posts           : Town Hall posts & announcements, category,
                                  content, media, sentiment, confidence, score,
                                  status, action_note.
  11. community_post_votes      : Upvote (+1) and downvote (-1) consensus
                                  records per user per post.
  12. community_resolution_votes: Student approval (+1) / disapproval (-1)
                                  reactions on official resolution notes.
  13. community_comments        : Paginated anonymous discussion replies on
                                  Town Hall posts (with Developer tombstone
                                  moderation support).
  14. lexicon_terms             : Dynamic 350+ word Taglish dictionary
                                  categorized as positive, negative,
                                  intensifiers, negations, or profanity.

D. FIVE-LAYER RA 10173 DATA PRIVACY ARCHITECTURE
  1. Explicit Informed Consent: Mandatory RA 10173 modal and checkbox at
     registration (/signup), recorded in users.privacy_consent_at.
  2. Strict Identity-to-Response Decoupling: Survey answers and evaluated
     feedback records store no student user_id or username.
  3. $k$-Anonymity Small-Group Suppression ($k = 5$): Disaggregated survey
     analytics, optional question breakdowns, and CSV exports are hidden from
     non-Developer views whenever fewer than $5$ responses match.
  4. Automated PII & Profanity Scrubbing: Regex pipelines mask contact details,
     IDs, handles, self-introductions, and profanity prior to storage.
  5. Timestamp Coarsening & Response Shuffling: Survey feedback timestamps are
     rounded to the hour, completion records to the day, and displayed/exported
     survey narratives are shuffled via random.shuffle().

E. REPOSITORY FILE STRUCTURE & RENDER ENVIRONMENT VARIABLES
  - app.py                      : Main Flask server, SQLAlchemy models, Brevo
                                  HTTPS OTP mailer, Hybrid XLM-RoBERTa + 350-word
                                  Taglish ABSA engine, startup neutral rescorer,
                                  Matplotlib chart generator, and REST APIs.
  - templates/auth.html         : Sliding Sign-In / Sign-Up portal (Student -
                                  Regular & Student - Officer), RA 10173 modal,
                                  6-digit OTP verification, and Password Reset.
  - templates/dashboard.html    : Quantitative Analytics Dashboard, Quick
                                  Workspace drawer (Alt + S), Total Summary &
                                  Custom Summary Builder, Explainable Logs, AI
                                  Inspector, CSV Importer, Slang Manager, F1
                                  Modal, and Clear Demo Data control.
  - templates/student_portal.html: Student Community Portal, Community Pulse,
                                  Town Hall composer & feed, Edit/Delete Post
                                  modals, Formal Surveys hub, Survey Builder,
                                  and single floating Back to Dashboard pill.
  - static/student_portal.js    : Frontend logic for Town Hall posts, pre-flight
                                  AI preview, 5-per-page paginated comments,
                                  Developer comment tombstone moderation, Survey
                                  Builder, theme studio, and survey deletion.
  - static/student_portal.css   : Dark/Light glassmorphism stylesheet and
                                  responsive mobile drawer styles.
  - static/tour.js & tour.css   : Interactive spotlight guided tour engine.
  - static/leximetrix-logo.svg  : Animated binary-green (0101) code-to-logo SVG.
  - Render Environment Variables: BREVO_API_KEY, MAIL_SENDER, DATABASE_URL,
                                  SECRET_KEY, PYTHON_VERSION, FLASK_ENV=production,
                                  HF_API_TOKEN, LOW_MEMORY_MODE=1.
================================================================================
