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
