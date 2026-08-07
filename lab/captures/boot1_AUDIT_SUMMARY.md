# boot1 audit — live lab badge (2026-08-07)

Source: boot1 serial on COM17 after power-cycle/bootwait

| Field | Value |
|-------|-------|
| Board type | Oem |
| Boot partition | PrimaryPartition |
| boot1 semver | v0.10.1-0-gbcfdca404 |
| Description | Towards 0.10.1 beta-1 |
| Stepping | A0 |
| Device serializer | d8a9fbb0-1b8cf420-3f6250c8-f19ed54c |
| Public serial | CP4FCB |
| UUID | 18c26e7d-ebf4f0f3-1de80b4c-8ec4768c |
| Paranoid mode | 0/0 |
| Attack attempts | 0 |
| Dev key slots (boot0/1/next) | all **enabled** (not lockdown) |
| Boot0 key | 0/0 (bao1) |
| Boot1 key | 2/2 (beta) |
| Next stage key | 2/2 (beta) |
| Erase proof | uninit or access denied |
| In-system keys | generated |
| CM7 & debug | **fused off** |
| Collateral | **erased** |
| bootwait | Enable |
| ID mode | SerialNumber |

Full log: captures/boot1_audit_20260807T060131Z.log

Notes:
- Developer key slot still enabled → public dev.key images accepted (will wipe chip secrets).
- CM7/debug fused off → no JTAG freebie.
- Collateral erased → third-party mutual-distrust path already taken or OEM path active.
- No k0 / light key material in audit output (expected).
