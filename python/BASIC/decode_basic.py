"""
BASIC Binary → ASCII Decoder
===========================
Convert tokenized MS‑DOS BASIC program files (GW‑BASIC, BASICA,
QuickBASIC, BASCOM) into a readable ASCII listing.

• **Prints to STDOUT** by default  (add `‑o FILE` to save a copy)
• **Follows the internal pointer chain** – the most reliable way to
  move from line to line across all dialects.
• **Skips header blocks** automatically (any record whose line number
  is 0).  QuickBASIC, for example, stores several admin blocks before
  the first real code line; we simply jump to `pointer` and continue.
• Unknown / un‑mapped tokens are shown as `<0xAB>` so you can spot where
  the table needs expanding.

Usage
-----
```bash
python decode_basic.py PROGRAM.BAS        # listing on console
python decode_basic.py PROGRAM.BAS -o out.txt
```

Author : Your Name
Updated : 2025‑04‑20
"""

from __future__ import annotations
import sys, argparse
from pathlib import Path
from typing import List, Dict

# ---------------------------------------------------------------------------
# TOKEN DICTIONARIES  – minimal but covers the vast majority of keywords.
# Expand as needed; unknown tokens fall back to <0xAB> notation.
# ---------------------------------------------------------------------------
ONE_BYTE: Dict[int, str] = {
    0x81:"END",0x82:"FOR",0x83:"NEXT",0x84:"DATA",0x85:"INPUT",0x86:"DIM",0x87:"READ",
    0x88:"LET",0x89:"GOTO",0x8A:"RUN",0x8B:"IF",0x8C:"RESTORE",0x8D:"GOSUB",0x8E:"RETURN",
    0x8F:"REM",0x90:"STOP",0x91:"PRINT",0x92:"CLEAR",0x93:"LIST",0x94:"NEW",0x95:"ON",
    0x96:"WAIT",0x97:"DEF",0x98:"POKE",0x99:"CONT",0x9A:"OUT",0x9B:"LPRINT",0x9C:"LLIST",
    0x9D:"WIDTH",0x9E:"ELSE",0x9F:"TRON",0xA0:"TROFF",0xA1:"SWAP",0xA2:"ERASE",0xA3:"EDIT",
    0xA4:"ERROR",0xA5:"RESUME",0xA6:"DELETE",0xA7:"AUTO",0xA8:"RENUM",0xA9:"DEFSTR",
    0xAA:"DEFINT",0xAB:"DEFSNG",0xAC:"DEFDBL",0xAD:"LINE",0xAE:"WHILE",0xAF:"WEND",
    0xB0:"CALL",0xB1:"WRITE",0xB2:"OPTION",0xB3:"RANDOMIZE",0xB4:"OPEN",0xB5:"CLOSE",
    0xB6:"LOAD",0xB7:"MERGE",0xB8:"SAVE",0xB9:"COLOR",0xBA:"CLS",0xBB:"MOTOR",
    0xBC:"BSAVE",0xBD:"BLOAD",0xBE:"SOUND",0xBF:"BEEP",0xC0:"PSET",0xC1:"PRESET",
    0xC2:"SCREEN",0xC3:"KEY",0xC4:"LOCATE",0xC5:"TO",0xC6:"THEN",0xC7:"TAB(",0xC8:"STEP",
    0xC9:"USR",0xCA:"FN",0xCB:"SPC(",0xCC:"NOT",0xCD:"ERL",0xCE:"ERR",0xCF:"STRING$",
    0xD0:"USING",0xD1:"INSTR",0xD2:"'",0xD3:"VARPTR",0xD4:"CSRLIN",0xD5:"POINT",
    0xD6:"LEFT$",0xD7:"RIGHT$",0xD8:"MID$",0xD9:"CHR$",0xDA:"SPACE$",0xDB:"HEX$",
    0xDC:"OCT$",0xDD:"LPOS",0xDE:"STR$",0xDF:"VAL",0xE0:"LEN",0xE1:"SIN",0xE2:"COS",
    0xE3:"TAN",0xE4:"ATN",0xE5:"PEEK",0xE6:"SQR",0xE7:"RND",0xE8:"LOG",0xE9:"EXP",
    0xEA:"ABS",0xEB:"INT",0xEC:"FRE",0xED:"INKEY$",
}

TWO_BYTE: Dict[int, str] = {
    0xFD81:"CVI",0xFD82:"CVS",0xFD83:"CVD",0xFD84:"MKI$",0xFD85:"MKS$",0xFD86:"MKD$",
    0xFF81:"LEFT$",0xFF82:"RIGHT$",0xFF83:"MID$",0xFF84:"SGN",0xFF85:"INT",0xFF86:"ABS",
    0xFF87:"SQR",0xFF88:"RND",0xFF89:"SIN",0xFF8A:"LOG",0xFF8B:"EXP",
}

# ---------------------------------------------------------------------------
# Decoder
# ---------------------------------------------------------------------------

def decode_listing(raw: bytes) -> List[str]:
    """Return a list of decoded BASIC lines."""
    n = len(raw)
    pos = 0
    listing: List[str] = []

    visited = set()  # guard against pointer loops

    while 0 <= pos < n and pos not in visited and pos + 4 <= n:
        visited.add(pos)
        ptr = int.from_bytes(raw[pos:pos+2], "little")
        line_num = int.from_bytes(raw[pos+2:pos+4], "little")
        pos += 4

        # header / admin block
        if line_num == 0:
            if 0 < ptr < n:
                pos = ptr
                continue
            break

        parts: List[str] = []
        while pos < n:
            b = raw[pos]; pos += 1
            if b == 0x00:
                break
            if b in (0xFD, 0xFE, 0xFF):
                if pos >= n:
                    parts.append(f"<0x{b:02X}>")
                    break
                second = raw[pos]; pos += 1
                parts.append(TWO_BYTE.get((b << 8) | second, f"<0x{b:02X}{second:02X}>") )
            elif b >= 0x81:
                parts.append(ONE_BYTE.get(b, f"<0x{b:02X}>") )
            elif 32 <= b <= 126:
                parts.append(chr(b))
            else:
                parts.append(f"<0x{b:02X}>")
        listing.append(f"{line_num} {' '.join(parts)}")

        # follow pointer to next record; if invalid, exit
        if 0 < ptr < n:
            pos = ptr
        else:
            break

    return listing

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="Decode tokenized BASIC files (GW‑BASIC / QuickBASIC) to ASCII listing.")
    p.add_argument("file", help="tokenized .BAS file")
    p.add_argument("-o", "--output", help="save listing to file")
    args = p.parse_args()

    src = Path(args.file)
    if not src.is_file():
        sys.exit(f"File not found: {src}")

    lines = decode_listing(src.read_bytes())
    text = "\n".join(lines) + "\n"
    print(text)

    if args.output:
        Path(args.output).write_text(text, encoding="utf‑8")
        print(f"[saved → {args.output}]")

if __name__ == "__main__":
    main()
