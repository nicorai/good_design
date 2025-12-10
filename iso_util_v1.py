"""
Pydantic v1 互換の iso_util 実装

- `Config` クラスで `arbitrary_types_allowed = True` を設定
- `__init__` をオーバーライドして、初期化直後に `PyCdlib` インスタンスを作成・ISO を open する

このファイルは pydantic v1 環境で動作することを意図しています。
"""

from pycdlib.pycdlib import PyCdlib
from pydantic import BaseModel
from pathlib import PurePosixPath
from typing import Optional


class iso_util_v1(BaseModel):
    iso_file_path: str
    target_file: str
    iso: Optional[PyCdlib] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        # pydantic v1 の初期化を行う
        super().__init__(**data)

        # PyCdlib インスタンスを作成して ISO を開く
        self.iso = PyCdlib()
        try:
            self.iso.open(self.iso_file_path)
        except Exception as e:
            raise RuntimeError(f"Failed to open ISO '{self.iso_file_path}': {e}")

    def close_iso(self) -> None:
        try:
            if self.iso:
                self.iso.close()
        except Exception:
            pass

    def find_iso(self, path_type: str = "iso_path") -> bool:
        """
        クラスの `target_file` を ISO 内で検索し、見つかれば内容を表示する。
        """
        if not self.iso:
            raise RuntimeError("ISO is not opened.")

        target_lower = self.target_file.lower()

        for parent_path, _, files in self.iso.walk(**{path_type: "/"}):
            for f in files:
                if f.lower() == target_lower:
                    full_path = str(PurePosixPath(parent_path) / f)
                    print(f"Found file: {self.target_file} at {parent_path}")

                    try:
                        with self.iso.open_file_from_iso(**{path_type: full_path}) as fd:
                            content = fd.read()
                            print("----- File Content -----")
                            try:
                                print(content.decode("utf-8", errors="ignore"))
                            except Exception:
                                print(content)
                            print("-----------------------")
                        return True
                    except Exception as e:
                        print(f"Error opening file: {e}")

        return False
