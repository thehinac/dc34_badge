# Disclosure package — DEF CON 34 Baochip / baosec

**Researcher:** thehinac · **Lab date:** 2026-08-07 … 2026-08-08  
**Policy:** publish **vulnerabilities, reproduction, and unfinished attack chains**.  
**Do not publish:** population light key `k0` / `Ko`, live gene oracle ciphertexts, PDDB dumps, or per-badge secrets.

Contact for authors: [dc34@baochip.com](mailto:dc34@baochip.com) · https://defcon.org/34b/

## Documents

| File | Topic |
|------|--------|
| [01-UF2-unsigned-write-oracle.md](01-UF2-unsigned-write-oracle.md) | Boot1 update-mode unsigned RRAM/SPI write (**VULN-10**) |
| [02-MSC-swap-payload-panic.md](02-MSC-swap-payload-panic.md) | MSC swap `payload_size ≠ 256` hang (**VULN-12**) |
| [03-stock-console-factory-surfaces.md](03-stock-console-factory-surfaces.md) | `test k0` write, `test bootwait` (**VULN-14/15**) |
| [04-attack-chains.md](04-attack-chains.md) | Chains A–C lab-proven + non-chains |
| [05-unfinished-first-AE.md](05-unfinished-first-AE.md) | Full pipeline still open for production first AE |
| [06-loader-swap-TOCTOU-status.md](06-loader-swap-TOCTOU-status.md) | Pre/post `bda6df7`, residual SPI race research |
| [FINDINGS-INDEX.md](FINDINGS-INDEX.md) | Master ID table (QR + boot + console + open) |

## Related repo docs

| Path | Topic |
|------|--------|
| [`../README.md`](../README.md) | Overview |
| [`../CHIP-SURFACE-CHAINS.md`](../CHIP-SURFACE-CHAINS.md) | Layer A/B/C trust model |
| [`../FULL-EXPLOIT-PIPELINE.md`](../FULL-EXPLOIT-PIPELINE.md) | What must still break for production root |
| [`../qr-codes/exploits-real/VERIFIED.md`](../qr-codes/exploits-real/VERIFIED.md) | QR VULN-1 / VULN-5 proof |
| [`../qr-codes/exploits-real/TOTP-VULNS-VERIFIED.md`](../qr-codes/exploits-real/TOTP-VULNS-VERIFIED.md) | TOTP VULN-6–9 |

## Lab context (non-secret)

| Item | Value |
|------|--------|
| Boot1 (lab) | `v0.10.1-0-gbcfdca404` |
| Factory Xous (lab) | `v0.10.2-beta1-71-gf3e687b2b` |
| UF2 family ID | public `0xa7d76373` |
| USB OS | `1d50:6198` @ **1_000_000** baud |
| USB boot1 | `1d50:6196` |
| Factory loader swap fix | **post-**[`bda6df7`](https://github.com/betrusted-io/xous-core/commit/bda6df7a5befd605f4a1a431718127bfaebe24af) (AEAD string present) |
| SPI NOR (core module) | `ZD25Q64BSIGT` SOIC-8 (schematic U2) |

## Explicitly **not** claimed

- Remote root without USB/physical access  
- QR → boot compromise  
- UF2 write past storage into KEYROM/keyband (lab peeks negative)  
- Software-only skip of post-fix swap signature/AEAD  
- Working production first AE (SPI TOCTOU / FI / SW leak still open)  
- Population `k0` extraction

## Severity framing (suggested)

| ID | Class | Severity |
|----|-------|----------|
| VULN-1 | App DoS (camera QR) | Medium |
| VULN-5 | Confidentiality (serial logs) | High (local USB) |
| VULN-6–9 | TOTP integrity / DoS | Medium–High (local) |
| VULN-10 | Firmware integrity / availability (USB update) | Medium–High |
| VULN-12 | Update-mode DoS | Medium |
| VULN-14 | Light-key integrity (serial) | **High** if mating/keying still live |
| VULN-15 | Staging for VULN-10 | Medium |

## Ethics

- Do not DoS or serial-sniff strangers’ badges without consent.  
- Do not run `test k0` on someone else’s badge (overwrites shared light key material).  
- Developer-signed custom firmware **wipes** provisioned secrets — never a safe “dump then restore” path for population units.
