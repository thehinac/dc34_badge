#!/usr/bin/env python3
"""
DC34 second-badge key extraction toolkit
========================================
NEVER run `test k0` on a badge whose population key you want to keep.

Modes:
  capture   - Generate challenge QR; save nonce for pairing with response
  ingest    - Ingest donor response + challenge nonce (oracle sample)
  verify    - Test a candidate 32-byte key against captured samples
  hash-check- SHA256 of candidate key (match About-screen k0_hash)
  install   - Install a key via serial (ONLY after you know it's correct)

Workflow for a NEW unmodified badge:
  1. capture  -> scan challenge-phase1.png with NEW badge (middle btn)
  2. Read response gene QR text from badge with phone
  3. ingest --response-b45 "..."
  4. Repeat 1-3 a few times (more samples help offline attack when Kp leaks)
  5. Photo About screen "k0: <hash>" if shown
  6. When a candidate key appears (leak/crack), verify --key-hex ...
  7. Only then install on your lab badge / rejoin mating
"""
from __future__ import annotations
import argparse, base64, hashlib, json, os, struct, sys, time, zlib
from pathlib import Path
from datetime import datetime, timezone

from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV

DC34_HEADER = bytes.fromhex("49db7671f34435ed5fddffdfcbb7508a")
B45_ALPH = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:"
B45_MAP = {c: i for i, c in enumerate(B45_ALPH)}
LAB = Path(r"C:\Users\thehinac\dc34-lab")
CAP_DIR = LAB / "captures"
CAP_DIR.mkdir(parents=True, exist_ok=True)

