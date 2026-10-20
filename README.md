# tracker-agent 📊

**Your job applications, tracked by an agent.** Reads recruiting emails from Gmail, classifies them (rejection / interview / OA / confirmation / outreach), stores everything in SQLite, and prints a one-line battle report.

[中文版](README_zh.md)

```
$ python main.py sync
Synced 23 emails, 5 new.

$ python main.py stats

战况: 已投 57 ｜ ❌ 拒 3 ｜ 🎯 面试 1 ｜ 📝 OA 2 ｜ ⏳ 等消息 51

$ python main.py digest

最近 5 封招聘邮件:
  ❌ [DRW] rejection    - Thank you for your interest...
  🎯 [Stripe] interview  - Next steps: technical phone screen
  📝 [Coinbase] oa       - Your online assessment is ready
  ✅ [Figma] confirmation - Application received
  📨 [Recruiter] outreach - Came across your profile...
```

## Why this exists

When you're firing off 10 applications a day, the inbox becomes the source of truth and the chaos at the same time. Rejections, interview invites, and online assessments all look alike at a glance. This tool turns that chaos into a single number you can check every morning: **how many in, how many out, how many moving forward.**

## How it works

```
Gmail API (read-only) ──▶ fetch.py ──▶ classify.py ──▶ store.py (SQLite) ──▶ report.py
                                          │
                              ┌───────────┴───────────┐
                              │  rule-based classifier │
                              │  rejection → oa →      │
                              │  interview →           │
                              │  confirmation →        │
                              │  outreach → other      │
                              └────────────────────────┘
```

1. **Fetch** — Gmail API with `gmail.readonly` scope. The search query in `config.yaml` targets ATS senders (Greenhouse, Lever, Ashby, Workday, …) plus interview/assessment keywords.
2. **Classify** — pure rules, no LLM. Recruiting emails are templates; keyword rules are more accurate than an LLM here, cost zero, never hallucinate, and a misfire is fixed by adding one keyword. Rules are checked in order because rejection emails love to mention "the interview process".
3. **Match** — each email is matched to a company: first against your company list in `config.yaml`, then the From display name, then the sender domain as fallback.
4. **Store** — SQLite, two tables (`companies`, `events`), deduplicated by Gmail message ID. Each company keeps the *strongest* status seen so far: `rejected > offer > interview > oa > applied > contacted`.

## Quickstart

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# put your OAuth credentials.json next to main.py (see SETUP.md)
python main.py sync
python main.py stats
```

Full 10-minute setup (Google Cloud clicks included): **[SETUP.md](SETUP.md)**.

## Commands

| Command | What it does |
|---|---|
| `python main.py sync` | Fetch new emails, classify, store |
| `python main.py digest [--limit N]` | Recent recruiting emails |
| `python main.py stats` | Battle report: applied / rejected / interviews / OAs / pending |
| `python main.py rejected` | Rejections only |

## Configuration

- `config.yaml → gmail.query` — the Gmail search. Missing a company? Extend the query.
- `config.yaml → companies` — your applied list, used for matching. One line per new application.
- `tracker/classify.py → RULES` — the keyword rules. A misclassified email is a one-line fix.

## Deliberately left out

- **No LLM classification.** See above: rules win for templated email.
- **No web UI.** CLI is enough; a daily digest via cron comes later.
- **Read-only.** It never writes, deletes, or labels anything in your mailbox.

## Roadmap

- [ ] Daily digest via cron + push notification
- [ ] Offer detection (offer letters have their own template flavor)
- [ ] Timeline view per company: applied → OA → interview → offer
