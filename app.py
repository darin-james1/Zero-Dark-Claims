import datetime
from io import BytesIO

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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
# Page config & header
# ======================

st.set_page_config(
    page_title="Zero Dark Claims – VA Letter Helper",
    layout="centered"
)

st.image("logo.png", width=160)

st.title("Zero Dark Claims – VA Letter Helper")

st.markdown(
    """
**Privacy & Use Notice**

This tool runs locally in your browser and on your device. No Veteran-identifying information is stored, logged, or sent to any external server. All letter drafts are generated for you to download, review, and edit, and you are responsible for how and where you choose to share them with your doctor, VSO, attorney, or other representative.
"""
)

# ======================
# Navigation state
# ======================

if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Quick Drafts"

st.sidebar.title("Navigation")
page_choice = st.sidebar.radio(
    "Go to:",
    ["Quick Drafts", "Advanced Letter Builder"],
    index=0 if st.session_state.nav_page == "Quick Drafts" else 1,
)
st.session_state.nav_page = page_choice

st.markdown("---")

# ======================
# QUICK DRAFTS PAGE
# ======================

if st.session_state.nav_page == "Quick Drafts":

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

elif st.session_state.nav_page == "Advanced Letter Builder":
    st.subheader("Advanced VA Letter Builder")
    st.write(
        "This page will host the multi-letter-type builder (initial service connection, secondary, "
        "increase, TDIU, appeals, lay/buddy, etc.)."
    )
    st.info(
        "Advanced builder is wired into navigation. Next step is to plug in the structured letter "
        "types and prompts you designed."
    )

# ======================
# FOOTER
# ======================

st.markdown(
    """
---
**Disclaimer:** Zero Dark Claims is an educational drafting tool and does not provide legal, medical, or financial advice. Use of this tool does not create an attorney–client, doctor–patient, or representative relationship. You should consult a qualified professional (VSO, attorney, accredited agent, or healthcare provider) before relying on any drafted content.
"""
)
