# Coordinated disclosure email (ready to send)

**To:** dc34@baochip.com  
**Subject:** Coordinated disclosure — DEF CON 34 Baochip badge: local vulns + unfinished AE map (thehinac / dc34_badge)

Copy everything below the line into your mail client.

---

To: dc34@baochip.com  
Subject: Coordinated disclosure — DEF CON 34 Baochip badge: local vulns + unfinished AE map (thehinac)

Hello Baochip / DC34 badge team,

I’m writing to report a set of **local** vulnerabilities and attack-chain observations on the DEF CON 34 Baochip (baosec-lite) badge, researched on lab hardware during DC34 (2026-08-07–08). This is **notify + public technical writeup** for coordinated awareness; we are **not** publishing population light-key material or gene-oracle ciphertexts.

Public package (advisories, chains, open pipeline):  
https://github.com/thehinac/dc34_badge  
Index: https://github.com/thehinac/dc34_badge/blob/main/disclosure/FINDINGS-INDEX.md  
Advisories root: https://github.com/thehinac/dc34_badge/tree/main/disclosure  

Researcher: thehinac (GitHub: https://github.com/thehinac/dc34_badge)

---

## Summary of verified findings

### A. Boot1 update mode (USB MSC / serial uf2)

| ID | Issue | Impact |
|----|--------|--------|
| **VULN-10** | Unsigned UF2 accepted into RRAM loader/kernel window (and MSC SPI swap pages); signature only at try_boot | Integrity / DoS until reflash; plant signed implant only if keys held — **not** free unsigned AE |
| **VULN-11** | MSC vs serial STORAGE_END bound inconsistency | Defense-in-depth / consistency |
| **VULN-12** | MSC swap path requires payload_size == 256; other sizes panic → update-mode hang until power cycle | Availability (recoverable) |
| **VULN-13** | UF2 block_no / num_blocks not enforced | Multi-address programming |

Family ID used in checks is the public constant 0xa7d76373.  
Lab boot1: v0.10.1-0-gbcfdca404.  
Details: disclosure/01-UF2-unsigned-write-oracle.md, disclosure/02-MSC-swap-payload-panic.md

### B. Stock OS console (USB serial @ 1_000_000 baud)

| ID | Issue | Impact |
|----|--------|--------|
| **VULN-14** | `test k0 <base64>` remains on stock builds: unauthenticated **write** of 32-byte light key + CRC via save_k0 | Integrity of mating/gene keying; **write-only** (no dump) |
| **VULN-15** | `test bootwait enable` from any serial session forces next cold boot into update mode | Stages VULN-10 without physical PROG |

Read-only k0check is correctly gated (hazardous-test); write is not.  
Details: disclosure/03-stock-console-factory-surfaces.md

### C. Application / QR (previously published in same repo; included for completeness)

| ID | Issue |
|----|--------|
| **VULN-1** | Short Base45 QR → vault OOB panic DoS (hardware verified) |
| **VULN-5** | Full QR text + TOTP secrets logged to USB serial (hardware verified) |
| **VULN-6–9** | TOTP overwrite / field injection / UI DoS / weak digits validation |

---

## Attack chains (what composes, what does not)

Documented in disclosure/04-attack-chains.md:

- **Chain A:** bootwait (VULN-15) or physical → update mode → unsigned UF2 / swap panic (VULN-10/12) → DoS/integrity only; try_boot still requires valid signature.  
- **Chain B:** serial → test k0 write (VULN-14) → light key overwrite.  
- **Chain C:** after developer-signed path / erase_secrets → sticky DEVELOPER_MODE → post-wipe bootkit-style RRAM persist (lab). **Not** a virgin first foothold.

**Falsified / closed:** QR → boot compromise; UF2 past STORAGE_END into keyband; software “any unsigned swap” on factory loader (lab loader UF2 is **post-bda6df7**); custom devkey FW as nondestructive k0 dump (erase_secrets before app by design).

---

## Unfinished: production first AE / population k0

We are **not** claiming production first arbitrary code execution on virgin silicon without signing keys or hardware attack.

Open map: disclosure/05-unfinished-first-AE.md, FULL-EXPLOIT-PIPELINE.md  

Still open classes:

1. Residual **SPI** physical TOCTOU / dual-image on external NOR (schematic U2 ZD25Q64BSIGT) under loader fresh-swap path — classic non-zero-key software skip fixed in bda6df7; load-time ed25519ph rehash hardens simple check-then-rewrite (disclosure/06-loader-swap-TOCTOU-status.md).  
2. Fault injection on validate_image / erase policy.  
3. New stock software **read** of in-RAM k0 / PDDB plaintext (none found in our review).  
4. Offline Ko recovery after public Kp day schedule (protocol design in defcon-scheme.md; we will not publish population samples or keys).

---

## Suggested fixes (short)

1. **UF2 (VULN-10/11/13):** require signature or device-bound MAC before programming; align MSC/serial ranges; enforce block counters; reject addr+len past STORAGE_END.  
2. **MSC swap (VULN-12):** no unwrap on payload length; require 256; recoverable error path.  
3. **Console (VULN-14/15):** gate `test k0` and `test bootwait` behind factory-only feature flags off in production; or require physical confirmation.  
4. **QR/serial (VULN-1/5–9):** bounds-check Base45 decode paths; remove secret material from Info logs; harden otpauth enrollment.  
5. **SPI residual:** keep first presentation of signed swap controlled; device-encrypt swap ASAP; continue dual-read/bollard work.

---

## Scope / ethics

- Research on lab / researcher-owned units; no intentional disruption of other attendees’ badges.  
- No population k0, Ko, or live gene-oracle ciphertext dumps in the public repo.  
- Happy to answer questions, share extra repro notes, or withhold further public detail on any item if you prefer a short embargo window for a patch release (latest.zip / CI).

Thank you for the open platform and the intentional red-team surface — the post-bda6df7 loader work and clear developer-mode wipe policy are appreciated.

Best regards,  
thehinac  
https://github.com/thehinac/dc34_badge  
https://github.com/thehinac/dc34_badge/tree/main/disclosure  

---

## After you send

- Optional: open a GitHub issue on this repo linking the email date (no secrets).  
- Optional: also CC Matrix/Discord maintainers only if they request formal mail.  
