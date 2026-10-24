# LexiMetrix: Team Guide (Plain-Language Version)

LexiMetrix is a website that reads what students write about their classes and tells us, in numbers and charts, whether the feedback is **positive**, **negative**, or **neutral**, and *what it is about*. It understands English, Tagalog, and Taglish (a mix of both).

It was built for the **Department of Computing and Informatics (DCI)** at City College of Calamba, covering **BSCS** and **BSIT** students.

---

## 1. Why we built it

Regular evaluation forms mostly ask students to pick a number from 1 to 5. The written comments are left unread because there are too many, and Taglish is hard for normal tools: "sobrang galing" means *very good*, and "galing mo, charot!" is actually sarcasm.

LexiMetrix reads those comments for us and organizes them, so teachers and student leaders can see what students really think.

---

## 2. The two sides of the website

| | Student Portal | Analytics Dashboard |
|---|---|---|
| **Who uses it** | Students (and staff, to view it) | Faculty and Developers |
| **What it is for** | Sharing feedback, voting, answering surveys | Seeing the results as numbers and charts |
| **Web address** | `/student-portal` | `/dashboard` |

### Student Portal: what students can do
- **Town Hall:** a community feed where students post concerns or praise, comment, and upvote/downvote each other's posts. Before posting, a student can press **Preview AI Analysis** to see how the AI would score their message.
- **Formal Surveys:** forms made by officers, faculty, or developers (like a mini Google Forms), with 1-5 ratings, multiple choice, checkboxes, and open answers.
- **Concern tracking:** officers and faculty can mark a concern as **Under Review** or **Action Taken**, with a note that students can react to.
- **Community Pulse:** a live counter showing how many students have spoken up, how many posts are praise vs. complaints, and how many surveys are open.

### Analytics Dashboard: what staff can see
- **Totals and charts:** how many responses are positive, negative, and neutral, plus bar and doughnut charts per topic.
- **Total Summary card:** click it for a full breakdown by program, topic, and school term. Inside is the **Custom Summary Builder** (a hidden panel) where you tick exactly what you want summarized, such as only BSIT, only 1st semester, or only complaints about facilities.
- **Feedback table with explanations:** every comment shows *why* it was marked positive or negative. Good words are green, bad words red, "very"-type words amber, and "not"/sarcasm words purple.
- **Keyword cloud:** the most-repeated words. Click one to filter the table.
- **Alerts:** if one topic gets many complaints, the system suggests an action (see section 5).
- **Developer tools:** upload old results from a CSV file, edit the Taglish word list, and check how accurate the AI is.

> **Moving between the two:** from the dashboard, click **Student Portal** in the top bar. From the portal, use **Analytics Dashboard** in the left menu to go back (only staff can see this link).

---

## 3. Who can do what

| Role | Where they land after login | Main abilities |
|---|---|---|
| **Student - Regular** | Student Portal | Post, comment, vote, answer surveys |
| **Student - Officer** | Student Portal | Everything above, plus make surveys and mark concerns as Under Review / Action Taken |
| **Faculty** | Dashboard | See results for their program, make surveys |
| **Developer** (thesis team) | Dashboard | Everything, including CSV uploads, word-list edits, fixing AI labels, and moderating comments |

---

## 4. How a comment travels through the system

1. **Sign up and verify.** Users sign up with their school email (`@ccc.edu.ph`), agree to the Data Privacy notice (RA 10173), and type in a **6-digit code** sent to their email. The code expires in 10 minutes and allows 5 tries.
2. **Log in safely.** Five wrong passwords in a row locks the account for 10 minutes. Signing out clears the page so the next person on a shared lab PC can't press "Back" to see it.
3. **Feedback comes in** from three places:
   - **Portal:** Town Hall posts and survey answers.
   - **CSV upload:** older or outside spreadsheets uploaded by developers. A wrong upload can be undone with one click.
   - **Testing:** sample sentences used to test the AI.
4. **Privacy cleanup.** Before anything is saved or shown, the system hides emails, phone numbers, student ID numbers, social media handles, and "my name is..." sentences. Bad words are replaced with stars (like `p*******a`), though the AI still notices them to judge how strong the emotion is.
5. **The AI reads it.** The comment is split into smaller ideas (for example, "Mabait si Sir **pero** mabilis magturo" becomes two ideas). Each idea is sorted into a topic and scored (see next section).
6. **Results appear** on the dashboard as charts, tables, and alerts.

---

## 5. How the AI decides (without the math)

The system uses **two helpers working together**:

