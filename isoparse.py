import pycdlib

def open_and_print_file(iso: pycdlib.PyCdlib, dr, path_type: str):
    """ディレクトリレコードからフルパスを取得して内容を表示"""
    full_path = iso.full_path_from_dirrecord(dr, rockridge=(path_type == 'rr_path'))
    with iso.open_file_from_iso(**{path_type: full_path}) as fd:
        content = fd.read()
        print("----- File Content -----")
        print(content.decode('utf-8', errors='ignore'))
        print("-----------------------")

def find_file_in_iso(iso: pycdlib.PyCdlib, target_file: str, path_type: str):
    """ISO 内を探索して target_file を見つけたら内容表示"""
    target_upper = target_file.upper()

    for parent_path, _, files in iso.walk(**{path_type: '/'}):
        # ISO のファイル名を正規化して一致確認
        matched_files = [f for f in files if f.upper().rstrip(';1') == target_upper]
        if not matched_files:
            continue

        # 子レコードから正しい dirrecord を探す
        children = iso.list_children(**{path_type: parent_path})
        dr = next((d for d in children 
                   if d.file_identifier().decode('utf-8').rstrip(';1').upper() == target_upper), None)
        if dr:
            print(f"Found file: {matched_files[0]} at {parent_path}")
            open_and_print_file(iso, dr, path_type)
            return True

    return False

def find_and_print_file(iso_file_path: str, target_file: str):
    iso = pycdlib.PyCdlib()
    iso.open(iso_file_path)
    path_type = 'rr_path' if iso.has_rock_ridge() else 'iso_path'

    if not find_file_in_iso(iso, target_file, path_type):
        print(f"{target_file} not found in {iso_file_path}")

    iso.close()


if __name__ == "__main__":
    find_and_print_file("output.iso", "file2.txt")
