import re

def normalize_color(val: str) -> str:
    if not isinstance(val, str): return ""
    v = val.strip().lower()
    if v.startswith("rgba"):  # rgba(13,110,253,1)
        nums = [x.strip() for x in v[v.find("(")+1:v.find(")")].split(",")]
        r,g,b = map(int, nums[:3])
        return "#{:02x}{:02x}{:02x}".format(r,g,b)
    if v.startswith("rgb"):
        nums = [x.strip() for x in v[v.find("(")+1:v.find(")")].split(",")]
        r,g,b = map(int, nums[:3])
        return "#{:02x}{:02x}{:02x}".format(r,g,b)
    if v.startswith("#"):
        if len(v) == 4:  # #fff
            return "#" + v[1]*2 + v[2]*2 + v[3]*2
        return v
    return v

_px_re = re.compile(r"(-?\d+(\.\d+)?)px")
def to_px(val) -> float:
    if isinstance(val, (int, float)): return float(val)
    if not isinstance(val, str): return 0.0
    m = _px_re.search(val.strip().lower())
    return float(m.group(1)) if m else 0.0

def font_contains(code_family: str, design_family: str) -> bool:
    # 代码中包含设计字体即可
    return design_family.strip().lower() in [x.strip().strip("'\"").lower() for x in code_family.split(",")]

def split_padding(val: str):
    """
    将 '8px 12px' 拆为 top,right,bottom,left （px为float）
    规则：1值=上下左右；2值=上下/左右；3值=上/左右/下；4值=上右下左
    """
    if not isinstance(val, str): return 0,0,0,0
    parts = val.lower().replace(",", " ").split()
    px = [to_px(p) for p in parts]
    if len(px) == 1:
        t=r=b=l = px[0]
    elif len(px) == 2:
        t=b=px[0]; r=l=px[1]
    elif len(px) == 3:
        t=px[0]; r=l=px[1]; b=px[2]
    else:
        t,r,b,l = (px+[0,0,0,0])[:4]
    return t,r,b,l
