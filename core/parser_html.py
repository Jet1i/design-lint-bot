from bs4 import BeautifulSoup

def extract_class_selectors(html: str):
    soup = BeautifulSoup(html or "", "html.parser")
    classes = set()
    for el in soup.select("[class]"):
        for c in el["class"]:
            classes.add("." + c)
    return list(classes)
