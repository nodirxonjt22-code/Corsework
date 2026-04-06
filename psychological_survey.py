"""
Psychological State Survey Program
------------------------------------
Assesses a respondent's psychological state through a validated questionnaire,
produces a scored result, and supports saving/loading in TXT, CSV, and JSON formats.
"""

import re
import csv
import json
import os
import sys
from datetime import datetime, date

# ─────────────────────────────────────────────────────────────────────────────
# QUESTIONNAIRE  (20 original questions, 4 options each)
# ─────────────────────────────────────────────────────────────────────────────
QUESTIONS =[
    {"q": "When your phone battery drops below 10%, you:",
     "opts": [("Ignore it; it’ll last as long as needed",0),("Feel a subtle urgency and distraction", 2),("Immediately look for a charger",3),("Feel oddly irritated or tense",4)]},
    {"q": "You hear a notification sound, but it’s not your device:",
     "opts": [("Ignore it completely",0),("Briefly check your own anyway",2),("Feel a moment of unease",3),("Get annoyed by the interruption",1)]},
    {"q": "When plans suddenly change:",
     "opts": [("I adapt quickly without much thought",0),("I feel slightly off but manage",2),("I need time to mentally reorganize",3),("I feel overwhelmed or frustrated",4)]},
    {"q": "Your thoughts before sleep are:",
     "opts": [("Mostly quiet or neutralt",0),("Mildly active but manageable",2),("Repetitive or looping",3),("Intense or difficult to stop",4)]},
    {"q": "When facing a minor mistake:",
     "opts": [("Shrug it off",0),("Replay it briefly",2),("Analyze it repeatedly",2),("Feel disproportionate frustration or guilt",4)]},
    {"q": "In a crowded environment, you tend to:",
     "opts": [("Feel energized",0),("Stay neutral",1),("Feel slightly drained",2),("Feel tense or overwhelmed",4)]},
    {"q": "When someone doesn’t reply to you:",
     "opts": [("Assume they’re busy",0),("Wonder briefly why",2),("Check repeatedly",3),("Assume something is wrong",4)]},
    {"q": "Your reaction to silence is:",
     "opts": [("Comfortable",0),("Slightly awkward",1),("Mentally filled with thoughts",3),("Unsettling or stressful",4)]},
    {"q": "When multitasking:",
     "opts": [("You perform efficiently",0),("Slight drop in focus",2),("Feel scattered",3),("Become stressed or ineffective",4)]},
    {"q": "You notice time passing:",
     "opts": [("Rarely; you're immersed",0),("Occasionally",1),("Frequently check time",3),("Constantly aware of it",4)]},
    {"q": "When you receive unexpected criticism:",
     "opts": [("Evaluate it objectively",1),("Feel mildly affected",2),("Dwell on it",3),("Feel deeply unsettled",4)]},
    {"q": "Your energy levels throughout the day:",
     "opts": [("Stable",0),("Slight fluctuations",1),("Noticeable highs and lows",3),("Unpredictable or draining",4)]},
    {"q": "When starting a new task:",
     "opts": [("Begin immediately",0),("Pause briefly",1),("Delay with minor distractions",3),("Avoid or feel resistance",4)]},
    {"q": "Your internal dialogue is:",
     "opts": [("Calm and neutral",0),("Occasionally critical",2),("Often questioning or doubting",3),("Frequently harsh or overwhelming",4)]},
    {"q": "When alone with no obligations:",
     "opts": [("Feel relaxed",0),("Slight restlessness",1),("Seek stimulation",3),("Feel uneasy or unsettled",4)]},
    {"q": "Your reaction to uncertainty:",
     "opts": [("Accept it",0),("Slight concern",2),("Try to control outcomes",3),("Feel anxious or tense",4)]},
    {"q": "When recalling past events:",
     "opts": [("Neutral reflection",0),("Occasional regret",2),("Frequent revisiting",3),("Emotionally charged recall",4)]},
    {"q": "Your typical pace of thinking:",
     "opts": [("Steady and controlled",0),("Slightly fast",2),("Rapid or jumping topics",3),("Overwhelming or racing",4)]}
]

psych_states = {
    "Grounded & Balanced State": (0, 10),
    "Mild Cognitive Load": (11, 22),
    "Elevated Stress State": (23, 36),
    "Persistent Anxiety Pattern": (37, 50),
    "High Psychological Strain": (51, 62),
    "Acute Dysregulation State": (63, 72),
    
}

NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z\-' ]*$")


