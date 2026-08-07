#!/usr/bin/env python3
"""Parse a saved DC34 serial log for secrets, nonces, genes."""
from __future__ import annotations

import argparse
import re
import sys

ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
INV = {c: i for i, c in enumerate(ALPH)}
DC34_HEADER = bytes.fromhex("49db7671f34435ed5fddffdfcbb7508a")


def b45_decode(s: str) -> bytes | None:
    s = s.strip()
    if not s or any(c not in INV for c in s):
        return None
    try:
        out = bytearray()
        i = 0
        raw = s.encode("ascii")
        while i + 2 < len(raw):
            a, b, c = INV[chr(raw[i])], INV[chr(raw[i + 1])], INV[chr(raw[i + 2])]
            v = a + b * 45 + c * 45 * 45
            if v > 0xFFFF:
                return None
            out.append((v >> 8) & 0xFF)
            out.append(v & 0xFF)
            i += 3
        rem = raw[i:]
        if len(rem) == 2:
            out.append((INV[chr(rem[0])] + INV[chr(rem[1])] * 45) & 0xFF)
        elif len(rem) == 1:
            return None
        return bytes(out)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("logfile")
    args = ap.parse_args()
    text = open(args.logfile, encoding="utf-8", errors="replace").read()

    secrets = sorted(set(re.findall(r"secret:([A-Z2-7=]+)", text, re.I)))
    passwords = re.findall(r"Password:\s*(.+)", text)
    genes = re.findall(r"Replacing individual with (.+)", text)
    received = re.findall(r"Received gene (.+)", text)

    print("=== TOTP secrets ===")
    for s in secrets:
        print(s)
    print(f"({len(secrets)} unique)\n")

    print("=== Passwords from pwauth://new ===")
    for p in passwords:
        print(p)
    print()

    print("=== Phase-1 nonces (from Base45 QR payloads) ===")
    for m in re.finditer(r"got qr data: (.+?), mode:", text):
        raw = b45_decode(m.group(1))
        if raw and len(raw) >= 28 and raw[:16] == DC34_HEADER:
            print(raw[16:28].hex(), "from", m.group(1)[:40] + "…")
    print()

    print("=== Gene replace lines ===")
    for g in genes:
        print(g)
    print()
    print("=== Received gene lines ===")
    for g in received:
        print(g)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
