#!/usr/bin/env python3
"""Watch DC34 badge USB serial for QR-related INFO log dumps (VULN-5)."""
from __future__ import annotations

import argparse
import re
import sys
import time

try:
    import serial
except ImportError:
    print("pip install pyserial", file=sys.stderr)
    raise

INTERESTING = re.compile(
    r"(got qr data:|mode:.*s:|Password:|b45dec:|Replacing individual|"
    r"SERIALDUMP|Authentication error|Invalid gene|Unhandled string|"
    r"Attempting gene|otpauth|pwauth)",
    re.I,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("port", nargs="?", default="COM18", help="serial port (default COM18)")
    ap.add_argument("-b", "--baud", type=int, default=1_000_000)
    ap.add_argument("-a", "--all", action="store_true", help="print every line, not only QR-related")
    args = ap.parse_args()

    print(f"Opening {args.port} @ {args.baud} … Ctrl+C to stop", flush=True)
    print("Scan a QR on the badge; watch for 'got qr data:' / 'Password:' lines.\n", flush=True)

    ser = serial.Serial(args.port, args.baud, timeout=0.2)
    buf = b""
    try:
        while True:
            chunk = ser.read(4096)
            if not chunk:
                time.sleep(0.05)
                continue
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                try:
                    text = line.decode("utf-8", "replace").rstrip("\r")
                except Exception:
                    text = repr(line)
                if args.all or INTERESTING.search(text):
                    print(text, flush=True)
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
    finally:
        ser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
