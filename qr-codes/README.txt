DC34 badge scannable QR codes
Generated: 2026-08-06T21:30:19-05:00

How to scan: middle button = camera (mode matters — see notes)

=== 01-time-set-clock.png ===
time://2026-08-06T21:30:19-05:00

=== 02-pwauth-example-com.png ===
pwauth://pass/example.com?time=2026-08-06T21:30:19-05:00

=== 03-otpauth-defcon-demo.png ===
otpauth://totp/DEFCON:badge-demo@defcon.org?secret=JBSWY3DPEHPK3PXP&issuer=DEFCON&algorithm=SHA1&digits=6&period=30

=== 04-factory-standalone-test.png ===
factory://factory-aae949f6969-lorem-ipsum-data

Notes:
1) time:// and pwauth:// need vault/token modes that handle URI schemes.
2) otpauth:// enrolls TOTP secret JBSWY3DPEHPK3PXP (demo only — well-known test secret).
3) factory:// runs standalone button test UI — not for light genes.
4) Light-gene QRs must be live from another badge (encrypted, nonce-bound).
5) For real password use, install baochip QR browser extension and scan live pages.

