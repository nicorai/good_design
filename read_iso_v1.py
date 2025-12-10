from iso_util_v1 import iso_util_v1

# ISOファイルと検索対象ファイル名を指定
ISO_PATH = "output.iso"
TARGET_FILE = "example.txt"  # 例: ISO内で探すファイル名
PATH_TYPE = "iso_path"      # "iso_path" または "rr_path"


def main() -> None:
    try:
        obj = iso_util_v1(iso_file_path=ISO_PATH, target_file=TARGET_FILE)
        print(f"ISOファイル '{ISO_PATH}' を開きました (pydantic v1)")
    except Exception as e:
        print(f"ISOファイルのオープンに失敗: {e}")
        raise SystemExit(1)

    found = obj.find_iso(PATH_TYPE)
    if not found:
        print(f"ファイル '{TARGET_FILE}' はISO内に見つかりませんでした")

    obj.close_iso()


if __name__ == "__main__":
    main()
