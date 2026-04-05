import streamlit as st
import json
from datetime import datetime
import sys
import os

# ---------------- DATA ----------------
version_float = 1.1

questions = [
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

# ---------------- HELPERS ----------------
def validate_name(name: str) -> bool:
    return len(name.strip()) > 0 and not any(c.isdigit() for c in name)

def validate_dob(dob: str) -> bool:
    try:
        datetime.strptime(dob, "%Y-%m-%d")
        return True
    except:
        return False

def interpret_score(score: int) -> str:
    for state, (low, high) in psych_states.items():
        if low <= score <= high:
            return state
    return "Unknown"

def save_json(filename: str, data: dict):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Student Psychological Survey")
st.title("📝 Student Psychological Survey")

st.info("Please fill out your details and answer all questions honestly.")

# --- User Info ---
name = st.text_input("Given Name")
surname = st.text_input("Surname")
dob = st.text_input("Date of Birth (YYYY-MM-DD)")
sid = st.text_input("Student ID (digits only)")

# --- Start Survey ---
if st.button("Start Survey"):

    # Validate inputs
    errors = []
    if not validate_name(name):
        errors.append("Invalid given name.")
    if not validate_name(surname):
        errors.append("Invalid surname.")
    if not validate_dob(dob):
        errors.append("Invalid date of birth format. Use YYYY-MM-DD.")
    if not sid.isdigit():
        errors.append("Student ID must be digits only.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        st.success("All inputs are valid. Proceed to answer the questions below.")

        total_score = 0
        answers = []

        for idx, q in enumerate(questions):
            opt_labels = [opt[0] for opt in q["opts"]]
            choice = st.selectbox(f"Q{idx+1}. {q['q']}", opt_labels, key=f"q{idx}")
            score = next(score for label, score in q["opts"] if label == choice)
            total_score += score
            answers.append({
                "question": q["q"],
                "selected_option": choice,
                "score": score
            })

        status = interpret_score(total_score)

        st.markdown(f"## ✅ Your Result: {status}")
        st.markdown(f"**Total Score:** {total_score}")

        # Save results to JSON
        record = {
            "name": name,
            "surname": surname,
            "dob": dob,
            "student_id": sid,
            "total_score": total_score,
            "result": status,
            "answers": answers,
            "version": version_float
        }

        json_filename = f"{sid}_result.json"
        save_json(json_filename, record)

        st.success(f"Your results are saved as {json_filename}")
        st.download_button("Download your result JSON", json.dumps(record, indent=2), file_name=json_filename)

