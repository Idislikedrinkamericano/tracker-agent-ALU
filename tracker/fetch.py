"""Fetch recruiting emails from Gmail."""
import base64


def _headers(payload_headers):
    return {h["name"].lower(): h["value"] for h in payload_headers}


def _snippet_text(msg):
    return msg.get("snippet", "")


def fetch_emails(service, query, days_back, max_results=100):
    """Return list of dicts: gmail_id, from, subject, date, snippet."""
    q = f"{query} newer_than:{days_back}d"
    out = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=q, maxResults=min(50, max_results - len(out)),
                  pageToken=page_token)
            .execute()
        )
        ids = [m["id"] for m in resp.get("messages", [])]
        for mid in ids:
            m = (
                service.users()
                .messages()
                .get(userId="me", id=mid,
                     format="metadata",
                     metadataHeaders=["From", "Subject", "Date"])
                .execute()
            )
            h = _headers(m["payload"]["headers"])
            out.append({
                "gmail_id": mid,
                "from": h.get("from", ""),
                "subject": h.get("subject", ""),
                "date": h.get("date", ""),
                "snippet": _snippet_text(m),
            })
            if len(out) >= max_results:
                return out
        page_token = resp.get("nextPageToken")
        if not page_token:
            return out
