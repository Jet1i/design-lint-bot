import os, requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()  # 读取 .env

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)
CHECK_API = os.getenv("CHECK_API_URL", "http://localhost:8000/check")

@app.command("/component")
def handle_component(ack, respond, command):
    # 允许 "/component button main"：第一个词是组件名，第二个词是分支
    text = (command.get("text") or "").strip()
    parts = text.split()
    comp = parts[0] if parts else "button"
    branch = parts[1] if len(parts) > 1 else None

    ack(f"开始检查 `{comp}`（branch: {branch or 'default'}），请稍候…")

    try:
        payload = {"component": comp, "branch": branch, "source": "auto"}
        r = requests.post(CHECK_API, json=payload, timeout=60)
        r.raise_for_status()
        rep = r.json()

        s = rep.get("summary", {})
        artifacts = rep.get("artifacts", {}) or {}
        src = artifacts.get("source", "?")
        br  = artifacts.get("branch", branch) or "default"

        # Top 差异（最多 5 条）
        top_fail = [d for d in rep.get("diffs", []) if not d.get("match")][:5]
        if top_fail:
            diff_lines = "\n".join([
                f"- `{d['token']}` 设计:`{d.get('design')}` → 代码:`{d.get('code')}`"
                for d in top_fail
            ])
        else:
            diff_lines = "无差异 ✅"

        respond(blocks=[
            {
                "type":"section",
                "text":{"type":"mrkdwn",
                        "text": (
                            f"*{rep.get('component','?')}* 合规分：*{s.get('score','?')}*  "
                            f"✅{s.get('passed',0)} ❌{s.get('failed',0)}\n"
                            f"来源：*{src}*（branch: *{br}*）"
                        )}
            },
            {"type":"section","text":{"type":"mrkdwn","text": f"*Top 差异*\n{diff_lines}"}}
        ])

    except requests.HTTPError as e:
        try:
            err_json = e.response.json()
        except Exception:
            err_json = {"error": e.response.text if e.response else str(e)}
        respond(f"检查失败（HTTP）：{err_json}")
    except Exception as e:
        respond(f"检查失败：{e}")

if __name__ == "__main__":
    # 用 Socket Mode（无需公网 URL）
    handler = SocketModeHandler(app, os.environ["SLACK_APP_LEVEL_TOKEN"])
    handler.start()
