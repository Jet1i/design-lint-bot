import os, requests, base64

GH_TOKEN = os.getenv("GITHUB_TOKEN")
GH_REPO = os.getenv("GITHUB_REPO")  # e.g. "yourname/your-repo"
GH_BRANCH = os.getenv("GITHUB_DEFAULT_BRANCH", "main")

def _headers():
    if not GH_TOKEN:
        return {}
    return {"Authorization": f"token {GH_TOKEN}"}

def get_file_raw(path: str, ref: str = None) -> str:
    if ref is None:
        ref = GH_BRANCH
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{path}?ref={ref}"
    r = requests.get(url, headers=_headers(), timeout=20)

    # 👉 调试日志
    print(f"[GitHub] GET {url} -> {r.status_code}")

    if r.status_code == 200:
        data = r.json()
        return base64.b64decode(data["content"]).decode("utf-8")
    else:
        # 打印错误信息，便于排查
        try:
            print("Response:", r.json())
        except Exception:
            print("Response text:", r.text)
        return ""

def get_component_files(component: str, branch: str = None) -> dict:
    name = component.split("/")[-1]
    base = f"src/components/{name}"
    html = get_file_raw(f"{base}/{name}.html", ref=branch)
    css  = get_file_raw(f"{base}/{name}.css", ref=branch)
    js   = get_file_raw(f"{base}/{name}.js", ref=branch)
    return {"html": html, "css": css, "js": js}
