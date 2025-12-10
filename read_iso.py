from iso_util import iso_util

# ISOファイルと検索対象ファイル名を指定
ISO_PATH = "output.iso"
TARGET_FILE = "example.txt"  # 例: ISO内で探すファイル名
PATH_TYPE = "iso_path"      # "iso_path" または "rr_path"


def main() -> None:
    # ローカルの ISO をバイナリで読み込み、iso_bytes として util に渡す
    try:
        with open(ISO_PATH, "rb") as f:
            iso_bytes = f.read()
    except Exception as e:
        print(f"ISOファイルの読み込みに失敗: {e}")
        raise SystemExit(1)

    try:
        # コンストラクタでバイト列をキーワード引数として渡す
        obj = iso_util(iso_bytes=iso_bytes)
        print(f"ISOファイル '{ISO_PATH}' をバイト列として読み込み、util を生成しました")
    except Exception as e:
        print(f"ISO の初期化に失敗: {e}")
        raise SystemExit(1)

    found = obj.find_iso(TARGET_FILE, PATH_TYPE)
    if not found:
        print(f"ファイル '{TARGET_FILE}' はISO内に見つかりませんでした")
    else:
        print(f"ファイル '{TARGET_FILE}' の内容を表示しました")

    obj.close_iso()


if __name__ == "__main__":
    main()
