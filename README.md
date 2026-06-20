# 📚 Study Pilot

**Stop guessing what to study.**

[**Access the Live App Here**](https://sree-kirthana-studypilot.streamlit.app/)

Study Pilot is an intelligent, automated AI study assistant designed to transform raw course syllabus documents into structured, priority-weighted, and manageable daily study schedules.

## 📂 Project Structure

* **`app.py`**: The main entry point; manages the Streamlit UI, user interactions, and the 3-page navigation flow.
* **`extract.py`**: The ingestion engine; uses `pdfplumber` and Llama 3.1 to convert unstructured syllabus PDFs into structured JSON data.
* **`planner.py`**: The "brain." It calculates subject priorities based on exam proximity and weightage, then interfaces with Llama 3.1 via Groq API to generate the final study schedule.
* **`pdf_export.py`**: Logic to convert the generated JSON timetable into a clean, printable PDF document.
* **`reminder.py`**: Manages the logic for sending daily notifications to keep the user on track.
* **`syllabus_output.json`**: The structured data file containing your subjects, chapters, and exam metadata.
* **`timetable.json`**: The final output file containing your generated study schedule.

## 🛠 Tech Stack
* **Framework:** Streamlit
* **AI/LLM:** Llama 3.1 (via Groq Cloud API)
* **Processing:** pdfplumber (Data Extraction)
* **Deployment:** Streamlit Community Cloud

---

## 📂 Project Structure

* **`app.py`**: The main entry point; manages the Streamlit UI, user interactions, and the 3-page navigation flow.
* **`extract.py`**: The ingestion engine; uses `pdfplumber` and Llama 3.1 to convert unstructured syllabus PDFs into structured JSON data.
* **`planner.py`**: The "brain." It calculates subject priorities based on exam proximity and weightage, then interfaces with Llama 3.1 via Groq API to generate the final study schedule.
* **`pdf_export.py`**: Logic to convert the generated JSON timetable into a clean, printable PDF document.
* **`reminder.py`**: Manages the logic for sending daily notifications to keep the user on track.
* **`syllabus_output.json`**: The structured data file containing your subjects, chapters, and exam metadata.
* **`timetable.json`**: The final output file containing your generated study schedule.
---

## 📂 Folder Structure

```text
StudyPilot/
├── .streamlit/             # App configuration (theme settings)
├── app.py                  # Main Streamlit dashboard UI
├── extract.py              # PDF text ingestion & JSON conversion
├── planner.py              # Llama 3.1 AI planning & scheduling
├── pdf_export.py           # ReportLab PDF timetable generator
├── reminder.py             # Email notification logic
├── style.css               # Custom Minimal Aurora UI styles
├── sample.pdf              # Example syllabus for testing
├── requirements.txt        # Project dependencies
└── syllabus_output.json    # Structured syllabus data
---


*Created by [V Sree Kirthana]*
