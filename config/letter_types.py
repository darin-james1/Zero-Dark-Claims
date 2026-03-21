LETTER_TYPES = {
    "personal_statement": {
        "label": "Personal Statement (Lay Evidence)",
        "description": "Your own statement describing how your condition began, how it affects you now, and key in-service events.",
        "system_prompt": """You are assisting a veteran in drafting a clear, honest VA personal statement to support a disability claim.
Write in the veteran's voice, first person, plain language, roughly 8th-grade reading level, no legal jargon.
Follow VA-friendly structure: introduction (who I am, what I'm claiming), in-service events, symptom history and timeline, current impact on work and daily life, and a closing request for fair consideration.""",
        "sections": [
            "Claim overview and what you’re asking for",
            "How and when the condition started (in service or shortly after)",
            "Key in-service events/incidents related to the condition",
            "Symptom history over time (before, during, after service)",
            "Current daily impact (work, family, sleep, mobility, mental health)",
            "Treatments, medications, or accommodations",
            "Closing paragraph to the VA"
        ],
    },
    "buddy_letter": {
        "label": "Buddy Letter (Lay Statement from Others)",
        "description": "Statement from someone who knows you, describing what they observed about your condition.",
        "system_prompt": """You are assisting a lay witness (family member, friend, coworker, or supervisor) to write a VA buddy letter.
Write in the witness's voice, first person, clear and specific, focusing on what they personally observed.
Structure: who the witness is and how they know the veteran, what they observed during and after service, concrete examples of symptoms and functional impact, and a brief closing statement of support.""",
        "sections": [
            "Who you are and how you know the veteran",
            "How often you interact(ed) with the veteran and in what context",
            "What you observed during their service (if applicable)",
            "Changes you noticed after service",
            "Specific examples of current symptoms and limitations",
            "How the condition affects the veteran’s daily life",
            "Closing statement of support"
        ],
    },
    "nexus_letter": {
        "label": "Nexus Letter (Clinician Opinion)",
        "description": "Draft language for a medical provider explaining the link between service and a condition.",
        "system_prompt": """You are assisting a medical professional in drafting a VA nexus letter.
Use professional but plain language. Include: credentials, records reviewed, diagnosis, clear nexus opinion using VA terminology such as 'at least as likely as not (50% or greater probability)', and a medical rationale referencing history and evidence.
This draft is for the provider to review and modify on their letterhead.""",
        "sections": [
            "Provider introduction and credentials",
            "Veteran identification and purpose of the letter",
            "Summary of relevant medical and service history reviewed",
            "Current diagnosis(es)",
            "Nexus opinion using VA language (e.g., 'at least as likely as not')",
            "Detailed medical rationale explaining the connection",
            "Closing and signature block (for provider letterhead)"
        ],
    },
    "increase_statement": {
        "label": "Increase / Worsening Statement",
        "description": "Statement explaining how a service-connected condition has worsened and why an increased rating is warranted.",
        "system_prompt": """You are helping a veteran describe how an already service-connected condition has worsened over time.
Emphasize concrete before-and-after examples, new limitations, increased frequency or severity of symptoms, and recent medical evidence.""",
        "sections": [
            "Reference to existing service-connected condition and rating",
            "How symptoms used to be (baseline)",
            "How symptoms are now (frequency, duration, intensity)",
            "New limitations at work, at home, and socially",
            "Recent medical treatment and evidence of worsening",
            "Impact on daily activities and quality of life",
            "Closing request for an increased rating"
        ],
    },
    "secondary_condition": {
        "label": "Secondary Condition Statement",
        "description": "Statement describing a secondary condition caused or aggravated by a primary service-connected disability.",
        "system_prompt": """You are helping a veteran explain a secondary condition that is caused or aggravated by an existing service-connected disability.
Clarify the primary condition, the secondary condition, and the logical connection between them, using clear, everyday language.""",
        "sections": [
            "Primary service-connected condition (name and rating, if known)",
            "Secondary condition (diagnosis and main symptoms)",
            "When the secondary condition began",
            "How the secondary condition is caused or aggravated by the primary condition",
            "Examples of combined impact on daily life and work",
            "Treatment history for both conditions",
            "Closing statement tying everything together"
        ],
    },
}
