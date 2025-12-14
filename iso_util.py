
from pathlib import PurePosixPath

from pycdlib.pycdlib import PyCdlib
from pydantic import BaseModel, ConfigDict, Field


class iso_util(BaseModel, frozen=True):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    # constructor should receive ISO as bytes (positional allowed)
    iso_bytes: bytes
    iso: PyCdlib = Field(default_factory=PyCdlib, init=False)

    def model_post_init(self, __context: object = None) -> None:
        iso_bytes: bytes = context.get("iso_bytes")  # 型注釈だけ付ける
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False) as tf:
                tf.write(self.iso_bytes)
                tf.flush()
                self.iso.open(tf.name)
        except Exception as e:
            raise RuntimeError(f"Failed to open ISO from bytes: {e}")

    def close_iso(self) -> None:
        try:
            self.iso.close()
        except Exception:
            pass

    def find_iso(self, target_file: str, path_type: str = "iso_path") -> bool:
        """指定された `target_file` を ISO 内で検索し、見つかれば内容を表示する。"""
        if not self.iso:
            raise RuntimeError("ISO is not opened.")

        target_lower = target_file.lower()

        for parent_path, _, files in self.iso.walk(**{path_type: "/"}):
            for f in files:
                if f.lower() == target_lower:
                    full_path = str(PurePosixPath(parent_path) / f)
                    print(f"Found file: {target_file} at {parent_path}")

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
