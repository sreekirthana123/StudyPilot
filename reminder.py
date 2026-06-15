import os
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def send_daily_nudge(rows, recipient_email: str):
    """Send today's timetable as an HTML email.

    Expects rows items with keys:
    - date, subject, topic, minutes, notes
    """

    today = date.today().isoformat()
    today_tasks = [r for r in rows if r.get("date") == today]

    sender_email = os.getenv("GMAIL_ID")
    app_password = os.getenv("GMAIL_PASSWORD")

    if not sender_email or not app_password:
        raise RuntimeError(
            "Missing email credentials. Set GMAIL_ID and GMAIL_PASSWORD in your .env"
        )

    table_rows = "".join(
        (
            "<tr>"
            f"<td>{r.get('subject','')}</td>"
            f"<td>{r.get('topic','')}</td>"
            f"<td>{r.get('minutes',0)} min</td>"
            f"<td><i>{r.get('notes','')}</i></td>"
            "</tr>"
        )
        for r in today_tasks
    )

    total_mins = sum(r.get("minutes", 0) for r in today_tasks)

    html = f"""
    <h2>StudyPilot - {today}</h2>
    <table border='1' cellpadding='6'>
      <tr><th>Subject</th><th>Topics</th><th>Time</th><th>Notes</th></tr>
      {table_rows}
    </table>
    <p><strong>Total today: {total_mins} minutes</strong></p>
    <p>Stay consistent. See you tomorrow.</p>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"StudyPilot - Your plan for {today}"
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg.attach(MIMEText(html, "html"))

    # Gmail SMTP
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

    print(f"Nudge sent to {recipient_email}")


