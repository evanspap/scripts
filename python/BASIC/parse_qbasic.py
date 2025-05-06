#!/usr/bin/env python3
"""
QuickBASIC / QBASIC binary-saved .BAS detokenizer
Rev7 - 20 Apr 2025

Usage:
    python parse_qbasic.py AERIO2.BAS > AERIO2_out.BAS

Compare AERIO2_out.BAS to AERIO2_R.BAS with `diff -u` for no differences.
"""
import struct, sys
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

# Single-byte tokens
TOKEN: Dict[int, str] = {
    0x81:"END",0x82:"FOR",0x83:"NEXT",0x84:"DATA",0x85:"INPUT",0x86:"DIM",
    0x87:"READ",0x88:"LET",0x89:"GOTO",0x8A:"RUN",0x8B:"IF",0x8C:"RESTORE",
    0x8D:"GOSUB",0x8E:"RETURN",0x8F:"REM",0x90:"STOP",0x91:"PRINT",
    0x92:"CLEAR",0x93:"LIST",0x94:"NEW",0x95:"ON", 0x96:"WAIT",
    0x97:"DEF",  0x98:"POKE", 0x99:"CONT",0x9A:"OUT", 0x9B:"LPRINT",
    0x9C:"LLIST",0x9D:"WIDTH",0x9E:"ELSE",0x9F:"TRON",0xA0:"TROFF",
    0xA1:"SWAP",0xA2:"ERASE",0xA3:"ERROR",0xA4:"RESUME",0xA5:"DELETE",
    0xA6:"AUTO",0xA7:"RENUM",0xA8:"DEFSTR",0xA9:"DEFINT",0xAA:"DEFSNG",
    0xAB:"DEFDBL",0xAC:"LINE",0xAD:"EDIT",0xAE:"OPTION",0xAF:"BASE",
    0xB0:"MID$",0xB1:"CLS",0xB2:"LOCATE",0xB3:"TO",0xB4:"THEN",
    0xB5:"TAB(",0xB6:"STEP",0xB7:"USING",0xB8:"VARPTR",0xB9:"USR",
    0xBA:"ERL",0xBB:"FN",0xBC:"SPC(",0xBD:"POINT",0xBE:"FRE",
    0xBF:"INKEY$",0xC0:"'",0xC3:"CSRLIN",0xC4:"POS",0xC5:"SYSTEM",
    0xC6:"LPRINT",0xC7:"WIDTH",0xCB:"VIEW",0xCC:"WINDOW",0xCE:"LINE",
    0xCF:"PSET",0xD0:"PRESET",0xD1:"SCREEN",0xD2:"KEY",0xD3:"LOCATE",
    0xD4:"TO",0xD5:"CIRCLE",0xD6:"COLOR",0xD7:"STRING$",0xD8:"PAINT",
    0xDB:"DEF SEG",0xDC:"BSAVE",0xDD:"BLOAD",0xDE:"SOUND",0xDF:"BEEP",
    0xE0:"PSET",0xE1:"DECLARE",0xE2:"CHAIN",0xE3:"FIELD",0xE4:"USING$",
    0xE5:"ERROR",0xE6:"RESUME",0xE7:"FILES",0xE8:"KILL",0xE9:"NAME",
    0xEA:"LSET",0xEB:"RSET",0xEC:"SAVE",0xED:"LFILES",0xEE:"PUT",
    0xEF:"GET",0xF0:"LOF",0xF1:"EOF",0xF2:"LOC",0xF3:"SEEK",
    0xF4:"OPEN",0xF5:"CLOSE",0xF6:"LOAD",0xF7:"MERGE",0xF8:"FILES",
    0xF9:"LSET",0xFA:"RSET",0xFB:"WIDTH",0xFC:"PLAY",0xFD:"TROFF"
}

# Extended two-byte tokens
EXT: Dict[Tuple[int,int], str] = {
    (0xFF,0x20):"INSTR$",(0xFF,0x60):"RND",
    (0xFF,0x6C):"TIMER",(0xFF,0x03):"MOD"
}

_EOL = 0x0D

class QBFile:
    """Detokenizer for QBASIC SAVE "prog",B files."""
    def __init__(self, data: bytes):
        self.data = data
        self.names = self._load_names()

    def lines(self) -> Iterator[str]:
        pos = 0
        while True:
            header = self._next_header(pos)
            if header is None:
                break
            seg = header
            while True:
                nxt = int.from_bytes(self.data[seg:seg+2],"little")
                # end of chain
                if nxt == 0 or not (seg < nxt < len(self.data)):
                    pos = seg + 2
                    break
                yield self._decode_line(seg+4, nxt)
                seg = nxt

    def _next_header(self, start: int) -> Optional[int]:
        for off in range(start, len(self.data)-4, 2):
            nxt = int.from_bytes(self.data[off:off+2],"little")
            if off < nxt < len(self.data) and _EOL in self.data[off+4:nxt]:
                return off
        return None

    def _decode_line(self, s: int, e: int) -> str:
        out = []  # type: List[str]
        i = s
        while i < e and self.data[i] != _EOL:
            b = self.data[i]
            # extended token
            if b in (0xFE,0xFF):
                out.append(EXT.get((b,self.data[i+1]),f"<EXT {self.data[i+1]:02X}>")+" ")
                i += 2; continue
            # name-table code
            if b < 0x20:
                out.append(self.names[b]+" "); i += 1; continue
            # single-byte token
            if b >= 0x81:
                out.append(TOKEN.get(b,f"<0x{b:02X}>")+" "); i += 1; continue
            # ASCII
            if b != 0:
                out.append(chr(b))
            i += 1
        return "".join(out).rstrip()

    def _load_names(self) -> List[str]:
        names: List[str] = [""]*0x20
        # find name table marker
        p = self.data.find(b"\x00\x02",0x0100)
        if p < 0: return names
        while p < len(self.data)-1:
            length = self.data[p+1]
            if length == 0: break
            name = self.data[p+2:p+2+length].decode("ascii","replace")
            names.append(name)
            p += 2 + length
            # skip padding
            while p < len(self.data) and self.data[p] == 0:
                p += 1
        return names

if __name__ == "__main__":
    if len(sys.argv)<2: sys.exit("Usage: parse_qbasic.py <binary.BAS>")
    raw = Path(sys.argv[1]).read_bytes()
    for line in QBFile(raw).lines(): print(line)
