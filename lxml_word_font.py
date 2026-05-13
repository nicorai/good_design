from zipfile import ZipFile
from lxml import etree

docx_path = "sample.docx"

# namespace
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def get_attr(elem, name):
    return elem.get(
        f"{{{NS['w']}}}{name}"
    )


with ZipFile(docx_path) as z:

    # -----------------------------
    # document.xml
    # -----------------------------
    document_xml = etree.fromstring(
        z.read("word/document.xml")
    )

    # -----------------------------
    # styles.xml
    #-----------------------------
    styles_xml = etree.fromstring(
        z.read("word/styles.xml")
    )

    # -----------------------------
    # theme1.xml
    # -----------------------------
    theme_xml = etree.fromstring(
        z.read("word/theme/theme1.xml")
    )


# =========================================================
# 1. 直接書式（document.xml）
# =========================================================

print("\n=== Direct Formatting ===")

runs = document_xml.xpath("//w:r", namespaces=NS)

# for i, r in enumerate(runs):

#     text = "".join(
#         r.xpath(".//w:t/text()", namespaces=NS)
#     )

#     rfonts = r.xpath(".//w:rFonts", namespaces=NS)

#     if not rfonts:
#         continue

#     rf = rfonts[0]

#     print({
#         "run_index": i,
#         "text": text,
#         "ascii": get_attr(rf, "ascii"),
#         "hAnsi": get_attr(rf, "hAnsi"),
#         "eastAsia": get_attr(rf, "eastAsia"),
#         "asciiTheme": get_attr(rf, "asciiTheme"),
#         "eastAsiaTheme": get_attr(rf, "eastAsiaTheme"),
#     })
#     for f in rfonts:
#     	print(f.attrib)
#     # for rtb in rf:
#     #   if rtb:
#     #     print(rtb.tag, rtb.attrib)


for i, r in enumerate(runs):

    text = "".join(
        r.xpath(".//w:t/text()", namespaces=NS)
    )

    rfonts = r.xpath(".//w:rFonts", namespaces=NS)

    if not rfonts:
        continue

    rf = rfonts[0]

    # 属性を全部取得
    attrs = {}

    for k, v in rf.attrib.items():

        # namespace除去
        name = k.split("}")[-1]

        attrs[name] = v

    print({
        "run_index": i,
        "text": text,
        "fonts": attrs,
    })



# =========================================================
# 2. 文字スタイル
# =========================================================

print("\n=== Character Styles ===")

char_styles = styles_xml.xpath(
    "//w:style[@w:type='character']",
    namespaces=NS
)

for s in char_styles:

    style_id = get_attr(s, "styleId")

    rfonts = s.xpath(".//w:rFonts", namespaces=NS)

    if not rfonts:
        continue

    rf = rfonts[0]

    print({
        "style_id": style_id,
        "ascii": get_attr(rf, "ascii"),
        "eastAsia": get_attr(rf, "eastAsia"),
    })


# =========================================================
# 3. 段落スタイル
# =========================================================

print("\n=== Paragraph Styles ===")

para_styles = styles_xml.xpath(
    "//w:style[@w:type='paragraph']",
    namespaces=NS
)

for s in para_styles:

    style_id = get_attr(s, "styleId")

    rfonts = s.xpath(".//w:rFonts", namespaces=NS)

    if not rfonts:
        continue

    rf = rfonts[0]

    print({
        "style_id": style_id,
        "ascii": get_attr(rf, "ascii"),
        "eastAsia": get_attr(rf, "eastAsia"),
    })


# =========================================================
# 4. basedOn（ベーススタイル）
# =========================================================

print("\n=== BasedOn Relationships ===")

styles = styles_xml.xpath(
    "//w:style",
    namespaces=NS
)

for s in styles:

    style_id = get_attr(s, "styleId")

    based_on = s.xpath(
        "./w:basedOn/@w:val",
        namespaces=NS
    )

    if based_on:
        print({
            "style": style_id,
            "based_on": based_on[0]
        })


# =========================================================
# 5. theme1.xml
# =========================================================

print("\n=== Theme Fonts ===")

latin = theme_xml.xpath(
    "//a:latin",
    namespaces=NS
)

ea = theme_xml.xpath(
    "//a:ea",
    namespaces=NS
)

for x in latin:
    print({
        "type": "latin",
        "font": x.get("typeface")
    })

for x in ea:
    print({
        "type": "eastAsia",
        "font": x.get("typeface")
    })