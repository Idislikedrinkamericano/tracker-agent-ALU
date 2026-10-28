"""Rule-based classifier for recruiting emails.

Order matters: rejection patterns are checked first because rejection
emails often mention "interview process". The interview rule only fires
on invitation signals (invite/schedule/pick-a-time) -- the bare word
"interview" also appears in confirmation emails ("our interview process")
and must not trigger on its own. All matching is case-insensitive
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
        "pursuing candidates", "more closely match",
        "proceeding with other candidates",
    ]),
    ("oa", [
        "assessment", "hackerrank", "codesignal", "codility", "take-home",
    ]),
    ("interview", [
        "invite you to interview", "invited to interview",
        "interview invitation", "schedule an interview",
        "schedule a phone", "schedule a call", "schedule some time",
        "phone screen", "technical screen", "introductory call",
        "onsite", "on-site", "final round", "calendly",
        "interview availability", "select a time", "pick a time",
        "choose a time",
    ]),
    ("confirmation", [
        "application received", "we have received your application",
        "thank you for applying", "thanks for applying",
        "thanks for your interest", "thank you for your interest",
        "your application has been submitted", "application has been received",
        "application confirmation",
        # Added 2026-10-27 after live misses: Uber's "Your recent job
        # application" and Rippling/Golden's "We've got your application"
        # were both labeled "other" although they are confirmations.
        # Rejection patterns still run first, so a rejection that quotes
        # these phrases is still caught above.
        "we've got your application", "got your application",
        "your recent job application",
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
    subj = subject.lower()
    for category, keywords in RULES:
        # OA signals must appear in the subject: a job-alert email whose
        # body happens to mention "assessment" is not an OA invite.
        pool = subj if category == "oa" else text
        for kw in keywords:
            if kw in pool:
                return category, kw
    return "other", ""


# Optional variant -> canonical name map. Edit here, not in config.yaml,
# so a newer config on another machine is never overwritten by this file.
# NOTE: Citadel and Citadel Securities are TWO companies sharing one
# recruiting system. Never map one to the other; longest-match-first
# below keeps their emails attributed separately.
ALIASES = {
    # "roblox hiring team": "Roblox",
    # "epic games": "Epic",
    # Added 2026-10-27: canonical labels for senders whose ATS domain
    # otherwise steals the label (Rippling -> Golden).
    "golden analytics": "Golden",
    "uber talent": "Uber",
}


def extract_company(from_header, subject, known_companies, ats_domains):
    """Best-effort company match. Returns a name or 'Unknown'."""
    hay = f"{from_header} {subject}".lower()
    alias_map = {k.lower(): v for k, v in ALIASES.items()}
    # Alias variants first, longest first: "roblox hiring team" beats "roblox".
    for variant in sorted(alias_map, key=len, reverse=True):
        if re.search(r"\b" + re.escape(variant) + r"\b", hay):
            return alias_map[variant]
    # Known companies, longest first: "Citadel Securities" must win over
    # "Citadel", or their joint-branded emails all land on Citadel.
    for name in sorted(known_companies, key=len, reverse=True):
        # Word-boundary match: plain substring makes "wing" hit "following"
        # and "arc" hit "research", stealing other companies' emails.
        if re.search(r"\b" + re.escape(name.lower()) + r"\b", hay):
            return alias_map.get(name.lower(), name)
    # Try the From display name, e.g. "Jane via Greenhouse" -> "Jane"
    m = re.match(r'"?([^"<@]+?)"?\s*(?:via|<|$)', from_header)
    if m:
        cand = m.group(1).strip()
        if cand and not any(d in cand.lower() for d in ats_domains):
            # strip trailing "via ..." leftovers
            cand = re.sub(r"\s+via\s+.*$", "", cand, flags=re.I).strip()
            if cand:
                return alias_map.get(cand.lower(), cand.title())
    # Fallback: sender domain's first label, e.g. stripe.com -> Stripe
    dm = re.search(r"@([\w.-]+)", from_header)
    if dm:
        domain = dm.group(1).lower()
        if not any(domain == d or domain.endswith("." + d) for d in ats_domains):
            label = domain.split(".")[0]
            return alias_map.get(label, label.title())
    return "Unknown"
