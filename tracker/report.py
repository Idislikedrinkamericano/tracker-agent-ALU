"""CLI reports: stats + digest."""
from . import store

EMOJI = {
    "rejected": "\u274c", "offer": "\U0001f389", "interview": "\U0001f3af",
    "oa": "\U0001f4dd", "applied": "\u23f3", "contacted": "\U0001f4e8",
    "unknown": "\u2753",
}


def show_stats(conn):
    s = store.stats(conn)
    total = sum(s.values())
    print(f"\n\u6218\u51b5: \u5df2\u6295 {total}", end="")
    parts = []
    if s.get("rejected"):
        parts.append(f"\u274c \u62d2 {s['rejected']}")
    if s.get("offer"):
        parts.append(f"\U0001f389 offer {s['offer']}")
    if s.get("interview"):
        parts.append(f"\U0001f3af \u9762\u8bd5 {s['interview']}")
    if s.get("oa"):
        parts.append(f"\U0001f4dd OA {s['oa']}")
    pending = s.get("applied", 0) + s.get("contacted", 0) + s.get("unknown", 0)
    if pending:
        parts.append(f"\u23f3 \u7b49\u6d88\u606f {pending}")
    print(" \uff5c " + " \uff5c ".join(parts) if parts else "")


def show_digest(conn, limit=20):
    events = store.recent_events(conn, limit)
    if not events:
        print("No events yet. Run `python main.py sync` first.")
        return
    print(f"\n\u6700\u8fd1 {len(events)} \u5c01\u62db\u8058\u90ae\u4ef6:")
    for company, category, subject, date in events:
        e = EMOJI.get(store.CATEGORY_TO_STATUS.get(category, "unknown"), "")
        subj = (subject or "")[:60]
        print(f"  {e} [{company}] {category} - {subj}")


def show_rejected(conn):
    names = store.companies_by_status(conn, "rejected")
    if names:
        print("\n\u62d2\u4fe1:")
        for n in names:
            print(f"  \u274c {n}")
