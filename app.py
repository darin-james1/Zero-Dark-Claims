import datetime
from io import BytesIO

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from config.letter_types import LETTER_TYPES
from openai import OpenAI


# ======================
# THEME & GLOBAL STYLES
# ======================

st.set_page_config(
    page_title="Zero Dark Claims – VA Letter Helper",
    layout="centered"
)

st.markdown(
    """
    <style>
    :root {
      --zdc-bg: #050816;
      --zdc-bg-soft: #0b1220;
      --zdc-accent: #00e0ff;
      --zdc-accent-soft: rgba(0, 224, 255, 0.16);
      --zdc-text-main: #f9fafb;
      --zdc-text-muted: #d1d5db;
      --zdc-border-subtle: #1f2937;
    }

    .stApp {
      background: radial-gradient(circle at top, #111827 0, #020617 55%);
      color: var(--zdc-text-main);
      font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .zdc-card {
      background: radial-gradient(circle at top left, #111827, #020617);
      border-radius: 1.5rem;
      padding: 1.5rem 1.8rem;
      border: 1px solid rgba(148,163,184,0.18);
      box-shadow: 0 24px 80px rgba(15,23,42,0.85);
    }

        .stChatMessage {
      border-radius: 1.1rem !important;
      border: 1px solid rgba(31,41,55,0.9) !important;
      background: rgba(15,23,42,0.9) !important;
    }

    .stButton > button {
      background: linear-gradient(135deg, #22d3ee, #0ea5e9);
      border: none;
      box-shadow: 0 18px 45px rgba(56,189,248,0.45);
      font-weight: 600;
      border-radius: 999px;
      padding: 0.55rem 1.3rem;
    }

    .stTabs [data-baseweb="tab"] p {
      color: #f9fafb !important;
    }

    /* Force all form field labels to white */
    .stApp div[data-testid="stForm"] label p,
    .stApp div[data-testid="stForm"] label span,
    .stApp label p,
    .stApp label span,
    .stApp .stTextInput label div,
    .stApp .stTextArea label div,
    .stApp .stSelectbox label div {
      color: #ffffff !important;
      opacity: 1 !important;
    }
    /* Make all field titles (help text above inputs) white */
    .stApp div[data-testid="stMarkdown"] p {
      color: #ffffff !important;
    }

    .stApp [data-testid="stTextInput"] label div,
    .stApp [data-testid="stTextArea"] label div,
    .stApp [data-testid="stSelectbox"] label div {
      color: #ffffff !important;
    }


    </style>
    """,
    unsafe_allow_html=True,

)


# ======================
# CHATBOT SETUP ("Avery")
# ======================

VA_COACH_SYSTEM_PROMPT = """
You are a disability claims writing coach named Avery helping a Veteran improve the clarity of their written statements.

Your job is to:
- Help them clearly describe their own experiences, not invent new facts.
- Focus on structure, plain language, and specific, concrete examples (dates, frequency, duration, impact on work, family, sleep, etc.).
- Tailor your guidance to the section they are working on (for example: in-service event, current symptoms, daily impact, nexus, lay/witness statement).
- Use calm, respectful, Veteran-friendly language.

You must NOT:
- Give legal, medical, or financial advice.
- Claim to represent them before VA, or say you are VA, a VSO, or an attorney.
- Predict ratings, promise outcomes, or tell them what percentage they “should” get.
- Tell them exactly what to write as if you were a witness; instead, give examples and let them adapt in their own words.

Always:
- When they paste a draft, first point out 2–4 ways to make it clearer (missing details, timeline, frequency, daily impact).
- Then provide a sample rewrite or bullet suggestions they can copy and adapt.
- Encourage them to review their final letters with a VSO, accredited agent, or attorney before submitting.
"""

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "avery_messages" not in st.session_state:
    st.session_state.avery_messages = [
        {"role": "system", "content": VA_COACH_SYSTEM_PROMPT}
    ]


