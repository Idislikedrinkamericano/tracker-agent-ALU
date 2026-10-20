# tracker-agent 安装（Mac，一次性 10 分钟）

## 1. 装依赖

```bash
cd tracker-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 开 Gmail API（Google 这步必须你亲手点）

1. 打开 https://console.cloud.google.com/，新建一个 Project（名字随便，如 `tracker-agent`）。
2. 左侧 **APIs & Services > Library**，搜 **Gmail API**，点 Enable。
3. **APIs & Services > OAuth consent screen**：选 External，填 App name 和你的邮箱，Developer contact 也填你的邮箱，一路 Save。
   - Scopes 页什么都不用加（代码里只申请 `gmail.readonly`）。
   - Test users：把你自己的 Gmail 加进去。
4. **APIs & Services > Credentials > Create Credentials > OAuth client ID**：
   Application type 选 **Desktop app**，下载 JSON。
5. 把下载的 JSON 重命名为 `credentials.json`，放到 `tracker-agent/` 目录下（和 `main.py` 同级）。

## 3. 第一次跑

```bash
python main.py sync
```

第一次会弹浏览器让你登录 Google 点同意（只读 Gmail），之后 token 存 `token.json` 自动刷新，不用再点。

## 4. 日常使用

```bash
python main.py sync     # 拉新邮件 + 分类入库
python main.py digest   # 看最近招聘邮件
python main.py stats    # 战况：已投 / 拒 / 面试 / OA / 等消息
python main.py rejected # 只看拒信
```

建议每天跑一次 `sync`，比如加到 cron。

## 5. 调参

- `config.yaml` 里的 `gmail.query` 是搜索条件，漏了哪家就加。
- `config.yaml` 里的 `companies` 是你投过的公司名单，匹配用。加新公司直接往里写。
- 分类规则在 `tracker/classify.py` 的 `RULES`，误判了就加关键词。
