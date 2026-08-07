#!/usr/bin/env python3
"""Capture serial through power-cycle into boot1; send audit when ready."""
from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import serial
from serial.tools import list_ports

PORT_PREF = "COM18"
BAUD = 1_000_000
OUT = Path(__file__).resolve().parents[1] / "captures" / (
    f"boot1_audit_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.log"
)


def ts() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S.%f")[:-3] + "Z"


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    logf = open(OUT, "w", encoding="utf-8")

    def emit(msg: str) -> None:
        line = f"[{ts()}] {msg}"
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    emit(f"=== boot1 audit capture log={OUT} ===")
    emit("ACTION: Power-cycle or reset the badge NOW (bootwait should stop in boot1).")
    emit("Hold nothing unless needed; wait for USB re-enumerate.")

    ser = None
    buf = b""
    audit_sent = False
    audit_rounds = 0
    saw_disconnect = False
    last_ports = set()
    last_probe = 0.0
    deadline = time.time() + 180  # 3 min

    try:
        while time.time() < deadline:
            ports = {p.device for p in list_ports.comports()}
            if ports != last_ports:
                emit(f"PORTS {sorted(ports)}")
                last_ports = ports

            if ser is None or not ser.is_open:
                for cand in [PORT_PREF] + sorted(ports - {PORT_PREF}):
                    if cand not in ports:
                        continue
                    try:
                        ser = serial.Serial(cand, BAUD, timeout=0.2)
                        ser.dtr = True
                        emit(f"OPEN {cand}")
                        if saw_disconnect:
                            emit("RECONNECT after disconnect — probing boot1")
                        break
                    except Exception as e:
                        ser = None
                if ser is None:
                    time.sleep(0.25)
                    continue

            try:
                chunk = ser.read(4096)
            except Exception as e:
                emit(f"DISCONNECT: {e}")
                try:
                    ser.close()
                except Exception:
                    pass
                ser = None
                saw_disconnect = True
                buf = b""
                audit_sent = False
                time.sleep(0.3)
                continue

            if chunk:
                buf += chunk
                while True:
                    # split on \n or \r
                    n_idx = buf.find(b"\n")
                    r_idx = buf.find(b"\r")
                    if n_idx < 0 and r_idx < 0:
                        break
                    if n_idx < 0:
                        idx = r_idx
                    elif r_idx < 0:
                        idx = n_idx
                    else:
                        idx = min(n_idx, r_idx)
                    line, buf = buf[:idx], buf[idx + 1 :]
                    line = line.strip(b"\r\n")
                    if not line:
                        continue
                    text = line.decode("utf-8", "replace")
                    emit(text)

            now = time.time()
            # After disconnect or periodically, try boot1 commands
            if (saw_disconnect or not audit_sent) and now - last_probe > 1.5:
                last_probe = now
                try:
                    if not audit_sent:
                        # wake + identify
                        ser.write(b"\r\n")
                        time.sleep(0.15)
                        ser.write(b"help\r")
                        time.sleep(0.3)
                        ser.write(b"audit\r")
                        audit_rounds += 1
                        emit(f">>> SENT help + audit (round {audit_rounds})")
                        if audit_rounds >= 2:
                            audit_sent = True
                            # follow-ups
                            time.sleep(0.5)
                            for cmd in (b"bootwait check\r", b"boardtype\r", b"idmode\r"):
                                ser.write(cmd)
                                time.sleep(0.25)
                                emit(f">>> SENT {cmd.decode().strip()}")
                except Exception as e:
                    emit(f"probe write failed: {e}")
                    try:
                        ser.close()
                    except Exception:
                        pass
                    ser = None
                    saw_disconnect = True

            # If still OS console, note it
            time.sleep(0.05)

        emit("=== timeout — stopping ===")
    except KeyboardInterrupt:
        emit("=== user stop ===")
    finally:
        if ser:
            try:
                ser.close()
            except Exception:
                pass
        logf.close()
        print(f"\nSaved: {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
