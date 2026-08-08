# SPI TOCTOU lab plan — first production AE (lab badge only)

**Goal:** Prove (or disprove) a **lab** path to first arbitrary code exec via the loader **fresh-swap** SPI window, without wiping a virgin population `k0`.  
**Endgame:** If lab AE is real, instrument dump → restore factory → repeat only if still non-destructive on virgin; else use gene/`Kp` offline path for population `k0`.  
**Policy:** **Lab (CP4FCB) disposable.** Virgin: **no** UF2, **no** `test k0`, **no** bootwait, **no** SPI rewrite.

Related: `SWAP-TOCTOU-MAP-AND-TESTPLAN.md` (software `bda6df7` map), `FIRST-AE-NEXT.md`, `ATTACK-CHAIN.md`, `K0-CUSTOM-FW-DUMP.md`.

---

## 0 — Reality check (post-`bda6df7` factory loader)

Factory `loader.uf2` is **post-fix** (AEAD string present). Two different paths:

| Path | Trigger | Signature | SPI race value |
|------|---------|-----------|----------------|
| **Fresh 0-key swap** | Trial AES-GCM-SIV decrypt of page 0 under **all-zero** key succeeds | `validate_image(LOADER_TO_SWAP)` then **load-time ed25519ph rehash** over full signed region | Author still calls first check “extremely easy TOCTOU”; **phase1 rehash closes classic check-then-load** unless FI or mid-pass dual-read |
| **Device AEAD swap** | 0-key trial fails → `SWAP_KEY` decrypt | **No** pubkey; integrity = AEAD tags | Need device key or AEAD break; different attack |

**Code anchors (tree `src/xous-core`):**

1. `loader/src/platform/bao1x/swap.rs` — “Fresh swap image found…”, `validate_image(LOADER_TO_SWAP, Some(flash_spim), …)`  
2. `loader/src/phase1.rs` (~660–1113) — if `tag` set (unencrypted/fresh path), hash every SPI page as loaded, then `verify_prehashed` / FIDO2 ed25519  
3. Layout: swap at SPI flash origin `0x0000_0000`, header `PAGE_SIZE`, UF2 host view `0x7000_0000`, PDDB after 4 MiB reserved  

**Honest threat model after rehash:**

- Classic “sigcheck good image, then rewrite SPI before load” **should fail** load-time `ed25519ph` unless the rewrite still matches the signed hash (needs beta keys) or verification is glitched.  
- Residual first-AE angles that still justify SPI lab work:
  1. **Fault injection** on `verify_prehashed` / bollards / `die_no_std` (Lead 3).  
  2. **Mid-transaction SPI dual-read** (interposer returns A during hash pass, B during a later re-read if any path re-reads without re-verify — measure first).  
  3. Confirm **live** branch: fresh vs already-device-encrypted (timing, serial strings).  
  4. **Software-only** backup: MSC sector desync (`FIRST-AE-NEXT` Lead 2) — no SPI gear.

Do **not** flash a pre-`bda6df7` loader (needs beta keys; devkey path wipes secrets).

---

## 1 — Success criteria (what “lab PoC” means)

| Level | Definition | Virgin impact |
|-------|------------|---------------|
| **L0** | Serial map: which branch on cold boot; timings of Fresh/AEAD/ed25519ph | none |
| **L1** | Controlled SPI rewrite **outside** boot (lab) of unsigned / garbage swap → expected `SWAPSIGFAIL`/`SWAPDECFAIL`; restore OK | lab only |
| **L2** | Timed SPI rewrite **during** boot window; observe fail-closed (rehash works) or unexpected accept | lab only |
| **L3** | First AE: attacker-controlled code runs (e.g. instrumented console / marker in RAM or RRAM) **without** beta private key | lab only |
| **L4** | From L3, read population-class secrets **or** prove dump path that preserves PDDB `k0` | **not** on virgin until L3 solid + restore plan |
| **Production k0** | Prefer **gene oracle + Kp/Ko** (`kp_verify_workflow.md`) if AE remains closed | virgin oracle already done (6 samples) |