1. **A trained language model** (XLM-RoBERTa) that has read huge amounts of text in many languages and gives a first guess.
2. **Our own Taglish rulebook** that fixes what the model tends to miss.

**Topics the AI sorts each comment into:**
- **Teaching style** (lessons, explaining, speed, quizzes)
- **Teacher attitude** (kind, approachable, strict)
- **Campus facilities** (rooms, aircon, Wi-Fi, computers)
- **General feedback** (anything else)

**What the rulebook looks for:**
- **Good and bad words**, scored +1 or -1.
- **"Very" words** like *sobrang*, *napaka*, and *super* make the next word stronger (about 1.5 times).
- **"Not" words** like *hindi*, *wala*, and *not* flip the meaning ("hindi malinaw" = bad).
- **"No such thing" phrases** such as *walang wifi* count as complaints.
- **Sarcasm markers** like *eme*, *charot*, and *joke* turn the comment negative ("Ang galing mo magturo, eme lang!").
- **Word endings and prefixes** in Tagalog are trimmed so *nakakainis* and *inis* are treated alike.

**Alerts:** when one topic gets **at least 3 mentions and 40% or more of them are negative**, the dashboard suggests an action:
- Facilities: a **Community Action Alert** for General Services
- Teaching style: a **Pedagogical Dialogue Request** about lesson pacing
- Teacher attitude: a **Student Welfare Advisory** about teacher-student rapport

**Fixing the AI:** developers can mark any comment's label as correct or wrong. These corrections feed the accuracy check (the confusion matrix and F1 score), which shows how often the AI agrees with human judgment.

---

## 6. Privacy and safety, in plain words

- **Anonymous answers.** The system remembers *that* a student finished a survey (so they can't answer twice), but their answers are stored somewhere else with **no name attached**. Times are rounded to the hour or day so nobody can be matched by timing.
- **Small-group hiding.** If fewer than **5** responses match a filter, non-developers see no details or CSV export, because with so few people someone could guess who wrote what.
- **Automatic cleanup** of personal info and bad words (see step 4 above).
- **Consent first.** Nobody can create an account without accepting the Data Privacy notice.
- **Developer accounts** for the thesis team are created automatically when the site starts. Their passwords are stored scrambled, never as plain text. Don't share your password, and change it after your first login.

---

## 7. Files in the project (what each one does)

| File | What it does |
|---|---|
| `app.py` | The brain of the site: database, email codes, the AI, charts, and all the behind-the-scenes functions |
| `templates/auth.html` | Sign-in, sign-up, email code, and password recovery page |
| `templates/dashboard.html` | The analytics dashboard |
| `templates/student_portal.html` | The student portal (Town Hall and Surveys) |
| `static/student_portal.js` | Makes the portal work (posting, comments, survey builder) |
| `static/student_portal.css` | Colors and layout for the portal, dark and light |
| `static/tour.js` and `tour.css` | The step-by-step "Tour" guide in both pages |
| `static/leximetrix-logo.svg` | The animated logo |
| `requirements.txt` | The list of tools the site needs to run |
| `render.yaml` | Settings for our hosting on Render |

---

## 8. Good to know for the team

- **Hosting:** the site runs on **Render's free plan**. If nobody visits for about 15 minutes, it goes to sleep and the next visit can take up to a minute to load. This is normal.
- **Emails** (verification codes and password resets) are sent through **Brevo**. If a code doesn't arrive, check the spam folder.
- **Never share or upload secrets** (passwords, API keys, the secret key file). They live in Render's settings, not in GitHub.
- **Need a tour?** Press the **❓ Tour** button at the top of either page.
- **Shortcut:** `Alt + S` opens the dashboard's quick menu.

---

## 9. Word list (glossary)

| Term | Meaning |
|---|---|
| **NLP** | Teaching computers to understand human language |
| **ABSA** | Aspect-Based Sentiment Analysis: working out the feeling *and* the topic it is about |
| **Sentiment** | Whether a comment is positive, negative, or neutral |
| **Taglish** | Mixed Tagalog and English |
| **OTP** | One-Time Passcode, the 6-digit email code |
| **CSV** | A simple spreadsheet file |
| **Likert scale** | A 1-5 rating where 1 is strongly disagree and 5 is strongly agree |
| **PII** | Personal info such as names, numbers, or emails |
| **RA 10173** | The Philippine Data Privacy Act |
| **Confusion matrix / F1** | Ways to measure how often the AI agrees with human labels |
| **Hash** | A scrambled version of a password or code that can't be turned back into the original |
