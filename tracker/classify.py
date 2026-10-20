"""Rule-based classifier for recruiting emails.

Order matters: rejection patterns are checked first because rejection
emails often mention "interview process". All matching is case-insensitive
on subject + snippet.
"""
import re

# (category, [keywords/phrases])
RULES = [
    ("rejection", [
        "unfortunately", "not moving forward", "decided to move forward with other",
        "pursue other candidates", "not selected", "we regret to inform",
        "will not be moving", "no longer under consideration",
        "decided not to move forward",
    ]),
    ("oa", [
        "online assessment", "coding assessment", "hackerrank", "codesignal",
        "take-home assessment", "technical assessment", "codility",
    ]),
    ("interview", [
        "interview", "phone screen", "schedule a call", "next steps",
        "onsite", "on-site", "technical screen", "meet the team",
        "introductory call",
    ]),
    ("confirmation", [
        "application received", "we have received your application",
        "thank you for applying", "your application has been submitted",
        "application confirmation",
    ]),
    ("outreach", [
        "reaching out", "came across your profile", "impressed by your background",
        "would love to chat", "opportunity at",
    ]),
]

CATEGORIES = ["rejection", "oa", "interview", "confirmation", "outreach", "other"]

# company status derived from the strongest event seen
STATUS_PRECEDENCE = ["rejected", "offer", "interview", "oa", "applied", "contacted", "unknown"]
CATEGORY_TO_STATUS = {
    "rejection": "rejected",
    "interview": "interview",
    "oa": "oa",
    "confirmation": "applied",
    "outreach": "contacted",
    "other": "unknown",
    "offer": "offer",
}


def classify(subject, snippet):
    text = f"{subject} {snippet}".lower()
    for category, keywords in RULES:
        for kw in keywords:
            if kw in text:
                return category, kw
    return "other", ""


def extract_company(from_header, subject, known_companies, ats_domains):
    """Best-effort company match. Returns a name or 'Unknown'."""
    hay = f"{from_header} {subject}".lower()
    for name in known_companies:
        if name.lower() in hay:
            return name
    # Try the From display name, e.g. "Jane via Greenhouse" -> "Jane"
    m = re.match(r'"?([^"<@]+?)"?\s*(?:via|<|$)', from_header)
    if m:
        cand = m.group(1).strip()
        if cand and not any(d in cand.lower() for d in ats_domains):
            # strip trailing "via ..." leftovers
            cand = re.sub(r"\s+via\s+.*$", "", cand, flags=re.I).strip()
            if cand:
                return cand.title()
    # Fallback: sender domain's first label, e.g. stripe.com -> Stripe
    dm = re.search(r"@([\w.-]+)", from_header)
    if dm:
        domain = dm.group(1).lower()
        if not any(domain == d or domain.endswith("." + d) for d in ats_domains):
            return domain.split(".")[0].title()
    return "Unknown"
