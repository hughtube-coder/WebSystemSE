import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, f1_score
from app import app, run_absa_pipeline, get_active_lexicon

# Standardized Ground-Truth Validation Set (Taglish, English, Sarcastic & Compound Nuances)
EVALUATION_DATASET = [
    # Positive Sentences
    ("Sobrang galing magturo ni Sir, malinaw ang bawat lesson at hands-on activities.", "Positive"),
    ("Mabait si Ma'am at very approachable kapag may hindi kami maintindihan.", "Positive"),
    ("Clear and concise lectures. The slides provided are very helpful.", "Positive"),
    ("Goods na goods ang facilities sa computer laboratory, malamig ang aircon.", "Positive"),
    ("Masipag mag-consult si Sir bago magpa-exam, sobrang laking tulong.", "Positive"),
    ("Petiks pero may natutunan, maayos makipag-usap sa mga estudyante.", "Positive"),
    ("Sulit ang tuition, magaganda ang projector at upuan sa DCI building.", "Positive"),
    ("Prof is very professional and provides constructive feedback on projects.", "Positive"),

    # Negative Sentences
    ("Sobrang bilis magturo ni Sir, hindi namin ma-gets ang coding examples.", "Negative"),
    ("Laging late pumasok si Ma'am tapos nagagalit pa pag nagtanong.", "Negative"),
    ("Mainit sa classroom, sira ang electric fan at madilim ang projector.", "Negative"),
    ("Boring mag-discuss, binabasa lang yung PowerPoint slide per slide.", "Negative"),
    ("Masungit ang instructor tuwing submission ng laboratory exercise.", "Negative"),
    ("Walang kwenta ang Wi-Fi connection sa campus, hindi magamit sa research.", "Negative"),
    ("Magulo magpa-quiz, walang kaugnayan sa na-discuss nung prelims.", "Negative"),
    ("The pacing of the lecture is very fast and confusing for beginners.", "Negative"),

    # Nuanced, Sarcastic & Slang Clauses
    ("Ang galing mo magturo ma'am, eme lang!", "Negative"), # Sarcasm Invalidation
    ("Solid ang explanation ni Sir pero charot lang pala.", "Negative"), # Sarcasm Invalidation
    ("Mabait si Sir pero hindi nagtuturo nang maayos tuwing lecture.", "Negative"), # Compound Inversion
    ("Hindi malinaw ang instructions sa final project requirements.", "Negative"), # Negator
    ("Sobrang init sa room pero mabait naman si Sir.", "Neutral"), # Compound Split Balancing
    ("The examination covered chapters one to five as announced.", "Neutral"), # Informational
    ("The lecture started at exactly 8:00 AM in Room 302.", "Neutral"), # Informational
    ("Hindi masungit si Ma'am kapag tinatanong sa office.", "Positive") # Inverted Negative
]


# 40-Item Unseen Holdout Test Set (Untuned Adversarial & Natural Student Feedback)
UNSEEN_HOLDOUT_DATASET = [
    # Positive (14)
    ("Mabilis sumagot si sir kapag may tanong kami sa group chat.", "Positive"),
    ("Hindi ko alam kung bakit sobrang galing ni sir magturo sa algorithm.", "Positive"),
    ("Not only is the prof good, the lessons are great and practical.", "Positive"),
    ("Hindi lang mabait si maam, sobrang husay pa mag-explain ng code.", "Positive"),
    ("I really like the new laboratory computers, smooth gamitin sa programming.", "Positive"),
    ("Malinis at malamig ang room namin sa second floor.", "Positive"),
    ("Very considerate at patient si prof sa mga beginners mag-code.", "Positive"),
    ("Pota ang galing magturo ni Sir sa Networking!", "Positive"),
    ("Gago ang husay ng explanation sa Data Structures!", "Positive"),
    ("Hindi mahirap intindihan yung lecture kasi organized ang slides.", "Positive"),
    ("Responsive ang portal at mabilis ang internet sa computer lab.", "Positive"),
    ("Thankful kami kasi approachable at fair magbigay ng grades si maam.", "Positive"),
    ("Solid ang hands-on exercises, marami kaming natutunan ngayong sem.", "Positive"),
    ("Maayos na ulit yung projector at gumagana na lahat ng PC sa lab.", "Positive"),

    # Negative (16)
    ("The grading system is unclear and unfair to students.", "Negative"),
    ("The instructor was unprofessional and inconsiderate during submission.", "Negative"),
    ("The laboratory wifi is unavailable and inaccessible all week.", "Negative"),
    ("Very inconvenient schedule and uncomfortable chairs in the room.", "Negative"),
    ("The portal is unresponsive and inefficient during enrollment.", "Negative"),
    ("I dislike how the lessons are rushed every meeting.", "Negative"),
    ("Sayang ang tuition, laging walang klase at absent.", "Negative"),
    ("The wifi is slow in the computer lab.", "Negative"),
    ("Ang galing ni sir. Charot.", "Negative"),
    ("The programming exam was hard, no joke.", "Negative"),
    ("Maganda sana kung nagana talaga computer sa computer lab.", "Negative"),
    ("Tanginang wifi yan walang kwenta.", "Negative"),
    ("Kupal at bastos sumagot pag tinatanong sa klase.", "Negative"),
    ("Bobo at tanga yung lumang systema, laging naghahang.", "Negative"),
    ("Walang aircon sa room tapos sira pa yung electric fan.", "Negative"),
    ("Galing magturo ni sir pero putangina ang init sa room.", "Negative"),

    # Neutral (10)
    ("Maganda ang turo kaso lang mainit sa lab.", "Neutral"),
    ("Ok but slow wifi in the laboratory.", "Neutral"),
    ("Good teacher but bad wifi.", "Neutral"),
    ("He speaks like a robot during lectures.", "Neutral"),
    ("Nag-upload na ng bagong module at reading materials sa portal.", "Neutral"),
    ("Our midterm exam is scheduled next Wednesday in Lab 2.", "Neutral"),
    ("We used Python, Flask, and PostgreSQL for our software engineering project.", "Neutral"),
    ("The class section was transferred to the third floor room.", "Neutral"),
    ("May general assembly ang DCI students bukas ng hapon.", "Neutral"),
    ("The laboratory manual has ten chapters covering SQL queries.", "Neutral"),
]

