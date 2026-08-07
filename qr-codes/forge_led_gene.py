#!/usr/bin/env python3
"""DC34 light-gene forger + key probe."""
from __future__ import annotations
import argparse, base64, struct, sys, zlib
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV

DC34_HEADER = bytes.fromhex("49db7671f34435ed5fddffdfcbb7508a")
B45_ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
B45_MAP = {c: i for i, c in enumerate(B45_ALPH)}

def b45_encode(data: bytes) -> str:
    out = []
    i = 0
    while i < len(data):
        if i + 1 < len(data):
            n = data[i] * 256 + data[i + 1]
            c = n % 45; n //= 45; d = n % 45; n //= 45; e = n
            out.extend([B45_ALPH[c], B45_ALPH[d], B45_ALPH[e]]); i += 2
        else:
            n = data[i]; c = n % 45; d = n // 45
            out.extend([B45_ALPH[c], B45_ALPH[d]]); i += 1
    return "".join(out)

def b45_decode(s: str) -> bytes:
    s = s.strip()
    out = bytearray(); i = 0
    while i < len(s):
        if i + 2 < len(s):
            c, d, e = B45_MAP[s[i]], B45_MAP[s[i+1]], B45_MAP[s[i+2]]
            n = c + 45*d + 45*45*e
            out.append(n // 256); out.append(n % 256); i += 3
        else:
            c, d = B45_MAP[s[i]], B45_MAP[s[i+1]]
            out.append(c + 45*d); i += 2
    return bytes(out)

PRESETS = {
    "red": dict(cd_period=2, cd_rate=200, cd_dir=255, sat=255, hue_ratedir=2, hue_base=0, hue_bound=20, chaser=255, nonlin=255, badge=6),
    "rainbow": dict(cd_period=6, cd_rate=255, cd_dir=255, sat=255, hue_ratedir=0, hue_base=0, hue_bound=255, chaser=0, nonlin=255, badge=1),
    "uber-red": dict(cd_period=1, cd_rate=128, cd_dir=40, sat=255, hue_ratedir=1, hue_base=220, hue_bound=255, chaser=20, nonlin=40, badge=0),
    "cyan": dict(cd_period=3, cd_rate=180, cd_dir=40, sat=200, hue_ratedir=3, hue_base=80, hue_bound=128, chaser=200, nonlin=128, badge=3),
    "magenta": dict(cd_period=0, cd_rate=0, cd_dir=0, sat=255, hue_ratedir=7, hue_base=200, hue_bound=210, chaser=255, nonlin=255, badge=5),
    # Full hue sweep, max rate, strong chaser (low chaser value), high nonlin — wild after phenotype blend
    "crazy": dict(cd_period=6, cd_rate=255, cd_dir=255, sat=255, hue_ratedir=0, hue_base=0, hue_bound=255, chaser=0, nonlin=255, badge=1),
    "hyper": dict(cd_period=1, cd_rate=255, cd_dir=255, sat=255, hue_ratedir=0, hue_base=0, hue_bound=255, chaser=1, nonlin=255, badge=0),
}

def pack_haploid(p: dict) -> bytes:
    h = bytes([p[k]&0xFF for k in ("cd_period","cd_rate","cd_dir","sat","hue_ratedir","hue_base","hue_bound","chaser","nonlin")])
    buf = bytearray(16); buf[:len(h)] = h; buf[15] = p.get("badge",7)&0xFF
    return bytes(buf)

def key_from_args(args) -> bytes:
    if getattr(args, "key_hex", None):
        return bytes.fromhex(args.key_hex.replace(" ",""))
    kb = int(args.key, 16) if str(args.key).startswith("0x") else int(args.key)
    return bytes([kb & 0xFF] * 32)

def make_qr(payload: str, path: Path):
    import qrcode
    img = qrcode.make(payload, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    img.save(path)

def cmd_install_key(args):
    import serial, time
    key = key_from_args(args)
    crc = zlib.crc32(key) & 0xFFFFFFFF
    b64 = base64.b64encode(key + struct.pack("<I", crc)).decode()
    print(f"[*] key={key.hex()} crc={crc:08x}")
    print(f"[*] test k0 {b64}")
    ser = serial.Serial(args.port, 1_000_000, timeout=2)
    try:
        ser.reset_input_buffer()
        ser.write(f"test k0 {b64}\r".encode())
        time.sleep(1.5)
        print(ser.read(4096).decode("ascii", errors="replace"))
    finally:
        ser.close()
    print("[!] Power-cycle required after changing key before vault uses it.")

def cmd_challenge(args):
    """Make a phase-1 QR so the BADGE encrypts a gene with ITS key. We know the nonce."""
    import os
    nonce = os.urandom(12)
    # avoid header collision like firmware does
    while nonce == DC34_HEADER[:12]:
        nonce = os.urandom(12)
    raw = DC34_HEADER + nonce
    payload = b45_encode(raw)
    out = Path(args.output)
    make_qr(payload, out)
    meta = Path(str(out) + ".nonce")
    meta.write_text(nonce.hex() + "\n" + payload + "\n", encoding="utf-8")
    print(f"[+] challenge QR: {out.resolve()}")
    print(f"[+] nonce hex:    {nonce.hex()}")
    print(f"[+] phase1 b45:   {payload}")
    print(f"[+] saved:        {meta}")
    print()
    print("ON BADGE: middle-button scan this QR (badge acts as DONOR).")
    print("Then read the RESPONSE gene QR text with your phone and run:")
    print(f'  python forge_led_gene.py probe-key --nonce-hex {nonce.hex()} --response-b45 "..."')

def cmd_probe_key(args):
    """Try decrypting a badge gene response under candidate keys."""
    ct = b45_decode(args.response_b45)
    nonce = bytes.fromhex(args.nonce_hex.replace(" ",""))
    print(f"[*] ct len={len(ct)} nonce={nonce.hex()}")
    candidates = []
    # known experiment key
    candidates.append(("0x42*32", bytes([0x42]*32)))
    candidates.append(("0x41*32", bytes([0x41]*32)))
    candidates.append(("0x00*32", bytes(32)))
    candidates.append(("0x01*32", bytes([1]*32)))
    if args.key_hex:
        candidates.insert(0, ("key-hex", bytes.fromhex(args.key_hex.replace(" ",""))))
    # try first bytes of sha256 of empty etc - skip
    for name, key in candidates:
        try:
            pt = AESGCMSIV(key).decrypt(nonce, ct, None)
            print(f"[+] DECRYPT OK with {name}: {pt.hex()}")
            print(f"    haploid={list(pt[:9])} badge={pt[15]}")
            return
        except Exception as e:
            print(f"[-] {name}: {type(e).__name__}")
    print("[!] No candidate worked. Badge is NOT using our installed k0, or response was mis-copied.")
    print("    Try install-key + power-cycle again, then challenge again.")

def cmd_decode_phase1(args):
    raw = b45_decode(args.b45) if args.b45 else bytes.fromhex(args.hex.replace(" ",""))
    print(f"raw ({len(raw)}): {raw.hex()}")
    print(f"header match: {raw[:16]==DC34_HEADER if len(raw)>=16 else False}")
    if len(raw) >= 28:
        print(f"nonce: {raw[16:28].hex()}")

def cmd_forge(args):
    key = key_from_args(args)
    if args.nonce_hex:
        nonce = bytes.fromhex(args.nonce_hex.replace(" ",""))
    else:
        raw = b45_decode(args.nonce_b45)
        if len(raw) < 28 or raw[:16] != DC34_HEADER:
            raise SystemExit(f"bad phase1: len={len(raw)} header_ok={raw[:16]==DC34_HEADER if len(raw)>=16 else False}")
        nonce = raw[16:28]
    params = PRESETS[args.preset].copy()
    for field in ("cd_period","cd_rate","cd_dir","sat","hue_ratedir","hue_base","hue_bound","chaser","nonlin","badge"):
        v = getattr(args, field, None)
        if v is not None: params[field] = v
    pt = pack_haploid(params)
    ct = AESGCMSIV(key).encrypt(nonce, pt, None)
    payload = b45_encode(ct)
    out = Path(args.output)
    make_qr(payload, out)
    print(f"[*] key={key.hex()[:16]}... nonce={nonce.hex()}")
    print(f"[*] plain={pt.hex()} ct_len={len(ct)}")
    print(f"[*] b45={payload}")
    print(f"[+] {out.resolve()}")

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("install-key"); p.add_argument("--port", default="COM18"); p.add_argument("--key", default="0x42"); p.add_argument("--key-hex"); p.set_defaults(func=cmd_install_key)
    p = sub.add_parser("challenge"); p.add_argument("-o","--output", default="challenge-phase1.png"); p.set_defaults(func=cmd_challenge)
    p = sub.add_parser("probe-key"); p.add_argument("--nonce-hex", required=True); p.add_argument("--response-b45", required=True); p.add_argument("--key-hex"); p.set_defaults(func=cmd_probe_key)
    p = sub.add_parser("decode-phase1"); p.add_argument("--b45"); p.add_argument("--hex"); p.set_defaults(func=cmd_decode_phase1)
    p = sub.add_parser("forge"); p.add_argument("--key", default="0x42"); p.add_argument("--key-hex"); p.add_argument("--nonce-hex"); p.add_argument("--nonce-b45"); p.add_argument("--preset", choices=sorted(PRESETS), default="rainbow"); p.add_argument("-o","--output", default="gene.png")
    for field in ("cd_period","cd_rate","cd_dir","sat","hue_ratedir","hue_base","hue_bound","chaser","nonlin","badge"):
        p.add_argument(f"--{field}", type=int, default=None)
    p.set_defaults(func=cmd_forge)

    args = ap.parse_args(); args.func(args)

if __name__ == "__main__":
    main()

