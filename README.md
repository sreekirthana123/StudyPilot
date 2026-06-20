# 📚 Study Pilot

**Stop guessing what to study.**

[**Access the Live App Here**](https://sree-kirthana-studypilot.streamlit.app/)

Study Pilot is an intelligent, automated AI study assistant designed to transform raw course syllabus documents into structured, priority-weighted, and manageable daily study schedules. 

Built with a focus on MLOps and Generative AI, this dashboard helps students optimize their revision sessions based on upcoming deadlines and available daily time commitments.

## 🚀 Key Features

* **Intelligent Syllabus Extraction:** Parses messy PDF syllabus files into clean, actionable data.
* **AI-Powered Planning:** Uses LLM-driven logic (via Groq Cloud) to break down massive workloads into bite-sized daily tasks.
* **Dynamic Dashboard:** A modern, minimal, and responsive UI built with Streamlit.
* **Optimized Revision:** Automatically prioritizes topics based on upcoming exam dates and individual study capacity.
* **PDF Export:** Generate your custom study plan as a clean, printable PDF.

## 🛠 Tech Stack

* **Framework:** Streamlit
* **AI/LLM:** Llama 3.1 (via Groq Cloud API)
* **Frontend:** Custom CSS/Minimal Aurora Theme
* **Processing:** Data Orchestration Layer
* **Deployment:** Streamlit Community Cloud

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

*Created by [V Sree Kirthana]*
