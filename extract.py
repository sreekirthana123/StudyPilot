import os
import json
import pdfplumber
from groq import Groq
from dotenv import load_dotenv

# Load environment variables and initialize client globally
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_syllabus(text):
    prompt = f"""
You are a JSON extraction engine.

Extract ONLY the syllabus units from the text below.
Return ONLY valid JSON.

Rules:
- Output must be a JSON array.
- Each array element is one unit object.
- Do NOT wrap the JSON in markdown.

Schema:
[
  {{
    "subject": "string",
    "unit": "string",
    "chapters": ["string"],
    "exam date": "YYYY-MM-DD or null",
    "weightage": "percentage or null"
  }}
]

Syllabus text:
{text}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=4000,
    )


    return response.choices[0].message.content or ""



def clean_json_response(raw):
    start = raw.find("[")
    end = raw.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON found")

    return raw[start : end + 1]



def main():
    # Try a few common locations for the input PDF
    script_dir = os.path.dirname(__file__)

    # Change this filename if your input PDF has a different name.
    input_filename = "sample.pdf"
    output_filename = "syllabus_output.json"

    candidates = [
        os.path.join(script_dir, input_filename),
        os.path.join(os.path.dirname(script_dir), input_filename),
        # Common: /Pictures under the user home
        os.path.join(script_dir, "..", "..", "..", "Pictures", input_filename),
        os.path.join(os.getcwd(), "..", "..", "..", "Pictures", input_filename),
        os.path.join(os.getcwd(), "..", "Pictures", input_filename),
        os.path.join(os.path.dirname(script_dir), "..", "Pictures", input_filename),
    ]

    pdf_path = next((p for p in candidates if os.path.exists(p)), None)
    if not pdf_path:
        raise FileNotFoundError(
            "Could not find input PDF. Looked in: " + ", ".join(candidates)
        )

    # 1. Extract text from the PDF file
    text = extract_text_from_pdf(pdf_path)

    # 2. Send text to Groq AI model
    raw_output = extract_syllabus(text)

    # 3. Clean and parse raw string into a Python list/dictionary
    cleaned = clean_json_response(raw_output)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: strip trailing content after the last JSON bracket
        last = cleaned.rfind("]")
        if last != -1:
            data = json.loads(cleaned[: last + 1])
        else:
            raise

    # 4. Create and save the data to a new JSON file
    output_path = os.path.join(script_dir, output_filename)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print("Json has been written properly")
    print(data)



if __name__ == "__main__":
    # main()
    pass


