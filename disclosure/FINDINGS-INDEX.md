# Findings index — all IDs

Last updated: 2026-08-08

## Application / QR (Layer C) — hardware verified

| ID | Title | Status | Writeup |
|----|-------|--------|---------|
| **VULN-1** | Short Base45 QR → vault OOB panic DoS | **VERIFIED** | `qr-codes/exploits-real/VERIFIED.md` |
| **VULN-5 L1** | Full QR text logged to USB serial | **VERIFIED** | same + `SERIAL-DUMP.md` |
| **VULN-5 L2** | TOTP `secret:` cleartext via `TotpRecord::try_from` on serial | **VERIFIED** | `TOTP-VULNS-VERIFIED.md` |
| **VULN-5 L3+** | pwauth / gene mate log paths | Source / partial | `DEEP-AUDIT.md` |
| **VULN-6** | Unauthenticated TOTP overwrite via otpauth QR | **VERIFIED** | `TOTP-VULNS-VERIFIED.md` |
| **VULN-7** | Newline/field injection into TOTP text records | **VERIFIED** | same |
| **VULN-8** | Colon in secret breaks TOTP UI (entry DoS) | **VERIFIED** | same |
| **VULN-9** | Weak digits / HOTP counter validation | **VERIFIED** | same |
| VULN-2/3 | unwrap panics on gene-less edges | Rare / needs k0 | campaign notes |
| VULN-4 | Nonce not cleared → same-session gene replay | Protocol | campaign notes |

## Boot1 / update mode (Layer B) — lab verified

| ID | Title | Status | Writeup |
|----|-------|--------|---------|
| **VULN-10** | Unsigned UF2 write oracle (RRAM + MSC SPI swap window) | **VERIFIED** | `01-UF2-unsigned-write-oracle.md` |
| **VULN-11** | MSC vs serial STORAGE_END bound inconsistency | **VERIFIED** (no extra overflow) | `01-…` § bounds |
| **VULN-12** | MSC swap `payload_size ≠ 256` panic hang | **VERIFIED** | `02-MSC-swap-payload-panic.md` |
| **VULN-13** | UF2 `block_no` / `num_blocks` not enforced | **VERIFIED** | `01-…` |
| INFO-boot1-audit | boot1 `audit` identity dump over serial | By design / useful recon | lab captures |

## Stock OS console (Layer C serial) — lab verified

| ID | Title | Status | Writeup |
|----|-------|--------|---------|
| **VULN-14** | `test k0 <b64>` unauthenticated light-key **write** | **VERIFIED** | `03-stock-console-factory-surfaces.md` |
| **VULN-15** | `test bootwait enable` forces update mode next cold boot | **VERIFIED** | same |
| INFO-jig | `test jig` / `test hw` factory surfaces | Low risk | same |

## Trust / post-AE (lab)

| ID | Title | Status | Writeup |
|----|-------|--------|---------|
| **INFO-16** | Sticky `DEVELOPER_MODE` after erase; factory UF2 does not restore secrets | **VERIFIED** | `04-attack-chains.md` Chain C |
| **INFO-17** | Post-wipe baremetal RRAM persist into boot1 region (bootkit pattern) | **VERIFIED** (after wipe only) | Chain C |
| **INFO-18** | Factory loader is **post-`bda6df7`** (easy non-zero-key skip-sig fixed) | **VERIFIED** (strings) | `06-loader-swap-TOCTOU-status.md` |

## Closed / falsified

| Claim | Result |
|-------|--------|
| QR panic → boot1 / SoC reset | **Falsified** |
| UF2 past STORAGE_END into keyband | **Not observed** |
| Software “any unsigned swap” on stock factory loader | **Closed** (post-fix) |
| BIO BDMA free read of k0/RRAM | **Closed** by independent measurement (empty filter) — see community notes |
| Devkey-signed dump without wipe | **Impossible by design** (`erase_secrets` before app) |

## Open research (unfinished full pipeline)

| ID | Goal | Status | Doc |
|----|------|--------|-----|
| **OPEN-1** | First production AE without signing keys | **OPEN** | `05-unfinished-first-AE.md`, `FULL-EXPLOIT-PIPELINE.md` |
| **OPEN-2** | Residual SPI check-vs-load race under load-time ed25519ph | Research | `06-…`, SPI plan |
| **OPEN-3** | Custom MSC host UF2 sector desync | Unproven | Lead 2 |
| **OPEN-4** | Offline `Ko` recovery after public `Kp` day schedule | Crypto (not a bug) | scheme + gene oracle |
| **OPEN-5** | Fault injection on `validate_image` / `erase_secrets` | Hardware | bounty-class |
| **OPEN-6** | Flag #1 / #2 RRAM slots without wipe | Hardware / survivor dump | design intent |

## Attack chains (composed)

| Chain | Composition | Production value |
|-------|-------------|------------------|
| **A** | VULN-15 or physical → update mode → VULN-10 / VULN-12 | Integrity / DoS, **no free AE** |
| **B** | USB serial → VULN-14 | Overwrite light key |
| **C** | First AE or already-dev → erase → bootkit | **After** secrets gone |
| **Full root** | Needs OPEN-1 (or keys / FI) | **Not completed** |
