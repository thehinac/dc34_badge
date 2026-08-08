# dc34_badge

DEF CON 34 Baochip / baosec research by **thehinac**.

**Verified local vulnerabilities**, attack chains, and an honest map of the **unfinished** production-root pipeline.

> ### Status (2026-08-08)
>
> | Area | Result |
> |------|--------|
> | QR / TOTP app bugs | **Multiple verified** (VULN-1, 5–9) |
> | Boot1 unsigned UF2 + MSC DoS | **Verified** (VULN-10–13) |
> | Stock console `test k0` write + bootwait | **Verified** (VULN-14/15) |
> | Production first AE / population k0 dump | **Not claimed complete** |
>
> Full index: **[`disclosure/FINDINGS-INDEX.md`](disclosure/FINDINGS-INDEX.md)**  
> Advisories: **[`disclosure/`](disclosure/)**

Upstream / platform:

- [bunnie/dc34-vault](https://github.com/bunnie/dc34-vault) · [dc34-console](https://github.com/bunnie/dc34-console) · [dc34-api](https://github.com/bunnie/dc34-api)
- [betrusted-io/xous-core](https://github.com/betrusted-io/xous-core)
- [baochip/baochip-1x](https://github.com/baochip/baochip-1x) · [bunnie/dc34-core-hw](https://github.com/bunnie/dc34-core-hw)
- Badge help: https://defcon.org/34b/ · report: dc34@baochip.com

---

## Verified findings (quick table)

### Application / QR (camera + USB serial @ 1 Mbaud)

| ID | Finding | Status |
|----|---------|--------|
| **VULN-1** | Short Base45 QR → vault OOB panic DoS | **VERIFIED** |
| **VULN-5 L1/L2** | QR text + TOTP `secret:` on serial | **VERIFIED** |
| **VULN-6** | Unauthenticated TOTP overwrite via otpauth | **VERIFIED** |
| **VULN-7** | Newline/field injection into TOTP records | **VERIFIED** |
| **VULN-8** | Colon in secret breaks TOTP UI | **VERIFIED** |
| **VULN-9** | Weak digits / HOTP counter validation | **VERIFIED** |

Writeups: [`qr-codes/exploits-real/VERIFIED.md`](qr-codes/exploits-real/VERIFIED.md) · [`TOTP-VULNS-VERIFIED.md`](qr-codes/exploits-real/TOTP-VULNS-VERIFIED.md)

### Boot1 update mode (USB MSC / serial `uf2`)

| ID | Finding | Status |
|----|---------|--------|
| **VULN-10** | **Unsigned** UF2 programs RRAM (loader/kernel window) + MSC SPI swap pages; sig only at `try_boot` | **VERIFIED** |
| **VULN-11** | MSC vs serial `STORAGE_END` bound inconsistency | **VERIFIED** |
| **VULN-12** | MSC swap `payload_size ≠ 256` → panic hang (power-cycle recover) | **VERIFIED** |
| **VULN-13** | UF2 `block_no` / `num_blocks` not enforced | **VERIFIED** |

Advisories: [`disclosure/01-UF2-unsigned-write-oracle.md`](disclosure/01-UF2-unsigned-write-oracle.md) · [`02-MSC-swap-payload-panic.md`](disclosure/02-MSC-swap-payload-panic.md)

### Stock OS console

| ID | Finding | Status |
|----|---------|--------|
| **VULN-14** | `test k0 <base64>` — **unauthenticated write** of 32-byte light key + CRC | **VERIFIED** |
| **VULN-15** | `test bootwait enable` — next cold boot stuck in update mode (stages VULN-10) | **VERIFIED** |

Advisory: [`disclosure/03-stock-console-factory-surfaces.md`](disclosure/03-stock-console-factory-surfaces.md)

---

## Attack chains

Documented end-to-end in [`disclosure/04-attack-chains.md`](disclosure/04-attack-chains.md):

| Chain | Summary | Production AE? |
|-------|---------|----------------|
| **A** | bootwait or physical → update mode → unsigned UF2 / swap panic | **No** (DoS / integrity only) |
| **B** | serial → overwrite light key | **No** (write, not read) |
| **C** | after developer wipe → baremetal persist / bootkit pattern | **After secrets gone** |

**QR → boot compromise:** falsified.

---

## Unfinished: full production root

Honest status: [`disclosure/05-unfinished-first-AE.md`](disclosure/05-unfinished-first-AE.md) · [`FULL-EXPLOIT-PIPELINE.md`](FULL-EXPLOIT-PIPELINE.md)

Still open for virgin units without signing keys:

1. Fault injection on signature / erase policy  
2. Residual **SPI** physical TOCTOU on external NOR (`ZD25Q64` SOIC-8) under loader — classic software skip is **fixed** (`bda6df7`); load-time rehash hardens race ([`disclosure/06-loader-swap-TOCTOU-status.md`](disclosure/06-loader-swap-TOCTOU-status.md))  
3. New stock software **read** of `k0` / PDDB  
4. Offline `Ko` recovery after public `Kp` day drops (protocol design; samples not published)

**Developer-signed custom firmware cannot dump factory secrets** — `erase_secrets()` runs before app code.

---

## Layout

| Path | Contents |
|------|----------|
| `disclosure/` | **Boot/console advisories, chains, open pipeline** |
| `qr-codes/exploits-real/` | QR/TOTP PoCs, verified writeups |
| `lab/captures/` | Serial proofs (panic, TOTP demo secret, boot1 audit) |
| `lab/tools/` | Serial watchers, boot1 helpers |
| `CHIP-SURFACE-CHAINS.md` | Layer A/B/C trust model |
| `FULL-EXPLOIT-PIPELINE.md` | Completed vs open pipeline map |

---

## Reproduction notes

- Console and boot1 serial: **1_000_000** 8N1 (not 115200).  
- OS COM often needs **battery boot first**, then USBC.  
- Update mode: hold button + reset, or `test bootwait enable` + cold boot.  
- UF2 family ID (public): `0xa7d76373`.  
- Demo TOTP secret in captures is the well-known test vector `JBSWY3DPEHPK3PXP`.

### VULN-1 (quick)

1. Middle-scan `qr-codes/exploits-real/CVE-oob-short-15-aa.png`  
2. Vault panics; UI dies until reboot  

### VULN-5 L2 (quick)

1. `python lab/tools/serial_qr_watch.py COMx -a -o capture.log`  
2. Token mode → scan otpauth PoC → serial shows `secret:…`  

### VULN-10 (quick)

1. Update mode  
2. Serial `uf2 <b64>` or MSC copy into `0x60060000+`  
3. Write succeeds; boot still needs valid signature  

### VULN-14 (do not abuse)

```text
test k0 <base64(key32||crc32_le)>
```

Overwrites light key. **Never** on someone else’s badge.

---

## Ethics & non-disclosure of secrets

- Do **not** DoS or serial-sniff strangers’ badges without consent.  
- Do **not** publish or request population `k0` / `Ko` / live gene oracle dumps in issues.  
- This repo documents **bugs and methods**; it does **not** ship population key material.  
- Coordinated notes: prefer `dc34@baochip.com` for 0-days that still affect con attendees.

---

## License

Research artifacts for DEF CON educational / coordinated disclosure use. Upstream firmware remains under its own licenses.