def benchmark_roberta_pipeline():
    print("=" * 65)
    print("  CITY COLLEGE OF CALAMBA — INSTITUTIONAL ABSA BENCHMARK")
    print("  Model Architecture: XLM-RoBERTa + Dynamic Taglish Rule Engine")
    print("=" * 65)

    y_true = []
    y_pred = []

    with app.app_context():
        lexicon = get_active_lexicon()

    print(f"\n[*] Evaluating pipeline over {len(EVALUATION_DATASET)} ground-truth samples...\n")

    for idx, (sentence, ground_truth) in enumerate(EVALUATION_DATASET, 1):
        _, predicted_sentiment, confidence, breakdown = run_absa_pipeline(sentence, lexicon)
        y_true.append(ground_truth)
        y_pred.append(predicted_sentiment)

        match_indicator = "✓" if predicted_sentiment == ground_truth else "✗"
        print(f"[{idx:02d}] {match_indicator} [{predicted_sentiment:<8}] (Expected: {ground_truth:<8} | Conf: {confidence}) -> \"{sentence[:45]}...\"")

    labels = ["Positive", "Negative", "Neutral"]
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average='macro')
    weighted_f1 = f1_score(y_true, y_pred, average='weighted')

    print("\n" + "=" * 65)
    print("  EVALUATION PERFORMANCE METRICS")
    print("=" * 65)
    print(f"  • Model Accuracy:      {acc * 100:.2f}%")
    print(f"  • Macro F1-Score:      {macro_f1:.4f}")
    print(f"  • Weighted F1-Score:   {weighted_f1:.4f}")
    print("-" * 65)
    print("\nClassification Report:\n")
    print(classification_report(y_true, y_pred, target_names=labels, zero_division=0))

    # Generate Confusion Matrix Figure
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    fig, ax = plt.subplots(figsize=(6, 5), dpi=300, facecolor='#0f1a30')
    ax.set_facecolor('#070d1d')

    cax = ax.matshow(cm, cmap=plt.cm.Blues, alpha=0.85)

    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(x=j, y=i, s=cm[i, j], va='center', ha='center',
                    fontsize=14, fontweight='bold',
                    color='#f8fafc' if cm[i, j] > (cm.max() / 2) else '#94a3b8')

    fig.colorbar(cax)
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold', color='#f8fafc')
    ax.set_yticklabels(labels, fontsize=10, fontweight='bold', color='#f8fafc')

    ax.tick_params(axis='both', which='both', length=0)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('rgba(255,255,255,0.1)')
    ax.spines['left'].set_color('rgba(255,255,255,0.1)')

    plt.title("XLM-RoBERTa ABSA Confusion Matrix", color='#f8fafc', fontsize=12, fontweight='bold', pad=20)
    plt.xlabel("Predicted Polarity", color='#94a3b8', fontsize=10, labelpad=10)
    plt.ylabel("Ground Truth Polarity", color='#94a3b8', fontsize=10, labelpad=10)

    output_path = "confusion_matrix.png"
    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()

    print(f"[+] Confusion matrix plot successfully saved to: {os.path.abspath(output_path)}\n")

if __name__ == "__main__":
    benchmark_roberta_pipeline()
