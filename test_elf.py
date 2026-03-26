import pathlib

import lief
from lief.ELF import Binary as ELFBinary, parse
# Using filepath (ELF.parse returns ELFBinary | None)
elf_path = pathlib.Path("/bin/ls")
elf: ELFBinary | None = parse(elf_path)
if elf is None:
    raise FileNotFoundError(f"ELF file not found or invalid: {elf_path}")

# Using a Path from pathlib
elf_path = pathlib.Path(r"C:\Users\test.elf")
elf = parse(elf_path)
if elf is None:
    raise FileNotFoundError(f"ELF file not found or invalid: {elf_path}")

# Using an IO object
with open("/bin/ssh", "rb") as f:
    elf = parse(f)
if elf is None:
    raise FileNotFoundError("ELF data from open file is invalid")
