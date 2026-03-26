from __future__ import annotations

from lief.ELF import Binary as ELFBinary

class ELF:
    Binary = ELFBinary

# Keep other symbols fallback to upstream stub
