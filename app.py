import datetime
from io import BytesIO

import streamlit as st
st.markdown(
    """
    <style>
    /* Completely hide the top toolbar / search area */
    div[data-testid="stToolbar"],
    header[data-testid="stHeader"],
    div[role="banner"] {
        display: none !important;
        visibility: hidden !important;
    }

    /* Pull content up a bit now that the header is gone */
    .block-container {
        padding-top: 1.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <style>
    /* Center column similar to your landing page */
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
        margin: 0 auto;
    }

    /* Top nav buttons (Quick Drafts / Future Letter Builder) as tab-like text */
    div.st-key-mode_quick button,
    div.st-key-mode_advanced button {
        background-color: transparent;
        color: #e5e7eb;
        border-radius: 0;
        border: none;
        font-weight: 600;
        padding: 0.25rem 0;
        font-size: 0.95rem;
    }

    /* Hover effect using your orange accent */
    div.st-key-mode_quick button:hover,
    div.st-key-mode_advanced button:hover {
        color: #ea580c;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

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

# Global CSS
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

    .avery-wrapper {
      position: fixed;
      top: 20%;
      right: 2%;
      z-index: 999;
    }

    .avery-avatar {
      width: 140px;
      height: auto;
      border-radius: 999px;
      box-shadow: 0 18px 45px rgba(56,189,248,0.4);
    }

    /* Make the main content not run under the chat input */
    .main .block-container {
      padding-bottom: 6rem; /* space for chat input */
    }

    /* Limit chat history height so it scrolls, input looks fixed */
    .chat-history-container {
      max-height: calc(100vh - 200px);
      overflow-y: auto;
      padding-right: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Hide GitHub / viewer badge
st.markdown(
    """
    <style>
    .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_,
    .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none !important;
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

if "messages" not in st.session_state:
    st.session_state.messages = []


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

# Bubble above the logo
st.markdown(
    """
    <div style="
        margin-bottom: 1.0rem;
        padding: 0.75rem 1.25rem;
        border-radius: 9999px;
        background: rgba(15,23,42,0.95);
        border: 1px solid rgba(148,163,184,0.4);
    ">
        <div style="
            font-size: 1.5rem;        /* match title size */
            font-weight: 700;
            color: #f9fafb;
            line-height: 1.25;
        ">
            Built by veterans, for veterans, to support your VA disability claim.
        </div>        
    </div>
    """,
    unsafe_allow_html=True,
)

# Logo + main title
st.image("logo.png", width=160)
col_main, col_right = st.columns([4, 1])

with col_main:
    st.title("Zero Dark Claims – VA Letter Helper")

    st.markdown(
        """
    **Privacy & Use Notice**

    For educational support only – not legal, medical, or financial advice.

    This tool runs locally in your browser and on your device. No Veteran-identifying information is stored, logged, or sent to any external server. Your information stays here until you close this window.  

    PRO TIP: Generate your letter then look it over and come back to this page to update/change your information and generate another letter. Repeat until you get the letter you want. 
    
    All letter drafts are generated for you to download, review, and edit, and you are responsible for how and where you choose to share them with your doctor, VSO, attorney, or other representative.
    """
    )

    st.markdown("---")

    st.markdown('<div class="chat-history-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown(
        """
        <div class="avery-wrapper">
            <img src="https://your-avery-url.png" class="avery-avatar" />
        </div>
        """,
        unsafe_allow_html=True,
    )




# ======================
# Top page buttons (replace tabs)
# ======================

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "quick"

col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    if st.button("Quick Drafts", key="mode_quick", use_container_width=True):
        st.session_state.active_tab = "quick"
with col_nav2:
    if st.button("Future Letter Builder", key="mode_advanced", use_container_width=True):
        st.session_state.active_tab = "advanced"

st.markdown("---")

# ======================
# QUICK DRAFTS PAGE
# ======================

if st.session_state.active_tab == "quick":

    # Mini-hero section
    st.markdown(
        """
        <div style="margin-bottom: 1.5rem;">
            <h2 style="margin-bottom: 0.25rem;">Draft VA-ready letters in minutes.</h2>
            <p style="margin-top: 0.25rem; font-size: 0.95rem; color: #9ca3af;">
                Answer plain-language questions, then download veteran-friendly drafts you can review,
                edit, and submit with your VA claim.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("Choose the type of letter you want to draft and then fill in your details.")
    st.markdown("### Step 1 – Choose Letter Type")

    if "letter_choice" not in st.session_state:
        st.session_state.letter_choice = None

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "Personal Statement",
            key="btn_personal",
            help="This should be input by the veteran.",
        ):
            st.session_state.letter_choice = "personal"

    with col2:
        if st.button(
            "Medical Nexus Letter Outline",
            key="btn_nexus",
            help="Bring this outline to your primary care provider for completion.",
        ):
            st.session_state.letter_choice = "nexus"

    with col3:
        if st.button(
            "Lay/Witness Statement (VA Form 21-10210 style)",
            key="btn_lay",
            help="This should be input by the witness/buddy.",
        ):
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
            "Main condition you're talking about",
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
                placeholder="Example: Since returning in 2019, I've seen him sleep with a light on, startle at loud noises, and withdraw from family gatherings."
            )
        else:
            lay_examples = ""

        # Chat with Avery
        st.markdown("### Chat with Avery, your writing guide")
        st.caption("Educational writing help only. Not legal, medical, or financial advice.")

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

Veteran's question:
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

        # PERSONAL / NEXUS / LAY blocks unchanged...
        # (keep your existing generation + PDF code here, still under the `if st.session_state.active_tab == "quick":`)

        # PERSONAL STATEMENT, NEXUS LETTER, LAY / WITNESS STATEMENT blocks
        # go here exactly as you have them now.

# ======================
# FUTURE LETTER BUILDER PAGE
# ======================

elif st.session_state.active_tab == "advanced":
    st.header("Future Letter Builder")
    st.write("This page is under construction.  Additional forms will go here.")
    # advanced_builder() later


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
