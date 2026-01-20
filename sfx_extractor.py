import lhafile
import os
import re

def find_lzh_start(file_path):
    # ファイルの末尾から有効なLZHヘッダーを探す
    # re を使ってパターンマッチングで探す
    # [ヘッダ長][02]["-lhX-"]
    with open(file_path, 'rb') as f:
        data = f.read()
    
    pattern = re.compile(rb'..-lh[0576d]-')
    # 後ろから探すため、finditer の結果を逆順に
    for match in reversed(list(pattern.finditer(data))):
        i = match.start()  # ヘッダー開始位置 (header_size)
        header_size = data[i]
        if header_size >= 24:  # reasonable header size (拡張ヘッダー対応で上限なし)
            return i  # ヘッダー開始位置
    return -1




def extract_lzh_from_sfx(sfx_path, output_dir):
    # LZHヘッダーの開始位置を探す
    lzh_start = find_lzh_start(sfx_path)
    if lzh_start == -1:
        raise ValueError("Valid LZH header not found in SFX file")

    # LZHデータを抽出
    with open(sfx_path, 'rb') as f:
        f.seek(lzh_start)
        lzh_data = f.read()

    # 一時ファイルとしてLZHデータを保存
    temp_lzh_path = os.path.join(output_dir, 'temp.lzh')
    with open(temp_lzh_path, 'wb') as temp_f:
        temp_f.write(lzh_data)

    # LZHファイルを解凍
    archive = lhafile.Lhafile(temp_lzh_path)
    for info in archive.infolist():
        data = archive.read(info.filename)
        with open(os.path.join(output_dir, info.filename), 'wb') as f:
            f.write(data)
    # archive を解放
    del archive

    # 一時ファイルを削除
    os.remove(temp_lzh_path)

# 使用例
if __name__ == "__main__":
    sfx_path = 'sfx.exe'  # SFXファイルのパス
    output_dir = 'extracted'  # 出力ディレクトリ
    os.makedirs(output_dir, exist_ok=True)
    extract_lzh_from_sfx(sfx_path, output_dir)