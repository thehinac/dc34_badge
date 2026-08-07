# DC34 badge — full attack campaign map (live + source)

**Device:** production OS console on COM18 @ 1M 8N1  
**Shell:** `echo, ver, test, image, bio` only  
**Date of probe:** during DEF CON 34 session  

---

## What we already own on THIS badge

| Capability | Status |
|------------|--------|
| Serial REPL | Yes |
| **Overwrite light key** `test k0` | **Yes — factory left open** |
| Forge gene QRs → change LEDs | **Yes** (key = `0x42*32` after our write) |
| Custom 128×128 image | Yes (`image` upload) |
| BIO SAO programs | Yes (`bio` upload; pins 21/22/30/31) |
| Crash via short Base45 QR | Yes (OOB panic; idle middle-scan enough) |
| Same-session gene QR replay | Yes (nonce not cleared post-decrypt) |
| QR extract k0 / RCE | **No** (source-audited) |
| Text injection modal | Yes (`msg://…` unhandled QR) |
| `test jig` | Yes → vault opcode 1025 |
| `test wfi` / `test deep` | Yes — **suspends** (USB drops) |
| `test bootwait enable` | Yes — can force bootloader wait |
| Dump original factory k0 | **No** (overwritten; no read cmd) |
| Change Attach: Human → Goon | **No** on stock |
| PDDB full dump | **No** public cmd |
| `test k0check` / transmute / hue | **Compiled out** |

---

## Production serial surface (confirmed live)

### Always available
- `echo`, `ver [xous]`
- `test proc | freemem | interrupts`
- `test bootwait [check|enable|disable]`
- `test time | temp | hw`
- `test k0 <b64>` — **write** PDDB light key (+ wipe badge type to None)
- `test jig` — factory jig mode IPC
- `test wfi` / `test deep` — power/suspend
- `image` / `image clear` — bitmap protocol
- `bio` / `bio clear|ready|reload|pin|clk|…` — BIO loader

### Source exists but NOT in your binary
- `k0check` (hazardous-test) — would log full key
- `transmute` / `bt` / `mate` / `hue` / `autogamy` (qa/misc)
- `reset` (misc) — would `delete_dict(dc34)` wipe all light game state

---

## Dump / extract paths — realistic ranking

### A. Light key (population k0) — original factory
| Method | Feasible now? |
|--------|----------------|
| Serial dump | **No** (no read) |
| QR dump | **No** |
| Encryption oracle (mate capture) | Theoretical; AES-256-GCM-SIV not practically breakable without reduced Ko / leak |
| Official leak / GPU crack | **Designed path** (README) |
| Second unmodified badge + somehow dump | Same problem on stock |
| HW debug / RRAM / glitch | Possible research; may wipe secrets if you go dev |

**Your badge:** original k0 is **gone** (we wrote `0x42…`). Restore = install population key when known.

### B. What’s still on device worth taking
| Asset | How |
|-------|-----|
| **Light genes** (phenotype) | Observable LEDs; gene blobs in PDDB `dc34/gene` — not exported |
| **Custom image** | Re-download not implemented; can overwrite |
| **TOTP / passwords** (if any stored in token mode) | Vendor HID CTAP backup commands exist in vault for TOTP/password — **not** k0 |
| **k0_hash** | About screen only (SHA-256) |
| **Process/RAM map** | `test proc` / `freemem` — addresses, not secrets |
| **HW telemetry** | `test hw` / `temp` |

### C. Escalate to dump (would need new bug)
Candidates from architecture (not proven on your unit):
1. Memory disclosure in IPC / PageBuf platform syscalls used by `test proc`
2. PDDB race / path traversal if any exists (none found in QR handlers)
3. Custom **dev-signed** firmware (public dev key in xous-core) → **wipes Baochip secrets**, may still read PDDB after
4. boot1 `audit` console (physical serial + bootwait) — device identity, not light k0

---

## High-value next moves (safe-ish → aggressive)

1. **Stay on `0x42` self-seeder** — full LED control via forge tool (already works).  
2. **Hunt population k0** on Discord/Matrix / end-of-con leak — then `test k0` real key + reboot.  
3. **Borrow unmodified badge** — only useful if extract method appears; don’t `test k0` it.  
4. **`test bootwait enable` + hold button reboot** — enter UF2/boot1 for reflash / audit (research).  
5. **Do NOT** casually `test deep` / `test wfi` if you need stable USB.  
6. **Do NOT** enable `test reset` even if a future build has it — wipes `dc34` dict.  
7. **Custom UF2** with `hazardous-test` — ultimate dump; **dev path wipes chip secrets**.

---

## Factory comment keys (NOT population key)

Source comments include sample provision blobs (valid CRC). Decoded:

```
24dd49a0b2d9770dae47914dc5c8bc57948729971a67f56ff13506682ba42151
478b8fadd3386652b182f429ade3ce42796ac6145284c0eef10942c304c3a9c1
```

These are **test vectors** for the factory tool, almost certainly **not** the con-wide key. Installing them would just change isolation key again.

---

## Bottom line

We **maxed the intentional + accidental surface** available without glitching or custom FW:

- **Best exploit:** open `test k0` → own light crypto → forge genes (done).  
- **No dump** of original factory k0 from this device after overwrite.  
- **No QR extract** of k0.  
- **Remaining hope for “real” mating:** published/leaked/cracked population key, or another unit + future extract bug.

Tools on disk: `C:\Users\thehinac\dc34-qr-codes\` (forge, text PoCs, writeups).