def validate_name(full_name: str) -> bool:
    """
    Accepts letters (a-z, A-Z), hyphens, apostrophes, and spaces.
    Must start with a letter. No digits or other punctuation allowed.
    Covers: O'Connor, Smith-Jones, Mary Ann, etc.
    """
    parts = full_name.strip().split()
    if len(parts) < 2:
        return False
    return all(NAME_PATTERN.match(part) for part in parts)


def validate_dob(dob_str: str) -> bool:
    """
    Accepts dates in DD/MM/YYYY, DD-MM-YYYY, or DD.MM.YYYY format.
    Validates calendar correctness (e.g. rejects 30 Feb).
    Date must be in the past and the person must not be over 130 years old.
    """
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            dob = datetime.strptime(dob_str.strip(), fmt).date()
            today = date.today()
            if dob >= today:
                return False
            if (today - dob).days > 130 * 365:
                return False
            return True
        except ValueError:
            continue
    return False


def validate_student_id(sid: str) -> bool:
    """Student ID must consist of digits only."""
    return sid.strip().isdigit() and len(sid.strip()) > 0


def get_input(prompt: str, validator, error_msg: str) -> str:
    """Loop until valid input is provided."""
    while True:
        value = input(prompt).strip()
        if validator(value):
            return value
        print(f"  ✗  {error_msg}")



def run_survey() -> dict:
    """Collect respondent details and administer the questionnaire."""
    print("\n" + "=" * 65)
    print("   PSYCHOLOGICAL STATE SURVEY")
    print("=" * 65)
    print("\nPlease answer each question honestly.")
    print("Your responses are used solely to estimate your current")
    print("psychological state.\n")

   
    surname_given = get_input(
        "Full name (Surname Given name): ",
        validate_name,
        "Name must contain at least a surname and given name. "
        "Only letters, hyphens (-), apostrophes ('), and spaces are allowed. "
        "No digits or other punctuation."
    )

    dob = get_input(
        "Date of birth (DD/MM/YYYY): ",
        validate_dob,
        "Invalid date. Use DD/MM/YYYY format with a valid past date "
        "(e.g. 15/04/1998)."
    )

    student_id = get_input(
        "Student ID (digits only): ",
        validate_student_id,
        "Student ID must contain only digits."
    )

   
    print("\n" + "-" * 65)
    print("QUESTIONNAIRE")
    print("-" * 65 + "\n")

    total_score = 0
    answers = []

    for idx, q in enumerate(QUESTIONS, start=1):
        print(f"Q{idx}. {q['text']}")
        for letter_idx, (text, _score) in enumerate(q["options"], start=1):
            print(f"   {letter_idx}. {text}")

        valid_choices = [str(i) for i in range(1, len(q["options"]) + 1)]
        while True:
            choice = input("   Your answer: ").strip()
            if choice in valid_choices:
                break
            print(f"   ✗  Please enter a number between 1 and {len(q['options'])}.")

        selected_text, selected_score = q["options"][int(choice) - 1]
        total_score += selected_score
        answers.append({
            "question": q["text"],
            "answer": selected_text,
            "score": selected_score,
        })
        print()

   
    state_label, state_description = "", ""
    for lo, hi, label, desc in STATES:
        if lo <= total_score <= hi:
            state_label = label
            state_description = desc
            break

    result = {
        "name": surname_given,
        "date_of_birth": dob,
        "student_id": student_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_score": total_score,
        "max_score": len(QUESTIONS) * 4,
        "state": state_label,
        "description": state_description,
        "answers": answers,
    }

    # ── Display result ────────────────────────────────────────────────────────
    _print_result(result)
    return result


def _print_result(result: dict) -> None:
    print("\n" + "=" * 65)
    print("   SURVEY RESULT")
    print("=" * 65)
    print(f"  Name        : {result['name']}")
    print(f"  Date of birth: {result['date_of_birth']}")
    print(f"  Student ID  : {result['student_id']}")
    print(f"  Completed   : {result['timestamp']}")
    print(f"  Total score : {result['total_score']} / {result['max_score']}")
    print(f"\n  ► {result['state']}")
    print(f"\n  {result['description']}")
    print("=" * 65 + "\n")


# ─────────────────────────────────────────────────────────────────────────────
# FILE I/O
# ─────────────────────────────────────────────────────────────────────────────
def save_result(result: dict) -> None:
    """Prompt user for format and save the result."""
    print("Save results as:")
    print("  1. TXT")
    print("  2. CSV")
    print("  3. JSON")

    while True:
        choice = input("Choose format (1/2/3): ").strip()
        if choice in ("1", "2", "3"):
            break
        print("  ✗  Please enter 1, 2, or 3.")

    safe_name = re.sub(r"\s+", "_", result["name"].strip())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"survey_{safe_name}_{timestamp}"

    if choice == "1":
        _save_txt(result, base_name + ".txt")
    elif choice == "2":
        _save_csv(result, base_name + ".csv")
    else:
        _save_json(result, base_name + ".json")


