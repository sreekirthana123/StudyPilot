import os
import json
from datetime import date, datetime
from groq import Groq
from dotenv import load_dotenv

# Initialize environment variables and Groq client globally
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def load_syllabus(path="syllabus_output.json"):
    """Loads your custom parsed syllabus JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def calculate_priority(subject, today=None):
    """Calculates study priority score based on weightage and days remaining."""
    if today is None:
        today = date.today()

    exam_date_str = subject.get("exam date")
    weightage_str = subject.get("weightage", "0%")

    try:
        weightage = float(weightage_str.replace("%", "").strip())
    except:
        weightage = 10.0

    if exam_date_str:
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
        days_remaining = max((exam_date - today).days, 1)
    else:
        days_remaining = 30

    priority = (weightage / days_remaining) * 100
    return priority


def allocate_hours(subjects, daily_hours=4):
    """Allocates available daily study minutes across subjects proportionally."""
    scored = []
    for subject in subjects:
        score = calculate_priority(subject)
        scored.append({
            "subject": subject["subject"],
            "chapters": subject.get("chapters", []),
            "exam date": subject.get("exam date", "Not specified"),
            "priority_score": score
        })

    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    total_score = sum(s["priority_score"] for s in scored)

    total_daily_minutes = daily_hours * 60
    for subject in scored:
        proportion = subject["priority_score"] / total_score
        minutes = round(proportion * total_daily_minutes)
        subject["daily_minutes"] = max(minutes, 20)

    return scored


def generate_timetable(allocated_subjects, daily_hours=4, days_ahead=7):
    """Sends allocated summary to Groq using standard text prompt instructions."""
    today = date.today()
    subject_summary = ""

    for subject in allocated_subjects:
        subject_summary += f"""
            Subject : {subject['subject']}
            Chapters : {', '.join(subject['chapters'])}
            Exam Date : {subject['exam date']}
            Priority Score: {subject['priority_score']}
            Daily study time : {subject['daily_minutes']} minutes
        """

    prompt = f"""
        You are a study planner AI.

        Today is {today.strftime('%A, %d %B %Y')}.
        The student has {daily_hours} hours to study per day.
        Create a {days_ahead}-day study timetable matching the provided structure rules.

        Here are the subjects with their priority scores and daily time allocations:
        {subject_summary}

        Rules:
        1. Higher priority subjects get more time each day.
        2. Sequence chapters logically - foundational topics before advanced ones.
        3. Include short 10-minute breaks between subjects.
        4. On days 6 and 7 (weekend), add a 30-minute revision slot for the highest priority subject.
        5. Return ONLY a valid JSON object. Do not include markdown code block syntax (like ```json).

        Return this exact format layout structure:
        {{
          "timetable": [
            {{
              "day": 1,
              "date": "YYYY-MM-DD",
              "slots": [
                {{
                  "subject": "string",
                  "duration_minutes": number,
                  "chapters_to_cover": ["string"],
                  "notes": "string"
                }}
              ],
              "total_study_minutes": number
            }}
          ],
          "weekly_summary": "string"
        }}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=4000,
    )

    raw_output = response.choices[0].message.content
    cleaned_output = clean_json_response(raw_output)
    timetable_data = json.loads(cleaned_output)

    return timetable_data


def clean_json_response(raw):
    """Strips away conversational flavor or markdown blocks safely."""
    start = raw.find("{")
    end = raw.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("Could not find curly brace boundaries in model output")

    return raw[start : end + 1]


def display_timetable(timetable_data):
    """Prints the rich formatted daily breakdown blocks and weekly summary."""
    print("\n" + "=" * 60)
    print("YOUR STUDY TIMETABLE")
    print("=" * 60)

    timetable_list = timetable_data.get("timetable", [])
    
    for day in timetable_list:
        print(f"\n📅 Day {day.get('day', '?')} - ({day.get('date', 'Unknown Date')})")
        print("-" * 40)
        
        for slot in day.get("slots", []):
            chapters = ", ".join(slot.get("chapters_to_cover", []))
            print(f"  ⏱️ {slot.get('duration_minutes', 0)} min | {slot.get('subject', 'Study Slot')}")
            print(f"     Chapters: {chapters}")
            
            if slot.get("notes"):
                print(f"     Note: {slot['notes']}")
                
        print(f"📊 Total: {day.get('total_study_minutes', 0)} minutes")

    print("\n" + "=" * 60)
    print("📝 WEEKLY SUMMARY")
    print(timetable_data.get("weekly_summary", "No summary provided."))
    print("=" * 60 + "\n")


def main():
    print("Loading syllabus")
    subjects = load_syllabus("syllabus_output.json")

    try:
        daily_hours = float(input("How many hours per day you can study? (default 4) "))
    except:
        daily_hours = 4.0

    print("Allocating study time across subjects")
    allocated = allocate_hours(subjects, daily_hours)

    print("Priority order")
    for i, subject in enumerate(allocated, 1):
        print(f"{i}. {subject['subject']} - Score: {subject['priority_score']:.2f} - {subject['daily_minutes']} min/day")

    print("Generating timetable via Groq...")
    timetable_data = generate_timetable(allocated, daily_hours=daily_hours)

    # 1. Displays the styled console output
    display_timetable(timetable_data)

    # 2. Writes output into structural json data storage file
    with open("timetable.json", "w") as f:
        json.dump(timetable_data, f, indent=2)

    # 3. Success log line added by the instructor
    print("saved to timetable json")


if __name__ == "__main__":
    # main()
    pass