Hand to DEF CON: **population `k0` material for validation** — prefer offline crypto proof over destructive AE on live badges.

---

## 2 — Lab prep (non-negotiable)

1. Label badges: **LAB-CP4FCB** vs **VIRGIN** (never swap cables mentally).  
2. Factory restore triple ready: `factory-fw/extracted/{loader,xous,swap}.uf2`.  
3. Scripts ready: `tools/factory_restore_live.py`, serial capture @ **1 000 000** baud.  
4. Baseline serial log: cold boot lab → save `captures/spi_toctou/L0_baseline_<ts>.log`.  
5. Grep markers:

```text
Fresh swap image found
Swap encrypted with AEAD by device key
ed25519ph verification passed
FIDO2 ed25519 verification passed
LOADER.SWAPSIGFAIL
LOADER.SWAPDECFAIL
LOADER.SWAPDIE
LOADER.SWAPDEV
```

6. Optional: re-provision lab light key `0x42×32` via stock `test k0` **only on lab** after any PDDB churn.  
7. **Never** SPI-clip the virgin badge for this track.

---

## 3 — Phase L0 — Branch + timing map (no hardware hack)

**Do on lab only.**

| Step | Action | Record |
|------|--------|--------|
| L0.1 | Cold boot stock factory after restore | Full serial log |
| L0.2 | Note branch string (Fresh vs AEAD) | Branch ID |
| L0.3 | If AEAD: force **fresh** path — Update mode, re-copy **factory `swap.uf2` only** (signed 0-key shape), cold boot | Fresh path log |
| L0.4 | Timestamp (host or logic analyzer on UART TX): gap from “Fresh swap…” → “ed25519ph verification passed” → OS up | Window ms |
| L0.5 | Count SPI activity if clip already on CS/SCK (LA only, passive) | Burst pattern |

**Pass:** know whether lab boots **fresh** or **device-AEAD** after normal use; know approximate race window.

**If only AEAD forever after first encrypt:** first presentation of a new signed swap is the only software-visible TOCTOU window — plan L2 around **reflash factory swap then race first boot**.

---

## 4 — Phase L1 — Negative SPI integrity (lab, offline rewrite)

No mid-boot race yet. Proves restore + fail-closed.

| ID | Action | Expected |
|----|--------|----------|
| L1.A | Update-mode flash **garbage** `swap.uf2` (random / truncated) | Boot fails; `SWAPDECFAIL` / `SWAPSIGFAIL` |
| L1.B | Restore factory swap | OS returns |
| L1.C | Optional: 0-key decryptable but **unsigned** swap if you can craft offline | `SWAPSIGFAIL` (new finding if boots) |
| L1.D | Document SPI flash package (SOIC-8 clip?) and pinout from board photos / baosec schematics | Clip plan |

**Pass:** lab recoverable; fail-closed documented.

---

## 5 — Phase L2 — Mid-boot SPI rewrite (needs gear)

### 5.1 Hardware options (pick one)

| Option | Difficulty | Notes |
|--------|------------|-------|
| **A. SOIC-8 clip + dual host** | Medium | Host A = badge; Host B = programmer that can assert CS and write sectors while badge held / mid-boot |
| **B. FPGA / CPLD interposer** | Hard | Dual-image: ImageGood (factory signed) vs ImageBad (payload); mux on CS/SCK/IO0 |
| **C. Glitch-only (no rewrite)** | Hard | Skip pure SPI; FI VDD/clock during `verify_prehashed` (Lead 3) |
| **D. No gear** | — | Stop SPI track; run `kp_verify` + MSC desync software track |

**You tell me which of A–D you can field this week.** Without A/B/C, L2+ is blocked on SPI; crypto track still proceeds.

### 5.2 Experiment matrix (lab)

