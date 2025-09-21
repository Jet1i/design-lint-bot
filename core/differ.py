# core/differ.py
import json
from typing import Dict, Any

from .parser_css import query_css
from .utils import normalize_color, to_px, font_contains

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _get_design_value(design_tokens: dict, token_path: str):
    """
    从设计 tokens（层级字典）里取值：
    token_path 形如 "typography.fontWeight"
    """
    cur = design_tokens.get("tokens", {})
    for p in token_path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

def _normalize_numeric_equiv(dval, cval) -> bool:
    """
    数值等价：把设计值当数字，代码值当 px 数字，允许 ±1px 容差。
    示例：600 vs "600"、14 vs "14px" 都算一致。
    """
    try:
        dnum = float(dval)
    except Exception:
        return False
    try:
        cnum = float(to_px(cval))
    except Exception:
        return False
    return abs(dnum - cnum) <= 1.0

def _equal(dval, cval, token_key: str) -> bool:
    """
    统一的等价判断：
    - 颜色：HEX/RGB/RGBA 归一比较
    - 字体家族：代码侧包含设计侧即可
    - 数值：数字 / "Npx" / "N" 容差 ±1px
    - 其它：字符串小写去空白比较
    """
    if dval is None or cval is None:
        return False

    # 颜色
    if isinstance(dval, str) and dval.strip().startswith("#"):
        return normalize_color(dval) == normalize_color(cval)

    # 字体
    if token_key.endswith("fontFamily"):
        return isinstance(cval, str) and font_contains(cval, str(dval))

    # 数值（fontWeight/size/lineHeight/letterSpacing/padding/borderRadius 等）
    if isinstance(dval, (int, float)) or (isinstance(dval, str) and dval.strip().replace(".", "", 1).isdigit()):
        return _normalize_numeric_equiv(dval, cval)

    # 其它统一为字符串比较
    return str(dval).strip().lower() == str(cval).strip().lower()

def compare(design_tokens: dict, css_index: dict, main_selector: str, mapping: dict) -> Dict[str, Any]:
    """
    - design_tokens: 设计侧 tokens（含 "tokens" 根节点）
    - css_index: 由 parser_css.build_css_index 构建的选择器→属性字典
    - main_selector: 主 CSS 选择器（如 ".btn-primary"）
    - mapping: 设计 token → 实现属性映射（例如 "color.hoverBackground": [".:hover.background-color"]）
    """
    diffs = []
    passed = failed = 0

    for token_path, css_paths in mapping.items():
        dval = _get_design_value(design_tokens, token_path)
        found = None
        matched = False

        for cp in css_paths:
            # 形如 ".:hover.background-color"
            if cp.startswith(".:"):
                try:
                    _, pseudo, prop = cp.split(".", 2)
                    selector = f"{main_selector}:{pseudo}"
                    found = query_css(css_index, selector, prop)
                except Exception:
                    found = None
            # 形如 ".btn-primary.border-color"（当前很少用）
            elif cp.startswith(".") and "." in cp[1:]:
                sel, prop = cp.rsplit(".", 1)
                found = query_css(css_index, sel, prop)
            else:
                # 普通属性，直接在主选择器上查
                found = query_css(css_index, main_selector, cp)

            if _equal(dval, found, token_path.split(".")[-1]):
                matched = True
                break

        diffs.append({
            "token": token_path,
            "design": dval,
            "code": found,
            "match": matched,
            "severity": None if matched else "error"
        })

        if matched:
            passed += 1
        else:
            failed += 1

    total = max(1, passed + failed)
    score = round(passed / total, 2)

    return {
        "summary": {"passed": passed, "failed": failed, "warnings": 0, "score": score},
        "diffs": diffs
    }
