DC34 SAFE COOL QR PACK
======================
None of these overwrite k0 or brick a stock badge.

01-03  TEXT ON SCREEN (~3s)
       Idle/normal mode, middle button, scan.
       Shows: Unhandled QR code: msg://...

04     FACTORY STANDALONE TEST
       Interactive button checklist easter egg.
       Finish test -> back to normal. Safe toy.

05     OTP LABEL (token / password mode only)
       Enrolls a demo TOTP named DC34:PartyMode
       (well-known demo secret - not secure).

06     SET CLOCK
       Sets RTC (Vegas-ish noon sample). Harmless.

07     SOCIAL CRYPTO TRICK (best party trick)
       Middle-scan THIS on someone else's badge.
       Their badge thinks you requested a light mate
       and shows a big encrypted GENE QR.
       - Looks magical / technical
       - Does NOT steal their key
       - Does NOT change their lights (you never
         complete the mate by scanning their response
         into their device as recipient)
       Actually: when THEY scan your challenge, THEY
       become donor and DISPLAY the gene QR. Their
       lights unchanged until someone mates with them
       properly. Pure spectacle.

YOUR LAB BADGE ONLY (0x42 key) - separate folder:
  gene-crazy.png etc. - real light changes
  Do NOT use forge genes on friends' badges with
  your 0x42 key - auth error only, not brick, but
  useless.

HOSTILE (do not use on strangers):
  short Base45 crash QRs - panic/reboot
  test k0 - overwrites their light key
