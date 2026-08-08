# Attack chains (lab-proven) + non-chains

**Unit class:** stock DEF CON 34 baosec / Baochip · 2026-08-07  
**Publish:** vulns and chains · **not** population secrets  

---

## Chain A — USB update-mode integrity / availability

```text
Attacker with USB (or one OS serial session)
        │
        ├─[VULN-15] stock OS: test bootwait enable
        │         └─ cold power cycle
        │
        └─[physical] button + reset / bootwait screen
                │
                ▼
        boot1 update mode (COM @ 1M, BAOCHIP MSC)
                │
        ┌───────┴───────────────────────────────┐
        ▼                                       ▼
  serial uf2 <b64>                      MSC copy *.uf2
  (VULN-10, no signature)               (VULN-10, no signature)
        │                                       │
        └───────────────┬───────────────────────┘
                        ▼
         rram.write_slice / SPI swap assembler
         (family 0xa7d76373, range check only)
                │
        ┌───────┼───────────────────────────────┐
        ▼       ▼                               ▼
  scribble   swap ps≠256                    plant beta-
  loader/    → VULN-12 hang                 signed implant
  kernel     (power-cycle OK)               (needs keys)
        │
        ▼
  try_boot still requires valid sig → no free AE
```

**Lab evidence:** UF2 matrix / residual peeks / factory restore cycles.

---

## Chain B — OS factory light-key overwrite

```text
USB serial on factory OS @ 1M
        │
        ▼
  test k0 <base64(key32 || crc32_le)>   (VULN-14)
        │
        ▼
  save_k0 → PDDB light key overwritten
  (no password, no hazardous-test flag)
```

**Impact:** mate/gene protocol identity compromise on **non-wiped** badges; **not** boot AE.  
**Does not read** the prior key.

---

## Chain C — Post-AE / post-wipe bootkit (lab)

```text
Any path that runs developer-signed baremetal/loader
  (or DEVELOPER_MODE already set)
        │
        ▼
  erase_secrets + sticky DEVELOPER_MODE   (INFO-16)
        │
        ▼
  baremetal RRAM write into boot1 region
        │
        ▼
  reboot → marker persists (lab: BM1P-style persist)
```

**Not production first foothold** — requires prior AE or already-dev unit.  
Factory UF2 restore does **not** restore wiped ROOT_SEED / population light material.

---

## Explicit non-chains (lab)

| Attempt | Result |
|---------|--------|
| QR OOB / TOTP (VULN-1,5–9) → boot | **No** |
| UF2 past STORAGE_END → keyband | **No stick** |
| UF2 write boot1 code (stock) | Rejected |
| Serial swap UF2 | Rejected (MSC only) |
| Factory reflash clears dev mode | **No** — OWC sticky |
| Incomplete SPI zeros → AE | Expected AEAD/sig fail (DoS) |
| Devkey custom FW → dump k0 then restore | **Impossible** — erase before app |
| BIO free physical memory read of k0 | **Closed** (BDMA filter empty; independent HW measure) |

---

## Production first-AE still required for

Full compromise of a **virgin** unit without signing keys:

1. Fault injection on `validate_image` / erase policy  
2. Residual SPI TOCTOU under loader (hardware; post-`bda6df7` rehash hardens classic race)  
3. New software bug yielding **exec or key read** (not write)  
4. Stolen beta/bao private keys  

See `05-unfinished-first-AE.md` and `FULL-EXPLOIT-PIPELINE.md`.