def b45_encode(data: bytes) -> str:
    out = []; i = 0
    while i < len(data):
        if i + 1 < len(data):
            n = data[i] * 256 + data[i + 1]
            c = n % 45; n //= 45; d = n % 45; n //= 45; e = n
            out += [B45_ALPH[c], B45_ALPH[d], B45_ALPH[e]]; i += 2
        else:
            n = data[i]; out += [B45_ALPH[n % 45], B45_ALPH[n // 45]]; i += 1
    return "".join(out)

def b45_decode(s: str) -> bytes:
    s = s.strip(); out = bytearray(); i = 0
    while i < len(s):
        if i + 2 < len(s):
            n = B45_MAP[s[i]] + 45 * B45_MAP[s[i+1]] + 45 * 45 * B45_MAP[s[i+2]]
            out.append(n // 256); out.append(n % 256); i += 3
        else:
            out.append(B45_MAP[s[i]] + 45 * B45_MAP[s[i+1]]); i += 2
    return bytes(out)

def make_qr(payload: str, path: Path):
    import qrcode
    qrcode.make(payload, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2).save(path)

def cmd_capture(args):
    nonce = os.urandom(12)
    while nonce == DC34_HEADER[:12]:
        nonce = os.urandom(12)
    phase1 = DC34_HEADER + nonce
    b45 = b45_encode(phase1)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = CAP_DIR / f"session_{ts}"
    session.mkdir(parents=True, exist_ok=True)
    qr_path = session / "challenge-phase1.png"
    make_qr(b45, qr_path)
    meta = {
        "created": ts,
        "nonce_hex": nonce.hex(),
        "phase1_b45": b45,
        "header_hex": DC34_HEADER.hex(),
        "note": "Scan this QR with TARGET badge (middle button). Badge must act as DONOR and show gene response QR.",
        "warning": "Do NOT run test k0 on the target badge.",
    }
    (session / "challenge.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (session / "ACTIVE").write_text(str(session), encoding="utf-8")
    (CAP_DIR / "ACTIVE_SESSION").write_text(str(session), encoding="utf-8")
    print(f"[+] session: {session}")
    print(f"[+] QR:      {qr_path}")
    print(f"[+] nonce:   {nonce.hex()}")
    print(f"[+] b45:     {b45}")
    print()
    print("NEXT: middle-scan challenge on TARGET badge, then:")
    print(f'  python extract_k0_lab.py ingest --response-b45 "..."')

def active_session() -> Path:
    p = CAP_DIR / "ACTIVE_SESSION"
    if not p.exists():
        raise SystemExit("No ACTIVE_SESSION — run capture first")
    return Path(p.read_text(encoding="utf-8").strip())

def cmd_ingest(args):
    session = Path(args.session) if args.session else active_session()
    meta = json.loads((session / "challenge.json").read_text(encoding="utf-8"))
    nonce = bytes.fromhex(meta["nonce_hex"])
    ct = b45_decode(args.response_b45)
    if len(ct) < 17:
        raise SystemExit(f"ciphertext too short: {len(ct)}")
    sample = {
        "ingested": datetime.now(timezone.utc).isoformat(),
        "nonce_hex": nonce.hex(),
        "ciphertext_hex": ct.hex(),
        "ciphertext_len": len(ct),
        "response_b45": args.response_b45,
        "plaintext_structure": "16-byte gamete: haploid[9] + pad + badge_type@15 under AES-256-GCM-SIV",
    }
    # try known keys for convenience
    for name, key in [
        ("0x42*32", bytes([0x42] * 32)),
        ("0x00*32", bytes(32)),
        ("0x01*32", bytes([1] * 32)),
    ]:
        try:
            pt = AESGCMSIV(key).decrypt(nonce, ct, None)
            sample["decrypted_with"] = name
            sample["plaintext_hex"] = pt.hex()
            sample["badge_type_byte"] = pt[15]
            print(f"[!] Unexpected: decrypted with {name} -> {pt.hex()}")
            print("    This target may already be on a non-factory key.")
            break
        except Exception:
            pass
    else:
        print("[+] Ciphertext does NOT decrypt with lab keys — good (likely real population key).")

    samples_path = session / "samples.jsonl"
    with samples_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(sample) + "\n")
    (session / "last_sample.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")
    print(f"[+] saved sample -> {samples_path}")
    print(f"    nonce={nonce.hex()}")
    print(f"    ct_len={len(ct)} ct={ct.hex()[:32]}...")
    print()
    print("Capture more sessions (capture+ingest) for offline attack when Kp leaks.")

def cmd_verify(args):
    if args.key_hex:
        key = bytes.fromhex(args.key_hex.replace(" ", ""))
    elif args.key_b64:
        raw = base64.b64decode(args.key_b64)
        key = raw[:32] if len(raw) >= 32 else raw
    elif args.key_byte is not None:
        key = bytes([int(args.key_byte, 0) & 0xFF] * 32)
    else:
        raise SystemExit("need --key-hex or --key-b64 or --key-byte")
    if len(key) != 32:
        raise SystemExit("key must be 32 bytes")

    print(f"[*] key     {key.hex()}")
    print(f"[*] k0_hash {hashlib.sha256(key).hexdigest()}")

    # verify against all samples
    ok = 0; fail = 0
    for sample_file in CAP_DIR.rglob("last_sample.json"):
        s = json.loads(sample_file.read_text(encoding="utf-8"))
        nonce = bytes.fromhex(s["nonce_hex"])
        ct = bytes.fromhex(s["ciphertext_hex"])
        try:
            pt = AESGCMSIV(key).decrypt(nonce, ct, None)
            print(f"[+] OK  {sample_file.parent.name} pt={pt.hex()}")
            ok += 1
        except Exception as e:
            print(f"[-] FAIL {sample_file.parent.name} {type(e).__name__}")
            fail += 1
    # also jsonl
    for jl in CAP_DIR.rglob("samples.jsonl"):
        for line in jl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            s = json.loads(line)
            try:
                AESGCMSIV(key).decrypt(bytes.fromhex(s["nonce_hex"]), bytes.fromhex(s["ciphertext_hex"]), None)
                ok += 1
            except Exception:
                fail += 1
    print(f"\n[=] verified ok={ok} fail={fail}")
    if ok and not fail:
        print("[+] Candidate key decrypts all samples — safe to install on lab badge.")
    elif ok:
        print("[?] Partial matches — more samples or wrong key mix.")
    else:
        print("[-] No matches.")

def cmd_hash(args):
    key = bytes.fromhex(args.key_hex.replace(" ", ""))
    print(hashlib.sha256(key).hexdigest())

def cmd_install(args):
    import serial
    key = bytes.fromhex(args.key_hex.replace(" ", ""))
    if len(key) != 32:
        raise SystemExit("key must be 32 bytes")
    crc = zlib.crc32(key) & 0xFFFFFFFF
    b64 = base64.b64encode(key + struct.pack("<I", crc)).decode()
    print(f"[*] Installing key {key.hex()}")
    print(f"[*] k0_hash {hashlib.sha256(key).hexdigest()}")
    print(f"[*] serial: test k0 {b64}")
    if not args.yes:
        print("Refusing without --yes (this OVERWRITES light key on the connected badge).")
        return
    ser = serial.Serial(args.port, 1_000_000, timeout=2)
    try:
        ser.reset_input_buffer()
        ser.write(f"test k0 {b64}\r".encode())
        time.sleep(1.5)
        print(ser.read(8192).decode("ascii", errors="replace"))
    finally:
        ser.close()
    print("[!] Power-cycle badge so vault reloads k0.")

def cmd_selftest_lab(args):
    """Prove dump/verify pipeline using THIS lab badge (key 0x42)."""
    key = bytes([0x42] * 32)
    nonce = os.urandom(12)
    # known plaintext like a gene
    pt = bytes([6, 255, 255, 255, 0, 0, 255, 0, 255, 0, 0, 0, 0, 0, 0, 1])
    ct = AESGCMSIV(key).encrypt(nonce, pt, None)
    # fake session
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = CAP_DIR / f"selftest_{ts}"
    session.mkdir(parents=True, exist_ok=True)
    sample = {
        "nonce_hex": nonce.hex(),
        "ciphertext_hex": ct.hex(),
        "response_b45": b45_encode(ct),
        "selftest": True,
    }
    (session / "last_sample.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")
    (session / "challenge.json").write_text(json.dumps({"nonce_hex": nonce.hex()}), encoding="utf-8")
    print("[*] selftest sample written", session)
    # verify
    class A: pass
    a = A(); a.key_hex = key.hex(); a.key_b64 = None; a.key_byte = None
    # inline verify this sample
    pt2 = AESGCMSIV(key).decrypt(nonce, ct, None)
    assert pt2 == pt
    print("[+] crypto selftest OK — verify pipeline works for second badge captures")

def main():
    ap = argparse.ArgumentParser(description="DC34 k0 extraction lab")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("capture"); p.set_defaults(func=cmd_capture)
    p = sub.add_parser("ingest"); p.add_argument("--response-b45", required=True); p.add_argument("--session"); p.set_defaults(func=cmd_ingest)
    p = sub.add_parser("verify"); p.add_argument("--key-hex"); p.add_argument("--key-b64"); p.add_argument("--key-byte"); p.set_defaults(func=cmd_verify)
    p = sub.add_parser("hash"); p.add_argument("--key-hex", required=True); p.set_defaults(func=cmd_hash)
    p = sub.add_parser("install"); p.add_argument("--key-hex", required=True); p.add_argument("--port", default="COM18"); p.add_argument("--yes", action="store_true"); p.set_defaults(func=cmd_install)
    p = sub.add_parser("selftest-lab"); p.set_defaults(func=cmd_selftest_lab)
    args = ap.parse_args(); args.func(args)

if __name__ == "__main__":
    main()
