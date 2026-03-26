from __future__ import annotations
from typing import IO, Optional, Union, overload
import io as _io
import os as _os

import lief

class ParserConfig:
    ...

class Binary(lief.Binary):
    @property
    def header(self) -> object: ...
    @property
    def sections(self) -> list[object]: ...
    @property
    def segments(self) -> list[object]: ...

@overload
def parse(obj: Union[str, _os.PathLike[str], bytes, bytearray, _io.IOBase, list[int]], config: ParserConfig = ...) -> Optional[Binary]: ...
