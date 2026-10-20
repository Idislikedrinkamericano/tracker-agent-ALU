"""tracker-agent CLI.

Usage:
  python main.py sync     # fetch Gmail + classify + store
  python main.py digest   # show recent recruiting emails
  python main.py stats    # show 战况 summary
  python main.py rejected # list rejections
"""
import argparse
import os
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(os.path.join(BASE_DIR, "config.yaml")) as f:
        return yaml.safe_load(f)


def cmd_sync(_args):
    from tracker import auth, fetch, classify, store
    cfg = load_config()
    service = auth.get_service(BASE_DIR)
    emails = fetch.fetch_emails(
        service,
        cfg["gmail"]["query"],
        cfg["gmail"]["days_back"],
    )
    conn = store.connect(BASE_DIR)
    store.seed_companies(conn, cfg.get("companies", []))
    known = cfg.get("companies", [])
    ats = cfg.get("ats_domains", [])
    new = 0
    for em in emails:
        cat, _kw = classify.classify(em["subject"], em["snippet"])
        company = classify.extract_company(em["from"], em["subject"], known, ats)
        if store.add_event(conn, em["gmail_id"], company, cat,
                           em["subject"], em["from"], em["date"], em["snippet"]):
            new += 1
    print(f"Synced {len(emails)} emails, {new} new.")
    conn.close()


def cmd_digest(args):
    from tracker import store
    conn = store.connect(BASE_DIR)
    store.show_digest(conn, args.limit)
    conn.close()


def cmd_stats(_args):
    from tracker import store
    conn = store.connect(BASE_DIR)
    store.show_stats(conn)
    conn.close()


def cmd_rejected(_args):
    from tracker import store
    conn = store.connect(BASE_DIR)
    store.show_rejected(conn)
    conn.close()


def main():
    ap = argparse.ArgumentParser(description="tracker-agent")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("sync")
    d = sub.add_parser("digest")
    d.add_argument("--limit", type=int, default=20)
    sub.add_parser("stats")
    sub.add_parser("rejected")
    args = ap.parse_args()
    {"sync": cmd_sync, "digest": cmd_digest,
     "stats": cmd_stats, "rejected": cmd_rejected}[args.cmd](args)


if __name__ == "__main__":
    main()
