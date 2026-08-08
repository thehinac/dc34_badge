# Unfinished pipeline — first production AE (OPEN-1)

This documents **what is still missing** for full production compromise.  
It is intentional red-team status, not a claim of a completed root.

## Goal

Run attacker-controlled code **while** `ROOT_SEED` / PDDB still decrypts (so light key `k0` and related secrets remain readable), **or** otherwise extract population `Ko` without wiping the unit.

## What we already have (insufficient alone)

| Primitive | Gives | Blocks |
|-----------|--------|--------|
| VULN-10 unsigned UF2 write | Corrupt stages / plant **signed** images | Exec still needs valid signature |
| VULN-14 `test k0` write | Overwrite light key | **No read** |
| VULN-15 bootwait | Enter update mode | Only stages A |
| Gene encryption oracle | Offline **verify** of key candidates | Needs `Kp` / brute for recovery |
| Devkey-signed images | Full AE **after wipe** | Secrets gone before dump |
| BIO code upload | Unsigned BIO cores | BDMA filter blocks secret windows |

## Architecture wall

```text
boot0 → boot1 (signed) → loader (signed) → xous + swap (signed / device-AEAD)
                │
                │  developer-signed next stage
                ▼
         erase_secrets()   ← ROOT_SEED / flags wiped
                │
                ▼
         attacker app runs  ← get_k0() fails; population gone
```

There is **no** “dump first, wipe second” window at application level under the public developer key.

## E1 targets still open

| ID | Target | Status |
|----|--------|--------|
| E1-SPI | Mid-boot / dual-image SPI on external NOR (`ZD25Q64`, swap region) under loader fresh path | Research; factory loader has load-time ed25519ph rehash post-`bda6df7` |
| E1-FI | Glitch `validate_image` or `erase_secrets` / bollards | Hardware bounty-class |
| E1-SW | Stock memory disclosure of `GlobalConfig.k0` or PDDB plaintext | None public; standing bounty |
| E1-MSC | Custom MSC host UF2 sector desync → surprise map | Unproven |
| E1-KEYS | Beta/bao private keys | Out of scope for public research |
| E1-BIO | BIO BDMA → SRAM/RRAM | Measured closed (empty whitelist) |

## Parallel non-AE path (design, not 0-day)

Light protocol: `K = Ko || Kp` (AES-256-GCM-SIV).  
`Kp` is meant to be publicly disclosed over conference days; `Ko` shrinks (scheme: 96→48 bit).  
Gene challenge/response is a **chosen-nonce MAC oracle** for offline search once `Kp` is known.  

We treat this as the **intended** non-destructive capture path for the shared light key, not a boot AE.

**We do not publish live population oracle samples or any recovered key material.**

## Definition of done (for us)

| Level | Meaning |
|-------|---------|
| Lab first AE | Controlled code under intact secrets on disposable unit |
| Population k0 | Offline crypto or non-wipe read validated against gene MAC |
| Full root | AE + persistence without relying on wiped-dev bootkit only |

**None of the production-root rows are claimed complete as of 2026-08-08.**

## Recommendations to platform

1. Treat residual SPI physical TOCTOU comments as still-relevant until device-bound AEAD is universal and first presentation is controlled.  
2. Keep shipping progressive `Kp` disclosure if the game design expects brute force.  
3. Close VULN-10/12/14/15 so “pre-AE” local compromise is less trivial.  
