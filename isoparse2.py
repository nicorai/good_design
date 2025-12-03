from pathlib import PurePosixPath

from pycdlib.pycdlib import PyCdlib
from pycdlib.dr import DirectoryRecord


def print_file(iso: PyCdlib, dr: DirectoryRecord, path_type: str) -> None:
    """ディレクトリレコードからフルパスを取得して内容を表示"""
    full_path: str = iso.full_path_from_dirrecord(
        dr, rockridge=(path_type == "rr_path")
    )
    with iso.open_file_from_iso(**{path_type: full_path}) as fd:
        content = fd.read()
        print("----- File Content -----")
        print(content.decode("utf-8", errors="ignore"))
        print("-----------------------")


def find_iso(iso: PyCdlib, target_file: str, path_type: str) -> bool:
    """ISO 内を探索して target_file を見つけたら内容表示"""
    target_lower = target_file.lower()

    for parent_path, _, files in iso.walk(**{path_type: "/"}):
        # walk() で返されたファイル名リストから直接マッチさせる
        for f in files:
            if f.lower() == target_lower:
                # フルパスを構築して open_file_from_iso を使用
                full_path = str(PurePosixPath(parent_path) / f)
                print(f"Found file: {target_file} at {parent_path}")

                try:
                    with iso.open_file_from_iso(**{path_type: full_path}) as fd:
                        content = fd.read()
                        print("----- File Content -----")
                        print(content.decode("utf-8", errors="ignore"))
                        print("-----------------------")
                    return True
                except Exception as e:
                    print(f"Error opening file: {e}")

    return False


def find_and_print_file(iso_file_path: str, target_file: str) -> None:
    iso = PyCdlib()
    iso.open(iso_file_path)

    # 優先順位: Rock Ridge > Joliet > ISO 9660
    if iso.has_rock_ridge():
        path_type = "rr_path"
    elif iso.has_joliet():
        path_type = "joliet_path"
    else:
        path_type = "iso_path"

    print(f"Using path type: {path_type}")

    if not find_iso(iso, target_file, path_type):
        print(f"{target_file} not found in {iso_file_path}")

    iso.close()


if __name__ == "__main__":
    find_and_print_file("test.iso", "abcdefghij.txt")
