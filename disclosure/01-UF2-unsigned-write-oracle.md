# VULN-10 — Boot1 update mode: unsigned UF2 write oracle

## Summary

While in boot1 USB update mode (BAOCHIP MSC or serial `uf2`), the device accepts **unsigned** UF2 blocks and programs RRAM (loader/kernel window) and, via MSC, SPI swap pages. Signature verification occurs only later at `try_boot`. An attacker with USB can corrupt next-stage firmware (DoS until reflash) or plant a **validly signed** implant if they possess signing keys.

## Affected

- Stock boot1 `v0.10.1-0-gbcfdca404` (lab; OEM baosec-lite default)
- Paths: USB MSC write loop; serial `uf2`
- Family ID check uses public constant `BAOCHIP_1X_UF2_FAMILY = 0xa7d76373`

## Details

1. UF2 parse validates magics, length, `payload_size ≤ 476`, family ID — **not** payload signature.  
2. Range check (non-`alt-boot1`): start address in `[BAREMETAL_START, STORAGE_END]`  
   - `BAREMETAL_START` ≈ `0x60060000`  
   - `STORAGE_END` ≈ `0x603DA000`  
3. **VULN-11:** MSC uses inclusive high bound; serial uses exclusive high. Address `0x603DA000` serial-rejects; MSC may pass range then AccessDenied. **No sticky keyband overflow observed.**  
4. **VULN-13:** `block_no` / `num_blocks` not enforced; sequential multi-block UF2 programs multiple addresses.  
5. Boot1 code region is **not** writable via stock UF2.  
6. Serial path has no SPI swap assembler; MSC targets `0x70000000+` for swap flash pages.

## Impact

- **Availability:** brick until factory reflash of loader/xous/swap  
- **Integrity:** plant signed malware if beta/bao keys compromised  
- **Not:** free unsigned code execution

## Reproduction (lab)

1. Enter update mode (button+reset, or **VULN-15** bootwait cold boot).  
2. Serial: `uf2 <base64 of 512-byte UF2 block>` targeting `0x60060000+`  
3. Or copy crafted `.uf2` to BAOCHIP volume  
4. Observe write (serial prints `Wrote …`; MSC silent success)  
5. `try_boot` / `boot` fails without valid signature  

Lab markers observed after peeks: residual words such as `MBLK`, `MSC0`, `OS2B`, U3 edge markers under baremetal inspection.

## Recommendations

1. Require signature (or device-bound MAC) **before** programming RRAM/SPI, or  
2. Restrict unsigned programming to a locked factory ACL / physical jig, or  
3. Erase programmed pages if `try_boot` fails; rate-limit update mode  
4. Align MSC vs serial range checks  
5. Reject `addr + len` past storage end (defense in depth)  
6. Enforce `block_no` / `num_blocks` if multi-block is intended  

## Source references

- `bao1x-boot/boot1` UF2 handlers / `repl.rs` / `uf2.rs` (xous-core)  
- Family ID public in bao1x headers  

## Related

- VULN-12 — MSC swap length panic  
- VULN-15 — software path into update mode  
