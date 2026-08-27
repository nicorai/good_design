import sys
import zipfile
from typing import List
import json
from lxml import etree
from dict_test import TagInfo

# Ensure stdout/stderr use UTF-8 and replace unencodable characters when writing
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    # Older Python or environments may not support reconfigure; ignore
    pass

# ドキュメントファイルのパスはコマンドライン引数で渡すかデフォルトを使用
if len(sys.argv) > 1:
    docx_path = sys.argv[1]
else:
    docx_path = "123.pptx"

# Office XMLの標準的な名前空間URI（フォールバック用）
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

try:
    with zipfile.ZipFile(docx_path, "r") as docx:
        # 圧縮内のすべての .xml ファイルを処理する
        xml_files = [name for name in docx.namelist() if name.lower().endswith(".xml")]
        if not xml_files:
            print("[Error] 圧縮ファイル内に .xml ファイルが見つかりません。")
            exit(1)

        # TagInfo を構築
        tag_info: TagInfo = {}
        tag_counter = 1

        for xml_name in xml_files:
            print(f"--- Processing: {xml_name} ---")
            try:
                with docx.open(xml_name) as xml_file:
                    # etree.parse でXMLを解析
                    tree = etree.parse(xml_file)
            except etree.XMLSyntaxError:
                print(f"[Warning] {xml_name} のXML解析に失敗しました。スキップします。")
                continue
            except Exception as e:
                print(f"[Warning] {xml_name} を開けませんでした: {e}")
                continue

            root = tree.getroot()

            # --- 名前空間の厳密なマッピング処理 (各XMLごとに初期化) ---
            ns = {}
            if root.nsmap:
                ns = {k: v for k, v in root.nsmap.items() if k is not None}
                if None in root.nsmap:
                    ns["w"] = root.nsmap[None]

            if "w" not in ns:
                ns["w"] = WORD_NS

            # すべてのテキストを持つ要素を取得（名前空間に依存しない）
            t_elements = [el for el in root.iter() if el.text and el.text.strip()]

            for t_element in t_elements:
                value = t_element.text if t_element.text is not None else ""

                # 近い祖先の w:r 要素を見つけ、その中のすべての w:rFonts を収集する
                r = t_element.getparent()
                while r is not None:
                    # QNameのlocalnameで 'r' を判定（名前空間を問わない）
                    q = etree.QName(r)
                    if q.localname == "r":
                        break
                    r = r.getparent()

                fonts: List[str] = []
                if r is not None:
                    # r 以下のすべての要素をチェックして、フォント属性を抽出する
                    for elem in r.iter():
                        for attr_name, attr_value in elem.attrib.items():
                            if not attr_value:
                                continue
                            # 属性名のローカル名を取り出す
                            try:
                                local = etree.QName(attr_name).localname
                            except Exception:
                                # attr_name が QName 形式でない場合は末尾を分解
                                local = attr_name.split("}")[-1]

                            # DrawingML や Word のフォント属性名を網羅
                            if local in (
                                "ascii",
                                "latin",
                                "eastAsia",
                                "ea",
                                "hAnsi",
                                "cs",
                            ):
                                if attr_value not in fonts:
                                    fonts.append(attr_value)

                # タグ名を要素のローカル名にする（重複時は連番を付与）
                qname = etree.QName(t_element)
                base_name = qname.localname if qname.localname else "tag"
                key = base_name
                if key in tag_info:
                    key = f"{base_name}_{tag_counter}"
                tag_counter += 1

                tag_info[key] = {"value": value, "font": fonts}

                # 結果を出力
                print(f"Tag: {key}")
                print(f"Value: {value}")
                print(f"rFonts: {fonts}")
                print("-" * 30)

        # DictTest を使って Pydantic モデルに詰める（検証のため）
        try:
            from dict_test import DictTest

            model = DictTest(tags=tag_info)
            print("\nPydantic model created successfully. Tags count:", len(model.tags))
            # tag_info を JSON に保存
            with open("tag_info.json", "w", encoding="utf-8") as f:
                json.dump(tag_info, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Warning] Pydantic model の作成に失敗しました: {e}")
            # それでも tag_info を保存
            try:
                with open("tag_info.json", "w", encoding="utf-8") as f:
                    json.dump(tag_info, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

except zipfile.BadZipFile:
    print("[Error] 指定されたファイルは有効なZip（Office）ファイルではありません。")
except etree.XMLSyntaxError:
    print("[Error] XMLの構文解析に失敗しました。データが破損している可能性があります。")
except Exception as e:
    print(f"[Error] 予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    pass
