import streamlit as st
import json, os, tempfile
from extract import extract_syllabus
from planner import allocate_hours, generate_timetable, clean_json_response
from pdf_export import generate_pdf, load_timetable
from reminder import send_daily_nudge
import streamlit as st
# Add this right after st.set_page_config
st.markdown("""<style>.stButton>button { background-color: #0D9488 !important; color: white !important; }</style>""", unsafe_allow_html=True)

# 1. Page Config
st.set_page_config(page_title="Study Pilot", page_icon="📚", layout="centered")

# BRUTE FORCE CSS INJECTION: This cannot be cached or ignored by the browser.
st.markdown("""
    <style>
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border: 3px solid #0D9488 !important; 
            box-shadow: 0 8px 32px 0 rgba(13, 148, 136, 0.4) !important; 
            background: rgba(255, 255, 255, 0.6) !important; 
            backdrop-filter: blur(16px) !important;
            -webkit-backdrop-filter: blur(16px) !important;
            border-radius: 16px !important;
            padding: 2rem !important;
        }
    </style>
""", unsafe_allow_html=True)


# 2. Connect the CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Initialize Session State for the 3-page flow
if 'step' not in st.session_state:
    st.session_state.step = 1

def go_to_next_step():
    st.session_state.step += 1

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.step = 1

# --- Central UI Container ---
with st.container(border=True):
    st.markdown('<div class="app_container_content">', unsafe_allow_html=True)

    # ==========================================
    # PAGE 1: Introduction
    # ==========================================
    if st.session_state.step == 1:
        st.title("📚 Study Pilot")
        st.markdown("### Stop guessing what to study.")
        st.write(
            "Welcome to your personal AI study assistant. Study Pilot takes your raw course syllabus "
            "and intelligently breaks it down into an optimized, manageable daily schedule based on "
            "the hours you have available."
        )
        st.write("Upload your document, set your time, and let the agent do the heavy lifting.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """<div style='font-size:18px; font-weight:800; color:#0F766E; text-align:center;'>Created by V Sree Kirthana</div>""",
            unsafe_allow_html=True,
        )

        
        st.button("Next ➔", on_click=go_to_next_step, type="primary", use_container_width=True)

    # ==========================================
    # PAGE 2: The Inputs (Upload & Hours)
    # ==========================================
    elif st.session_state.step == 2:
        st.title("Step 2: Your Study Profile")
        
        uploaded_file = st.file_uploader("Upload your syllabus (PDF format)", type=["pdf"])
        email = st.text_input("Email address (for daily nudges)")
        hours = st.slider("Daily study commitment (Hours)", min_value=1, max_value=8, value=4)

        if st.button("🚀 Generate Study Plan", type="primary", use_container_width=True):
            if not uploaded_file:
                st.error("Please upload a syllabus PDF file to continue.")
            else:
                with st.spinner("Analyzing your syllabus..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name

                    from extract import extract_text_from_pdf
                    raw_text = extract_text_from_pdf(tmp_path)
                    raw_syllabus = extract_syllabus(raw_text)
                    cleaned = raw_syllabus.strip()
                    if "```" in cleaned:
                        cleaned = cleaned.split("```")[1]
                        if cleaned.startswith("json"):
                            cleaned = cleaned[4:]

                    syllabus = json.loads(cleaned.strip())
                    
                    with st.spinner("Optimizing your 7-day schedule..."):
                        allocated_hours = allocate_hours(syllabus, daily_hours=hours)
                    raw_timetable = generate_timetable(allocated_hours, daily_hours=hours)

                    cleaned_timetable = json.dumps(raw_timetable) if isinstance(raw_timetable, dict) else raw_timetable.strip()
                    if "```" in cleaned_timetable:
                        cleaned_timetable = cleaned_timetable.split("```")[1]
                        if cleaned_timetable.startswith("json"):
                            cleaned_timetable = cleaned_timetable[4:]
                            
                    start = cleaned_timetable.find("{")
                    end = cleaned_timetable.rfind("}")
                    cleaned_timetable = cleaned_timetable[start : end + 1]

                    timetable_data = json.loads(cleaned_timetable)

                    with open("timetable.json", "w") as f:
                        json.dump(timetable_data, f, indent=2)

                with st.spinner("Generating your PDF document..."):
                    rows, summary = load_timetable("timetable.json")
                    generate_pdf(rows, summary, output_path="timetable.pdf")
                    
                    # Store data in session state so Page 3 can access it
                    st.session_state.timetable_data = timetable_data
                    st.session_state.email = email
                    st.session_state.rows = rows
                
                # Move to the final page
                st.session_state.step = 3
                st.rerun()

    # ==========================================
    # PAGE 3: The Output (Timetable & Conclusion)
    # ==========================================
    elif st.session_state.step == 3:
        st.title("Step 3: Your Study Plan")
        st.success("✅ Study Plan successfully generated!")

        # --- Central UI Container (bordered) for CSS to reliably highlight ---
        with st.container(border=True):
            st.markdown('<div id="timetable-shell">', unsafe_allow_html=True)


        for day in st.session_state.timetable_data["timetable"]:
            with st.container(border=True):
                st.subheader(f"Day {day['day']} • {day['date']}")

                for slot in day['slots']:
                    # 1. Join chapters if they exist
                    chapters = ", ".join(slot.get("chapters_to_cover", []))

                    # 2. Display Subject and Time
                    st.markdown(f"**{slot['subject']}** — `{slot['duration_minutes']} mins`")

                    # 3. Handle the Missing Focus AND fix the blurriness by using st.markdown
                    if chapters.strip():
                        st.markdown(f"🎯 **Focus:** {chapters}")
                    else:
                        st.markdown("🎯 **Focus:** *General Review & Practice*")

            st.divider()

        st.markdown('</div>', unsafe_allow_html=True)

        # Download Button
        with open("timetable.pdf", "rb") as f:
            st.download_button(
                label="📄 Download Timetable (PDF)",
                data=f,
                file_name="my_study_plan.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True
            )

            
        # Email Logic
        if st.session_state.email:
            try:
                send_daily_nudge(st.session_state.rows, recipient_email=st.session_state.email)
                st.info(f"Notifications active. Daily nudges will be sent to {st.session_state.email}")
            except Exception as e:
                st.warning(f"Could not connect to the email service: {e}")

        # Conclusion
        st.markdown("---")
        st.markdown("### 🎉 Thank you for using Study Pilot!")
        st.write("We wish you the best of luck with your upcoming studies. You've got this!")
        
        st.button("Start Over", on_click=reset_app)

    st.markdown('</div>', unsafe_allow_html=True)