def _save_txt(result: dict, filename: str) -> None:
    lines = [
        "PSYCHOLOGICAL STATE SURVEY — RESULTS",
        "=" * 50,
        f"Name          : {result['name']}",
        f"Date of birth : {result['date_of_birth']}",
        f"Student ID    : {result['student_id']}",
        f"Completed     : {result['timestamp']}",
        f"Total score   : {result['total_score']} / {result['max_score']}",
        f"State         : {result['state']}",
        f"Description   : {result['description']}",
        "",
        "DETAILED ANSWERS",
        "-" * 50,
    ]
    for i, a in enumerate(result["answers"], 1):
        lines.append(f"Q{i}: {a['question']}")
        lines.append(f"    Answer : {a['answer']}  (score: {a['score']})")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  ✓  Results saved to '{filename}'")


def _save_csv(result: dict, filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Field", "Value"])
        writer.writerow(["Name", result["name"]])
        writer.writerow(["Date of Birth", result["date_of_birth"]])
        writer.writerow(["Student ID", result["student_id"]])
        writer.writerow(["Timestamp", result["timestamp"]])
        writer.writerow(["Total Score", result["total_score"]])
        writer.writerow(["Max Score", result["max_score"]])
        writer.writerow(["State", result["state"]])
        writer.writerow(["Description", result["description"]])
        writer.writerow([])
        writer.writerow(["#", "Question", "Answer", "Score"])
        for i, a in enumerate(result["answers"], 1):
            writer.writerow([i, a["question"], a["answer"], a["score"]])
    print(f"  ✓  Results saved to '{filename}'")


def _save_json(result: dict, filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"  ✓  Results saved to '{filename}'")



# LOAD EXISTING RESULT

def load_result() -> None:
    """Load a previously saved result file and display it."""
    filepath = input("Enter the path to the saved result file: ").strip()

    if not os.path.isfile(filepath):
        print(f"  ✗  File not found: '{filepath}'")
        return

    ext = os.path.splitext(filepath)[1].lower()

    try:
        if ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                result = json.load(f)
            _print_result(result)

        elif ext == ".csv":
            data = {}
            answers = []
            reading_answers = False
            with open(filepath, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    if row[0] == "#":           # header row for answers
                        reading_answers = True
                        continue
                    if reading_answers:
                        answers.append({
                            "question": row[1],
                            "answer": row[2],
                            "score": int(row[3]),
                        })
                    elif row[0] != "Field":
                        data[row[0]] = row[1] if len(row) > 1 else ""

            result = {
                "name": data.get("Name", "N/A"),
                "date_of_birth": data.get("Date of Birth", "N/A"),
                "student_id": data.get("Student ID", "N/A"),
                "timestamp": data.get("Timestamp", "N/A"),
                "total_score": int(data.get("Total Score", 0)),
                "max_score": int(data.get("Max Score", 80)),
                "state": data.get("State", "N/A"),
                "description": data.get("Description", "N/A"),
                "answers": answers,
            }
            _print_result(result)

        elif ext == ".txt":
            with open(filepath, "r", encoding="utf-8") as f:
                print(f.read())

        else:
            print("  ✗  Unsupported file format. Accepted: .txt, .csv, .json")

    except Exception as exc:
        print(f"  ✗  Failed to load file: {exc}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    print("\n" + "=" * 65)
    print("   PSYCHOLOGICAL STATE ASSESSMENT SYSTEM")
    print("=" * 65)
    print("\nWhat would you like to do?")
    print("  1. Start a new questionnaire")
    print("  2. Load an existing result from a file")

    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice in ("1", "2"):
            break
        print("  ✗  Please enter 1 or 2.")

    if choice == "2":
        load_result()
        return

    # ── New survey ────────────────────────────────────────────────────────────
    result = run_survey()

    while True:
        save_choice = input("Would you like to save the results? (yes/no): ").strip().lower()
        if save_choice in ("yes", "y"):
            save_result(result)
            break
        elif save_choice in ("no", "n"):
            print("Results not saved.")
            break
        else:
            print("  ✗  Please enter 'yes' or 'no'.")

    print("\nThank you for completing the survey.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSurvey interrupted. Exiting.")
        sys.exit(0)
