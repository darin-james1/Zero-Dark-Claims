import datetime
from io import BytesIO

import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image


def build_pdf(text_blocks):
    """Create a simple PDF from a list of text blocks."""
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


# ---- Page config ----
st.set_page_config(page_title="Zero Dark Claims – VA Letter Helper", layout="centered")

# ---- Header with logo ----
header_cols = st.columns([1, 3])
with header_cols[0]:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    except Exception:
        st.write("")  # no logo found, skip

with header_cols[1]:
    st.title("Zero Dark Claims")
    st.subheader("VA Claim Letter Helper")

st.markdown(
    """
This free tool helps you draft **VA-friendly letter content** to support your disability claim.
You can edit everything before you submit it to VA or bring it to your provider.
"""
)

st.markdown(
    """
<small><b>Important:</b> Zero Dark Claims is a private educational tool. We are not part of the Department of Veterans Affairs and are not VA‑accredited representatives. We do not file claims for you, do not give legal advice, and do not take any portion of your VA benefits.</small>
""",
    unsafe_allow_html=True,
)

with st.expander("How this tool is different from “claim sharks”"):
    st.markdown(
        """
- Filing a VA claim is free, and accredited VSOs can help at no cost.
- This is **self‑help software**. It helps you organize your story and draft letters.
- We **do not** charge any fee based on your rating, back pay, or the amount of your VA benefits.
- We **do not** represent you before VA or contact VA on your behalf.
- You stay in control: you decide what to claim, what to submit, and who represents you.
"""
    )

st.markdown("---")

# ---- Step 1: choose letter type ----
st.markdown("### Step 1 – Choose Letter Type")

col1, col2, col3 = st.columns(3)
letter_choice = None

with col1:
    if st.button("Personal Statement"):
        letter_choice = "personal"

with col2:
    if st.button("Medical Nexus Outline"):
        letter_choice = "nexus"

with col3:
    if st.button("Lay/Witness Statement\n(VA Form 21-10210 style)"):
        letter_choice = "lay"

st.markdown("---")

# If no button clicked yet, stop here
if letter_choice is None:
    st.info("Select a letter type above to continue.")
else:
    st.markdown("### Step 2 – Enter Your Information")

    # ---- Common veteran info ----
    st.header("Veteran Information")
    veteran_name = st.text_input("Veteran full name")
    va_ssn
