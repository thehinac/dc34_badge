# dc34_badge

DEF CON 34 Baochip badge research: **verified** QR parser bugs, serial secret leaks, PoCs, and lab captures.

> ## Verified on live hardware (2026-08-07)
>
> | ID | Finding | Status |
> |----|---------|--------|
> | **VULN-1** | Short Base45 QR → vault OOB panic DoS | **VALID / VERIFIED** |
> | **VULN-5 L1** | Full QR text logged to USB serial | **VALID / VERIFIED** |
> | **VULN-5 L2** | TOTP `secret:` cleartext via `TotpRecord::try_from` on serial | **VALID / VERIFIED** |
> | **VULN-6** | Unauthenticated TOTP overwrite via otpauth QR | **VALID / VERIFIED** |
> | **VULN-7** | Newline/field injection into TOTP text records | **VALID / VERIFIED** |
> | **VULN-8** | Colon in secret breaks TOTP UI (entry DoS) | **VALID / VERIFIED** |
> | **VULN-9** | Weak digits / HOTP counter validation | **VALID / VERIFIED** |
>
> Writeups: **[`VERIFIED.md`](qr-codes/exploits-real/VERIFIED.md)** · **[`TOTP-VULNS-VERIFIED.md`](qr-codes/exploits-real/TOTP-VULNS-VERIFIED.md)** · **[`ADVISORY.md`](qr-codes/exploits-real/ADVISORY.md)**

Research against production DC34 firmware (camera + USB serial @ 1M 8N1) and open source:

- [bunnie/dc34-vault](https://github.com/bunnie/dc34-vault)
- [bunnie/dc34-api](https://github.com/bunnie/dc34-api)
- [bunnie/dc34-console](https://github.com/bunnie/dc34-console)
- [betrusted-io/xous-core](https://github.com/betrusted-io/xous-core) (boot1 / devkey)

## Layout

| Path | Contents |
|------|----------|
| `qr-codes/exploits-real/VERIFIED.md` | **Hardware proof writeup** |
| `qr-codes/exploits-real/` | PoC PNGs, advisory, serial-dump docs, builders |
| `lab/captures/` | Raw serial logs (panic, TOTP secret, boot1 audit) |
| `lab/tools/` | `serial_qr_watch.py`, decode/capture helpers |
| `qr-codes/cool-safe/` | Safe party demos (not vulns) |
| `qr-codes/forge_led_gene.py` | Forge light genes (needs `k0`) |
| `CHIP-SURFACE-CHAINS.md` | boot1 / devkey / chain analysis |

## Verified reproduction

### VULN-1 — vault DoS
1. Middle-scan `qr-codes/exploits-real/CVE-oob-short-15-aa.png`
2. Vault panics (`main.rs:624`); lights/QR UI die until full reboot

### VULN-5 L2 — TOTP secret on serial
1. `python lab/tools/serial_qr_watch.py COM18 -a -o capture.log`
2. Badge → **Token mode** (not GeneScan lights)
3. Scan `CVE-serial-otpauth-enroll.png`
4. Serial contains `secret:JBSWY3DPEHPK3PXP` from `storage.rs` Info log

Proof logs (sanitized demo secret only):

- `lab/captures/chain1_live.log` — OOB panic
- `lab/captures/totp_serial_dump_token_mode.log` — TOTP secret leak
- `lab/captures/boot1_audit_20260807T060131Z.log` — boot1 identity

## Other findings (source / partial)

| ID | Summary | Stock? |
|----|---------|--------|
| VULN-2 / VULN-3 | unwrap panics on gene-less edges | Rare / needs k0 |
| VULN-4 | Nonce not cleared → same-session gene replay | Protocol |
| VULN-5 L3+ | pwauth password log, gene mate logs | Source |
| QR panic → boot1 | **Falsified** (process kill ≠ SoC reset) | — |

**Not vulns:** `msg://`, `factory://`, `time://` intentional features. No QR path to factory population `k0` or RCE.

## Ethics

- Do **not** DoS or serial-sniff strangers’ badges without consent.
- Do **not** `test k0` on someone else’s badge (overwrites light key).
- Demo TOTP secret is the well-known test vector `JBSWY3DPEHPK3PXP`.

## License

Research artifacts for DEF CON educational / coordinated disclosure use. Upstream firmware remains under its own licenses.
