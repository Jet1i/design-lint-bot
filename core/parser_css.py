import cssutils
from .utils import split_padding

def build_css_index(css_text: str):
    """
    返回形如：
    {
      ".btn-primary": {"background-color":"#0D6EFD", ...},
      ".btn-primary:hover": {"background-color":"#0B5ED7"}
    }
    """
    index = {}
    sheet = cssutils.parseString(css_text or "")
    for rule in sheet:
        if rule.type != rule.STYLE_RULE:
            continue
        selectors = [s.selectorText.strip() for s in rule.selectorList]
        for selector in selectors:
            props = index.setdefault(selector, {})
            for decl in rule.style:
                props[decl.name.lower()] = decl.value
                # 在 for decl in rule.style: 循环结束后，增加：
                if "padding" in props and props.get("padding"):
                    t,r,b,l = split_padding(props["padding"])
                    # 只有当单边未显式设置时，用复合值回填
                    props.setdefault("padding-top", f"{t}px")
                    props.setdefault("padding-right", f"{r}px")
                    props.setdefault("padding-bottom", f"{b}px")
                    props.setdefault("padding-left", f"{l}px")

    return index

def query_css(index, selector, prop):
    return index.get(selector, {}).get(prop)
