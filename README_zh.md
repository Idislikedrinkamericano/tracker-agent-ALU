# tracker-agent 📊

**求职申请邮件追踪器。** 自动读 Gmail 里的招聘邮件，分类成拒信 / 面试 / OA / 确认信 / 猎头私信，SQLite 存档，一行命令出战报。

[English](README.md)

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

## 为什么做这个

一天投 10 家的时候，邮箱既是唯一真相来源，也是一团乱麻。拒信、面试邀约、OA 长得都差不多。这个工具把乱麻变成每天早上能看的一行数字：**投了多少、拒了多少、几个在往前走。**

## 原理

```
Gmail API（只读）──▶ fetch.py ──▶ classify.py ──▶ store.py (SQLite) ──▶ report.py
                                        │
                            ┌───────────┴───────────┐
                            │      纯规则分类器      │
                            │  rejection → oa →     │
                            │  interview →          │
                            │  confirmation →       │
                            │  outreach → other     │
                            └───────────────────────┘
```

1. **拉取** — Gmail API，只申请 `gmail.readonly` 权限。`config.yaml` 里的搜索条件覆盖各大 ATS（Greenhouse、Lever、Ashby、Workday…）加上面试/OA 关键词。
2. **分类** — 纯规则，不用 LLM。招聘邮件全是模板，关键词规则比 LLM 准、零成本、不幻觉，误判了加一行关键词就行。顺序有讲究：rejection 先判，因为拒信里经常提到 "interview process"。
3. **匹配公司** — 先按 `config.yaml` 里的公司名单匹配，再看发件人显示名，最后 fallback 到发件域名。
4. **入库** — SQLite，两张表（`companies`、`events`），按 Gmail message ID 去重。每家公司保留见过最强的状态：`rejected > offer > interview > oa > applied > contacted`。

## 上手

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# 把 OAuth 的 credentials.json 放到 main.py 旁边（见 SETUP.md）
python main.py sync
python main.py stats
```

完整 10 分钟安装（含 Google Cloud 点哪里）：**[SETUP.md](SETUP.md)**。

## 命令

| 命令 | 干嘛 |
|---|---|
| `python main.py sync` | 拉新邮件、分类、入库 |
| `python main.py digest [--limit N]` | 最近招聘邮件列表 |
| `python main.py stats` | 战报：已投 / 拒 / 面试 / OA / 等消息 |
| `python main.py rejected` | 只看拒信 |

## 配置

- `config.yaml → gmail.query` — Gmail 搜索条件，漏了哪家就加。
- `config.yaml → companies` — 你投过的公司名单，匹配用。加一行就行。
- `tracker/classify.py → RULES` — 关键词规则，误判了加一行。

## 故意没做的

- **不用 LLM 分类** — 模板邮件上规则就是比 LLM 准，见上文。
- **没做 Web UI** — CLI 够用，以后加 cron 每日推送。
- **只读不写** — 不会动你邮箱里任何东西。

## Roadmap

- [ ] cron 每日战报推送
- [ ] offer 信识别（offer 也有固定模板味）
- [ ] 单公司时间线：applied → OA → interview → offer
