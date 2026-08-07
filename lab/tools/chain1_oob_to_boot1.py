#!/usr/bin/env python3
"""
Chain 1 live: capture serial while user scans OOB crash QR → bootwait → boot1.
Then auto-send `audit` when boot1-like console appears.
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("pip install pyserial", file=sys.stderr)
    raise


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3] + "Z"


def open_port(port: str, baud: int) -> serial.Serial:
    s = serial.Serial(port, baud, timeout=0.15)
    s.dtr = True
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--port", default="COM18")
    ap.add_argument("-b", "--baud", type=int, default=1_000_000)
    ap.add_argument(
        "-o",
        "--out",
        default=str(
            Path(__file__).resolve().parents[1]
            / "captures"
            / f"chain1_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
        ),
    )
    ap.add_argument("--audit-delay", type=float, default=2.0, help="seconds after boot1 hint before audit")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    logf = open(out, "w", encoding="utf-8")

    def emit(line: str, also_print: bool = True) -> None:
        row = f"[{ts()}] {line}"
        logf.write(row + "\n")
        logf.flush()
        if also_print:
            print(row, flush=True)

    emit(f"=== Chain 1 start port={args.port} baud={args.baud} log={out} ===")
    emit("ACTION: On badge, middle-button scan: exploits-real/CVE-oob-short-15-aa.png")
    emit("Expect: vault panic / reboot / boot1 stay (bootwait=true)")

    ser: serial.Serial | None = None
    buf = b""
    boot1_hints = 0
    audit_sent = False
    last_open_try = 0.0
    saw_disconnect = False
    boot1_markers = (
        b"bootwait",
        b"Boot bypassed",
        b"Commands include",
        b"Command not recognized",
        b"BAOCHIP",
        b"audit",
        b"Semver",
        b"Board type",
        b"boot1",
        b"UF2",
        b">",  # weak
    )
    os_markers = (b"[console]", b"dc34_vault", b"dc34_console", b"xous")

    try:
        while True:
            now = time.time()
            if ser is None or not ser.is_open:
                if now - last_open_try < 0.5:
                    time.sleep(0.1)
                    continue
                last_open_try = now
                ports = [p.device for p in list_ports.comports()]
                # Prefer requested port; else any new USB serial
                candidates = [args.port] + [p for p in ports if p != args.port]
                opened = False
                for cand in candidates:
                    if cand not in ports and cand == args.port:
                        continue
                    try:
                        ser = open_port(cand if cand in ports else args.port, args.baud)
                        emit(f"OPEN {ser.port}  available={ports}")
                        # nudge OS console if still there
                        try:
                            ser.write(b"\r\n")
                        except Exception:
                            pass
                        opened = True
                        if saw_disconnect:
                            emit("RECONNECTED after disconnect — may be boot1")
                        break
                    except Exception as e:
                        ser = None
                        continue
                if not opened:
                    if not saw_disconnect:
                        emit(f"waiting for port… have {ports}", also_print=False)
                    time.sleep(0.3)
                    continue

            try:
                chunk = ser.read(4096)
            except Exception as e:
                emit(f"READ ERR / DISCONNECT: {e}")
                try:
                    ser.close()
                except Exception:
                    pass
                ser = None
                saw_disconnect = True
                buf = b""
                time.sleep(0.3)
                continue

            if not chunk:
                # periodic alive probe only while we think OS is up and no audit yet
                time.sleep(0.05)
                continue

            buf += chunk
            # boot1 may use \r only
            while b"\n" in buf or b"\r" in buf:
                if b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                else:
                    line, buf = buf.split(b"\r", 1)
                line = line.strip(b"\r")
                if not line:
                    continue
                try:
                    text = line.decode("utf-8", "replace")
                except Exception:
                    text = repr(line)
                emit(text)

                low = line.lower()
                if any(m.lower() in low for m in boot1_markers):
                    boot1_hints += 1
                if any(m in line for m in os_markers):
                    pass

                # Heuristic: after disconnect+reconnect, or strong boot1 text, fire audit
                if (
                    not audit_sent
                    and (boot1_hints >= 1 or saw_disconnect)
                    and (
                        b"Command not recognized" in line
                        or b"Commands include" in line
                        or b"Semver" in line
                        or b"Board type reads" in line
                        or (saw_disconnect and boot1_hints >= 1)
                    )
                ):
                    time.sleep(args.audit_delay)
                    emit(">>> SENDING: audit")
                    try:
                        ser.write(b"audit\r")
                        audit_sent = True
                    except Exception as e:
                        emit(f"audit send failed: {e}")

                # Also try after reconnect + idle: send help / audit once
                if saw_disconnect and not audit_sent and boot1_hints == 0:
                    # send a CR to see prompt, then audit after delay
                    pass

            # After reconnect, proactively poke boot1
            if saw_disconnect and not audit_sent and ser is not None:
                # every ~3s send audit until we get a response
                if int(now) % 3 == 0:
                    try:
                        ser.write(b"\raudit\r")
                        emit(">>> PROBE audit (post-disconnect)")
                        time.sleep(0.4)
                    except Exception as e:
                        emit(f"probe failed: {e}")
                        try:
                            ser.close()
                        except Exception:
                            pass
                        ser = None

    except KeyboardInterrupt:
        emit("=== stopped by user ===")
    finally:
        if ser:
            try:
                ser.close()
            except Exception:
                pass
        logf.close()
        print(f"\nLog saved: {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
