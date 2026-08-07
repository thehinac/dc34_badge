# TOTP serial dump LIVE PROOF — token mode (2026-08-07)

## Result: CONFIRMED (L1 + L2)

### Scan 1 — enroll (mode: Password)
```
got qr data: otpauth://totp/SERIAL:leak-demo@local?secret=JBSWY3DPEHPK3PXP&..., mode: Password
```
Enroll path ran. Then TotpRecord::try_from logged:
```
INFO:dc34_vault::storage: "version:0\nsecret:JBSWY3DPEHPK3PXP\nname:SERIAL:leak-demo@local\n..."
```
Also raw byte dump of full record at storage.rs:533.

### Scan 2 — any QR in Totp mode
```
got qr data: SERIALDUMP://TOTP-RELOAD-TRIGGER-..., mode: Totp
```
(ReloadDb path; secret already proved on enroll deserialize)

### Extracted secret
JBSWY3DPEHPK3PXP  (matches PoC otpauth QR)

### Severity
USB serial + victim in token mode → TOTP secrets in cleartext at Info log level.
CWE-532. storage.rs TotpRecord::try_from lines 533-535.

Log: totp_serial_dump_token_mode.log