# ======================
# PDF helper
# ======================

def build_pdf(text_blocks):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    for text in text_blocks:
        story.append(Paragraph(text, styles["Normal"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    buffer.seek(0)
    return buffer


# ======================
# ADVANCED BUILDER LOGIC
# ======================

def advanced_builder():
    st.subheader("Advanced VA Letter Builder")

    type_key = st.selectbox(
        "Letter type",
        options=list(LETTER_TYPES.keys()),
        format_func=lambda k: LETTER_TYPES[k]["label"],
        help="Choose what kind of VA-support letter you want to build.",
    )

    cfg = LETTER_TYPES[type_key]
    st.caption(cfg["description"])

    st.markdown("### Step 1 – Provide details for each section")

    user_inputs = {}
    for section in cfg["sections"]:
        user_inputs[section] = st.text_area(section, height=140)

    if st.button("Generate draft letter"):
        content_blocks = []
        for section, text in user_inputs.items():
            if text.strip():
                content_blocks.append(f"{section}:\n{text.strip()}")
        merged_content = "\n\n".join(content_blocks)

        full_prompt = cfg["system_prompt"] + "\n\nVETERAN INPUT:\n" + merged_content

        # TODO: replace with your actual LLM call
        generated = full_prompt  # placeholder so UI works

        st.markdown("### Draft letter")
        st.write(generated)


# ======================
# Page header (inside card)
# ======================

st.markdown('<div class="zdc-card">', unsafe_allow_html=True)

st.image("logo.png", width=160)
st.title("Zero Dark Claims – VA Letter Helper")

st.markdown(
    """
**Privacy & Use Notice**

This tool runs locally in your browser and on your device. No Veteran-identifying information is stored, logged, or sent to any external server. All letter drafts are generated for you to download, review, and edit, and you are responsible for how and where you choose to share them with your doctor, VSO, attorney, or other representative.
"""
)

st.markdown("---")

# ======================
# Tabs navigation (no sidebar)
# ======================

tab_quick, tab_advanced = st.tabs(["Quick Drafts", "Advanced Letter Builder"])

# ======================
# QUICK DRAFTS PAGE
# ======================

with tab_quick:
    st.write("Choose the type of letter you want to draft and then fill in your details.")

    st.markdown("### Step 1 – Choose Letter Type")

    if "letter_choice" not in st.session_state:
        st.session_state.letter_choice = None

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Personal Statement"):
            st.session_state.letter_choice = "personal"

    with col2:
        if st.button("Medical Nexus Letter Outline"):
            st.session_state.letter_choice = "nexus"

    with col3:
        if st.button("Lay/Witness Statement (VA Form 21-10210 style)"):
            st.session_state.letter_choice = "lay"

    letter_choice = st.session_state.letter_choice

    st.markdown("---")

    if letter_choice is not None:
        st.markdown("### Step 2 – Enter Your Information")

        # Common veteran info
        st.header("Veteran Information")
        veteran_name = st.text_input("Veteran full name")
        va_ssn = st.text_input("VA file number or SSN (last 4 is OK)")
        dob = st.text_input("Veteran date of birth (MM/DD/YYYY)")
        branch = st.text_input("Branch of service", placeholder="e.g., Army, Navy, Marine Corps")
        service_start = st.text_input("Service start year", placeholder="e.g., 2000")
        service_end = st.text_input("Service end year", placeholder="e.g., 2012")

        if letter_choice == "lay":
            st.header("Witness / Claimant Information")
            witness_name = st.text_input("Witness full name (person writing this statement)")
            relationship = st.text_input("Relationship to Veteran", placeholder="e.g., spouse, shipmate, squad leader")
            known_since = st.text_input("How long have you known the Veteran? (year or date)", placeholder="e.g., since 2005")
            witness_contact = st.text_input("Witness phone or email")
        else:
            witness_name = ""
            relationship = ""
            known_since = ""
            witness_contact = ""

        st.header("Service & Condition / Statement Content")

        location = st.text_input(
            "Duty station / location of main event",
            placeholder="e.g., Camp Pendleton; Baghdad; USS Example"
        )
        event = st.text_area(
            "Service event / exposure (what happened?)",
            placeholder="Example: IED blast, aircraft noise, burn pits, training accident"
        )
        condition = st.text_input(
            "Main condition you’re talking about",
            placeholder="e.g., PTSD, tinnitus, back pain, migraines"
        )
        onset_date = st.text_input(
            "When did symptoms or noticeable changes start?",
            placeholder="e.g., during deployment in 2008"
        )
        daily_impact = st.text_area(
            "How does this affect daily life now?",
            placeholder="Example: problems with sleep; avoids crowds; pain limits walking; misses work; changed personality"
        )

        if letter_choice == "lay":
            lay_examples = st.text_area(
                "Specific witnessed examples (for Section III – Statement)",
                placeholder="Example: Since returning in 2019, I’ve seen him sleep with a light on, startle at loud noises, and withdraw from family gatherings."
            )
        else:
            lay_examples = ""

        # ======== CHAT WITH AVERY – tied to daily impact section ========

        st.markdown("### Chat with Avery, your writing guide")
        st.caption("Educational writing help only. Not legal, medical, or financial advice.")

        # show history (excluding system)
        for msg in st.session_state.avery_messages[1:]:
            role = "assistant" if msg["role"] == "assistant" else "user"
            with st.chat_message(role):
                st.markdown(msg["content"])

        user_prompt = st.chat_input("Ask Avery for help with this section...")
        if user_prompt:
            section_name = "Daily impact of condition"
            draft_text = daily_impact or "[No draft text yet]"

            context = f"""Current section: {section_name}
Current draft:
{draft_text}

Veteran’s question:
{user_prompt}
"""
            st.session_state.avery_messages.append({"role": "user", "content": context})

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    resp = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.avery_messages,
                        temperature=0.3,
                        max_tokens=400,
                    )
                    reply = resp.choices[0].message.content
                    st.markdown(reply)

            st.session_state.avery_messages.append({"role": "assistant", "content": reply})

        st.markdown("---")

        # PERSONAL STATEMENT
        if letter_choice == "personal":
            if st.button("Generate Personal Statement"):
                today = datetime.date.today().strftime("%B %d, %Y")
                blocks = [
                    "<b>VA Form 21-4138: Statement in Support of Claim (DRAFT)</b>",
                    f"<b>Veteran:</b> {veteran_name}     <b>VA File/SSN:</b> {va_ssn}     <b>Date:</b> {today}",
                    "",
                    (
                        f"I, {veteran_name}, served in the United States {branch} from approximately {service_start} "
                        f"to {service_end}. While assigned to {location}, I experienced the following event(s) or "
                        f"conditions: {event}."
                    ),
                    "",
                    (
                        f"<b>It is my contention that these in-service event(s) are at least as likely as not "
                        f"(a 50 percent or greater probability) the cause of, or a significant contributor to, "
                        f"my current {condition}.</b>"
                    ),
                    "",
                    (
                        f"My symptoms began around {onset_date} and have been present continuously since that time. "
                        f"Today, this condition affects me in the following ways: {daily_impact}."
                    ),
                    "",
                    (
                        "These ongoing limitations significantly affect my daily functioning, relationships, work capacity, "
                        "and overall quality of life."
                    ),
                    "",
                    (
                        "I understand that this statement will be used in connection with my claim for VA disability benefits. "
                        "<b>I certify that the statements on this page are true and correct to the best of my knowledge and belief.</b>"
                    ),
                    "",
                    "Veteran Signature: _______________________________     Date: _______________",
                ]

                pdf = build_pdf(blocks)
                st.success("Personal Statement draft generated. Download, review, edit, and submit to VA.")
                st.download_button(
                    label="Download Personal Statement (PDF)",
                    data=pdf,
                    file_name="va_personal_statement_draft.pdf",
                    mime="application/pdf",
                )

        # NEXUS LETTER
        elif letter_choice == "nexus":
            if st.button("Generate Medical Nexus Outline"):
                today = datetime.date.today().strftime("%B %d, %Y")
                blocks = [
                    "<b>MEDICAL NEXUS OPINION LETTER</b>",
                    "<b>For Department of Veterans Affairs Disability Claim</b>",
                    "",
                    f"<b>Date:</b> {today}",
                    f"<b>Veteran Name:</b> {veteran_name}",
                    f"<b>Date of Birth:</b> {dob}",
                    f"<b>VA File Number / SSN:</b> {va_ssn}",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "<b>TO THE EXAMINING/TREATING PROVIDER:</b>",
                    "",
                    (
                        "This letter outline is provided to assist you in preparing a medical nexus opinion for a VA disability claim. "
                        "Please review the veteran's complete medical records, service records, and any relevant clinical literature "
                        "before finalizing your opinion."
                    ),
                    "",
                    "The VA uses the standard <b>\"at least as likely as not\"</b> (≥50% probability) for establishing service connection.",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "<b>SECTION 1: CURRENT DIAGNOSIS</b>",
                    "",
                    f"The veteran currently carries a diagnosis of: <b>{condition}</b>",
                    "",
                    "[Provider: Please confirm diagnosis and add ICD-10 code if applicable]",
                    "",
                    "Diagnosis confirmed: ☐ Yes   ☐ No   ☐ Modified (explain): _________________________________",
                    "",
                    "ICD-10 Code: ______________",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "<b>SECTION 2: PERTINENT SERVICE HISTORY</b>",
                    "",
                    f"Branch of Service: {branch}",
                    f"Dates of Service: Approximately {service_start} to {service_end}",
                    f"Duty Location/Assignment: {location}",
                    "",
                    "<b>Reported In-Service Event(s) / Exposure(s):</b>",
                    f"{event}",
                    "",
                    f"<b>Symptom Onset:</b> {onset_date}",
                    "",
                    f"<b>Current Impact:</b> {daily_impact}",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "<b>SECTION 3: MEDICAL OPINION (Provider to Complete)</b>",
                    "",
                    (
                        "After reviewing the veteran's medical records, service records, and the information provided above, "
                        "it is my professional medical opinion that:"
                    ),
                    "",
                    f"The veteran's current diagnosis of <b>{condition}</b> is:",
                    "",
                    "☐  <b>At least as likely as not (≥50% probability)</b>",
                    "☐  <b>Less likely than not (&lt;50% probability)</b>",
                    "",
                    (
                        "caused by, the result of, or <b>permanently aggravated beyond its natural progression</b> by the "
                        "in-service event(s), injury, or exposure described above."
                    ),
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "<b>SECTION 4: DETAILED RATIONALE (Provider to Complete)</b>",
                    "",
                    "Please provide a detailed explanation supporting your medical opinion, including:",
                    "",
                    "• Pertinent Medical History: Timeline of symptoms, prior diagnoses, treatment history",
                    "• Objective Clinical Findings: Physical exam, imaging, laboratory data, diagnostic tests",
                    "• Medical Literature / Evidence Base: Relevant studies, clinical guidelines, or accepted medical principles",
                    "• Causation Analysis: How the in-service event(s) could plausibly cause or aggravate this condition",
                    "• Temporal Relationship: Connection between timing of service event and symptom onset/progression",
                    "",
                    "[Provider: Please write your detailed rationale here or attach separate documentation]",
                    "",
                    "_________________________________________________________________________________",
                    "",
                    "_________________________________________________________________________________",
                    "",
                    "_________________________________________________________________________________",
                    "",
                    "_________________________________________________________________________________",
                    "",
                    "_________________________________________________________________________________",
                    "",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    "",
                    "<b>PROVIDER CERTIFICATION</b>",
                    "",
                    "I certify that I have reviewed the available records and that the opinions expressed above are given "
                    "to a reasonable degree of medical certainty based on my clinical expertise and the evidence available.",
                    "",
                    "Provider Name (Print): _________________________________________________",
                    "",
                    "Professional Title / Specialty: _________________________________________",
                    "",
                    "License Number & State: ________________________________________________",
                    "",
                    "Provider Signature: ___________________________________   Date: _______________",
                    "",
                    "Contact Information: ___________________________________________________",
                ]

                pdf = build_pdf(blocks)
                st.success("Medical Nexus Letter Outline draft generated. Download and bring to your doctor for completion and signature.")
                st.download_button(
                    label="Download Medical Nexus Outline (PDF)",
                    data=pdf,
                    file_name="va_nexus_letter_outline_draft.pdf",
                    mime="application/pdf",
                )

        # LAY / WITNESS STATEMENT
        elif letter_choice == "lay":
            if st.button("Generate Lay/Witness Statement (VA Form 21-10210 style)"):
                today = datetime.date.today().strftime("%B %d, %Y")
                observed_text = lay_examples if lay_examples else daily_impact

                blocks = [
                    "<b>VA Form 21-10210: Lay/Witness Statement (CONTENT DRAFT)</b>",
                    "",
                    "This draft is organized to match the sections of VA Form 21-10210 so you can copy it onto the official VA form.",
                    "",
                    "Veteran's Name: " + veteran_name,
                    "Social Security Number / VA File Number: " + va_ssn,
                    "Date of Birth: " + dob,
                    "",
                    (
                        "I have personal knowledge of the Veteran, " + veteran_name +
                        ", who served in the United States " + branch +
                        " from approximately " + service_start + " to " + service_end + ". "
                        "I know the Veteran because I am their " + relationship +
                        ", and I have known them since around " + known_since + ". "
                        "I am providing this statement to describe what I have personally seen and observed regarding "
                        "the Veteran’s " + condition + " and how it affects them."
                    ),
                    "",
                    (
                        "During and after the Veteran’s military service at " + location +
                        ", they reported experiencing or I am aware that they experienced the following event(s) or conditions: "
                        + event + "."
                    ),
                    "",
                    (
                        "Since around " + onset_date +
                        ", I have personally observed the following changes, symptoms, or limitations: "
                        + observed_text
                    ),
                    "",
                    (
                        "These changes have affected the Veteran’s daily life in ways such as difficulty with work, "
                        "family life, sleep, social activities, and overall functioning."
                    ),
                    "",
                    (
                        "I am not a medical professional and am not offering a medical opinion. "
                        "I am only describing what I have personally seen, heard, or observed about the Veteran’s condition "
                        "and how it affects them."
                    ),
                ]

                pdf = build_pdf(blocks)
                st.success("Lay/Witness Statement draft generated. Copy this content into VA Form 21-10210.")
                st.download_button(
                    label="Download Lay/Witness Statement Draft (PDF)",
                    data=pdf,
                    file_name="va_form_21_10210_lay_statement_draft.pdf",
                    mime="application/pdf",
                )


# ======================
# ADVANCED LETTER BUILDER PAGE
# ======================

with tab_advanced:
    advanced_builder()


# ======================
# FOOTER
# ======================

st.markdown(
    """
---
**Disclaimer:** Zero Dark Claims is an educational drafting tool and does not provide legal, medical, or financial advice. Use of this tool does not create an attorney–client, doctor–patient, or representative relationship. You should consult a qualified professional (VSO, attorney, accredited agent, or healthcare provider) before relying on any drafted content.
"""
)

st.markdown("</div>", unsafe_allow_html=True)
