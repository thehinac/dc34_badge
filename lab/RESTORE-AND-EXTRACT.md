# FACTORY RESTORE (bootable FW — does NOT restore original k0)

Firmware files:
  C:\Users\thehinac\dc34-lab\factory-fw\extracted\
    loader.uf2
    xous.uf2
    swap.uf2

Bootloader helpers:
  C:\Users\thehinac\dc34-lab\bootloader\bao1x-boot1.uf2
  C:\Users\thehinac\dc34-lab\bootloader\bao1x-alt-boot1.uf2

## Restore app firmware (from https://defcon.org/34b/)
1. Hold any button + press reset (or power cycle while holding a button)
2. Screen: "Update mode"
3. USB mass storage appears
4. Copy loader.uf2, xous.uf2, swap.uf2 (NOT the zip) onto the drive
5. Press a button to commit (sync/eject first on Linux)
6. Device reboots to stock OS

NOTE: PDDB (including light k0) SURVIVES firmware update.
Your lab badge will still have k0=0x42 after restore unless re-provisioned.

## bootwait (already enabled on lab badge)
`test bootwait enable` was run — next cold boot may pause in bootloader for UF2/serial.
Disable later: `test bootwait disable`

## Second badge extraction (DO NOT OVERWRITE KEY)
cd C:\Users\thehinac\dc34-lab\tools
python extract_k0_lab.py capture
# middle-scan challenge-phase1.png on SECOND badge
# phone-read response gene QR text
python extract_k0_lab.py ingest --response-b45 "RESPONSE_TEXT"
# repeat 3-5 times
# when you have a candidate key:
python extract_k0_lab.py verify --key-hex <64 hex chars>
python extract_k0_lab.py install --key-hex <64 hex chars> --yes   # only on LAB badge
# power cycle lab badge → can mate with population again

## Why we can't dump k0 from stock OS
- No k0check in production
- Gene QR never contains the key
- Factory UF2 does not include PDDB secrets
- Best path: capture oracles now + leak/crack later, OR custom FW with hazardous-test (dev mode wipes chip secrets)
