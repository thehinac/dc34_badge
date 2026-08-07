# dc34_badge

DEF CON 34 Baochip badge research notes, QR codes, forge tools, and real QR-parser exploit PoCs.

Research was done against live production hardware (serial console + camera QR scan) and open source:

- [bunnie/dc34-vault](https://github.com/bunnie/dc34-vault)
- [bunnie/dc34-api](https://github.com/bunnie/dc34-api)
- [bunnie/dc34-console](https://github.com/bunnie/dc34-console)

## Layout

| Path | Contents |
|------|----------|
| `qr-codes/exploits-real/` | **Real** QR vulns (DoS OOB, advisory, deep audit, PoC PNGs, builder script) |
| `qr-codes/vuln-pocs/` | Earlier crash / soft-fail / URI stress QRs |
| `qr-codes/cool-safe/` | Safe demos (text, factory test, social phase-1 helper) |
| `qr-codes/text-pocs/` | Text / scheme injection experiments |
| `qr-codes/forge_led_gene.py` | Forge AES-GCM-SIV light-gene QRs (needs `k0`) |
| `qr-codes/*.md` | Campaign map, k0/LED writeup, key proof notes |
| `lab/` | Restore notes, capture JSON, extract helper scripts |

## Real vulnerabilities (QR scan)

See **[`qr-codes/exploits-real/ADVISORY.md`](qr-codes/exploits-real/ADVISORY.md)** and **[`DEEP-AUDIT.md`](qr-codes/exploits-real/DEEP-AUDIT.md)**.

| ID | Summary | Stock badge? |
|----|---------|--------------|
| VULN-1 | Short Base45 → `data[..16]` panic DoS in `HandleQr` | **Yes** (idle middle scan) |
| VULN-2 | `get_padded_gamete().unwrap()` if no gene | Rare |
| VULN-3 | `get_egg().unwrap()` after decrypt w/ no gene | Needs `k0` |
| VULN-4 | Recipient nonce not cleared → same-session gene QR replay | Protocol |
| VULN-5 | QR / password content logged to USB serial (Info) | Needs serial cable |

**Not vulns:** `msg://`, `factory://`, `otpauth://`, `time://` (intentional features). No QR path to dump factory `k0` or RCE.

### Preferred crash PoC

`qr-codes/exploits-real/CVE-oob-short-15-aa.png` — Base45 decoding to 15 bytes → vault panic.

Regenerate PoCs:

```bash
python qr-codes/exploits-real/build_deep_pocs.py
```

## Light genes / LEDs

LED patterns come from **encrypted gene QRs** (AES-256-GCM-SIV, Base45), not a public color command.

```bash
python qr-codes/forge_led_gene.py --help
```

Lab note: serial `test k0 <b64+crc>` can **overwrite** the PDDB light key (factory surface left open). That is separate from QR bugs. Overwriting destroys the original population key on that unit.

## Ethics

- Do **not** show DoS crash QRs at strangers without consent.
- Do **not** `test k0` on someone else’s badge.
- Soft demos in `cool-safe/` are fine for party use.

## Upstream protocol

See vault `defcon-scheme.md` (clone `bunnie/dc34-vault`) for Ko/Kp mating design.

## License

Research artifacts for DEF CON educational use. Upstream badge firmware remains under its own licenses.
