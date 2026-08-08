# Loader swap TOCTOU — status (INFO-18 / OPEN-2)

## Historical bug (fixed)

Commit [`bda6df7`](https://github.com/betrusted-io/xous-core/commit/bda6df7a5befd605f4a1a431718127bfaebe24af)  
(“cleanup long-standing TOCTOU attack on the swap”, 2026-07-26):

**Pre-fix (conceptual):**

```text
trial decrypt page 0 with swap.key
  OK + key == 0  → validate_image (pubkey) required
  OK + key != 0  → NO signature check   ← structural hole
  FAIL           → device SWAP_KEY AEAD path
```

**Post-fix:**

```text
trial decrypt page 0 with 0-key
  OK   → ALWAYS validate_image; devkey swap requires DEVELOPER_MODE
  FAIL → device SWAP_KEY AEAD; print AEAD message; no pubkey on that path
```

## Factory DC34 loader (lab UF2)

String scan of stock `loader.uf2` includes exclusive post-fix markers, e.g.:

- `Swap encrypted with AEAD by device key, signature check not required`  
- `Fresh swap image found - checking signature…`  
- `LOADER.SWAPSIGFAIL` / `SWAPDECFAIL` / `SWAPDIE`

**Conclusion:** stock factory loader in our lab tree is **post-fix**.  
A naive “encrypt under non-zero loader key and skip sig” attack should **not** work.

## Residual physical concern (OPEN-2)

Even post-fix, source comments note that **fresh 0-key** presentation depends on SPI contents under the loader, and a physical adversary with SPI control can attempt races.

**Hardening present in current tree:** phase1 load path **re-hashes SPI pages** and runs ed25519ph / FIDO2 verify over the signed region as data is loaded — so classic “sigcheck then rewrite entire image before use” is **much harder** than pre-fix software skip.

Residual research angles:

1. Dual-image / mid-transaction SPI (interposer)  
2. Fault injection on final verify  
3. First-presentation window timing after factory swap reflash  

**Status:** not a completed public exploit; hardware lab work in progress.

## SPI flash identity (core module schematic)

From [bunnie/dc34-core-hw](https://github.com/bunnie/dc34-core-hw) `memory.kicad_sch`:

| Ref | Part | Role |
|-----|------|------|
| U2 | `ZD25Q64BSIGT` | 64 Mbit SPI NOR (swap/PDDB) |
| — | APS6404 / IS66 class | SPI PSRAM (not the TOCTOU target) |

Package: SOIC-8, 1.27 mm pitch. Bus: QSPI2 (`CS0`/`CS1`, SCK, D0–D3).

## Negative lab tests (stock loader)

| Test | Expected / observed |
|------|---------------------|
| Garbage / truncate swap | Fail closed (`SWAPDECFAIL` / halt) |
| Incomplete SPI holes | AEAD/sig fail (DoS) |
| Factory restore triple | Recoverable |

## Recommendations

1. Ensure first presentation of signed swap only in controlled environments; encrypt to device `SWAP_KEY` ASAP after first boot.  
2. Continue physical dual-read / bollard hardening on SPI path.  
3. Document for auditors: software non-zero-key skip is fixed; residual risk is physical.  
