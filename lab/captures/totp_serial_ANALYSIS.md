# TOTP serial dump live test — 2026-08-07

## Result: PARTIAL (L1 proved, L2 not exercised)

### Observed mode
Both scans: mode: GeneScan (badge was NOT in Totp/token list)

### Scan 1 — otpauth enroll PoC
got qr data: otpauth://totp/SERIAL:leak-demo@local?secret=JBSWY3DPEHPK3PXP&issuer=SERIAL&...
mode: GeneScan, s: otpauth://totp/SERIAL:leak-demo@local?secret=JBSWY3DPEHPK3PXP&...

PROOF L1: Full QR including TOTP secret appears on USB serial at Info.
NOTE: GeneScan does NOT run TotpRecord enroll (that is Password/Totp acquire_qr arm).
Secret still leaked via log of QR payload.

### Scan 2 — reload trigger
got qr data: SERIALDUMP://TOTP-RELOAD-TRIGGER-SCAN-IN-TOTP-MODE, mode: GeneScan
No TotpRecord::try_from / secret: line dumps (ReloadDb TOTP path not taken)

### L2 status
NOT confirmed live — requires VaultMode::Totp so post-scan ReloadDb deserializes TOTP dict with log::info!(desc_str).

### Retest procedure
1. Idle menu → Token mode (or switch to password/TOTP UI)
2. Navigate to TOTP list (mode Totp)
3. Scan otpauth enroll QR — should enroll without "Unhandled" gene modal
4. Stay on TOTP list, scan any second QR
5. Serial should show secret: lines from try_from for each stored TOTP

Log: totp_serial_dump_live.log
