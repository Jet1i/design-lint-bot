from dotenv import load_dotenv
load_dotenv()  # ✅ 先加载 .env

from fastapi import FastAPI
from pydantic import BaseModel
import time, json, os

from core.parser_css import build_css_index
from core.parser_html import extract_class_selectors
from core.differ import load_json, compare
from integrations.github_client import get_component_files  # ✅ 现在再导入


app = FastAPI()

class CheckReq(BaseModel):
    component: str
    branch: str | None = None   # 可指定分支，不传就用 .env 的默认分支
    source: str = "auto"        # 预留：auto|github|local

@app.get("/health")
def health():
    return {"ok": True}

def _load_local_samples(comp: str) -> dict:
    base = os.path.join("samples", comp)
    css_path = os.path.join(base, f"{comp}.css")
    html_path = os.path.join(base, f"{comp}.html")
    css_text = open(css_path, "r", encoding="utf-8").read() if os.path.exists(css_path) else ""
    html_text = open(html_path, "r", encoding="utf-8").read() if os.path.exists(html_path) else ""
    return {"css": css_text, "html": html_text, "js": ""}

@app.post("/check")
def check(req: CheckReq):
    raw = (req.component or "").strip()
    comp = raw.split()[0].split("/")[-1] or "button"
    mapping = load_json(os.path.join("configs", "mapping.json"))
    design_tokens = load_json(os.path.join("configs", "mock_figma_tokens", f"{comp}.json"))

    # 1) 读取实现代码：先 GitHub，失败回退本地
    files = {"css": "", "html": "", "js": ""}
    src = "local"
    try:
        files = get_component_files(comp, req.branch)  # src/components/<name>/<name>.(html|css|js)
        if files.get("css") or files.get("html"):
            src = "github"
        else:
            files = _load_local_samples(comp)
            src = "local"
    except Exception:
        files = _load_local_samples(comp)
        src = "local"

    # 2) 解析
    css_index = build_css_index(files.get("css", ""))
    selectors = extract_class_selectors(files.get("html", ""))

    # 3) 决定主选择器：有就取第一个，没有就默认 .btn-primary
    main_selector = selectors[0] if selectors else ".btn-primary"

    # 4) 对比
    report = compare(design_tokens, css_index, main_selector, mapping)
    report["component"] = req.component
    report["artifacts"] = {
        "source": src,
        "branch": req.branch or "",
        "mainSelector": main_selector
    }
    report["generatedAt"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # 5) 存档
    os.makedirs("storage/artifacts", exist_ok=True)
    out_path = os.path.join("storage", "artifacts", f"{comp}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report