| Exp | Setup | Hypothesis |
|-----|-------|------------|
| E1 | Present factory swap; during “Fresh swap…” rewrite **one** code page in SPI to `0x41…` | Rehash fails → die (proves rehash live) |
| E2 | Same, rewrite **after** “ed25519ph verification passed” | If OS still boots clean: late re-read window; if crash: pages already in RAM/swap |
| E3 | Dual-image: good for all reads until hash complete, then bad | Should still fail if hash and load share one SPI read per page (current code path) |
| E4 | FI at ed25519 pass branch | First AE if glitch works |

**Pass for science:** E1 fails closed with serial evidence → document “load-time rehash effective against naive SPI TOCTOU.”  
**Pass for AE:** any E* yields controlled code exec → L3 writeup + instrumented dump path (lab only).

### 5.3 Capture layout

```text
captures/spi_toctou/
  L0_baseline_<ts>.log
  L1_garbage_swap_<ts>.log
  L2_E1_rewrite_during_hash_<ts>.log
  L2_E2_rewrite_after_verify_<ts>.log
  NOTES.md          # pass/fail + timings + photos of clip
```

---

## 6 — Phase L3 — First AE exploit shape (only if L2 opens)

If something accepts attacker pages:

1. Prefer **minimal** implant: serial `echo AE-POC` / known RRAM marker (see Chain C style) **without** full developer path if possible.  
2. Avoid `erase_secrets` / DEVELOPER_MODE unless intentional lab sacrifice.  
3. From AE, paths toward k0:
   - Read PDDB / light key if ROOT_SEED still valid (stock kernel material).  
   - Or dump gene material / KEYROM-adjacent only if already compromised path.  
4. Always have factory restore; prove restore before any virgin discussion.

**If L2 never opens:** SPI TOCTOU is **not** the production first-AE; pivot fully to:

- Offline **Ko‖Kp** with virgin oracle (`kp_verify_workflow.md`)  
- Optional MSC desync software fuzz  
- Disclosure package already in `disclosure/`

---

## 7 — Phase L4 — Production k0 (decision tree)

```
SPI / FI first AE on lab?
  YES → instrument k0 read on lab with known key proof
        → if method needs only stock-signed stages + no wipe:
              carefully evaluate virgin (notify-first for zero-days)
        → else: AE is lab-only demo; k0 from gene path
  NO  → gene path is primary for population k0:
          virgin_oracle_index.json (6 samples) already captured
          need Kp (public release) ± reduced Ko space
          tools/kp_offline_verify.py
```

**Hand to DEF CON:** validated population `k0` (or Ko) under `PRIVATE-NOTES.md` rules — **not** public GitHub.

---

## 8 — What I need from you (checklist)

Fill this when ready; I will drive the next step from your answers.

| Need | Why | Your status |
|------|-----|-------------|
| Lab badge on USB serial (COM?) + power | L0 logs | |
| Confirm factory restore still works | Safety | |
| SPI flash access: clip / interposer / none | L2 gate | |
| Logic analyzer or even phone slow-mo on serial? | Timing | |
| Glitch rig? (ChipWhisperer / EM / voltage) | Lead 3 | |
| Any **Kp** leak, Discord/tweet day schedule, or hex dump | Offline k0 | |
| About-screen `k0:` hash photo from **virgin** if shown | Extra verify | |
| Permission to run L1 garbage swap on lab (expect temporary brick until restore) | Risk | |
| Odd ideas when stuck | Always welcome | |

---

## 9 — Parallel track (no SPI gear required)

While waiting on hardware:

1. Run `tools/kp_offline_verify.py selftest`  
2. Keep watching for **Kp** public bits (defcon-scheme day schedule)  
3. Optional: MSC desync host prototype (`tools/uf2_sector_sim.py` already offline)  
4. Package notify draft: `disclosure/` + `FINDINGS-SUMMARY.md` (no secrets)

---

## 10 — Stop conditions

- Virgin cable used for UF2/SPI/bootwait → **stop**, assess damage.  
- Any candidate population key → verify offline only; install **only** on lab with `--yes` after multi-sample OK.  
- Live first AE zero-day → `PRIVATE-NOTES.md` notify-first, no public dump of k0.

---

*Last updated for dual-badge campaign: lab PoC → virgin validation → DEF CON handover.*
