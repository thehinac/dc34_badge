# VULN-12 — Boot1 MSC: swap UF2 payload length panic (update-mode DoS)

## Summary

MSC handling of swap-targeted UF2 blocks (`0x70000000+`) does `record.data().try_into()` into a **fixed 256-byte** page array, then unwraps. Any `payload_size ≠ 256` panics the boot1 task, hanging update mode until power cycle.

## Affected

- Stock boot1 with baosec SPI swap path (`PageAssembler` / SPIM)  
- Serial non-SPI builds reject swap addresses (no panic on serial)

## Details

Conceptual:

```text
assembler.add_page(spim_addr, record.data().try_into().unwrap())
// PAGE_SIZE = SPINOR_PAGE_LEN = 256
```

Factory `swap.uf2` always uses `payload_size = 256`. Attacker-controlled UF2 need not.

## Impact

- **Availability:** USB serial + BAOCHIP disappear; requires **power cycle** (lab-confirmed recoverable, not permanent brick)  
- Practical denial of firmware update service  

## Reproduction (lab)

1. Update mode + BAOCHIP mounted  
2. Copy UF2 block: family `0xa7d76373`, addr `0x70000000`, `payload_size = 200` (or other ≠ 256)  
3. Observe host disconnect / COM gone  
4. Power cycle recovers boot1  

## Recommendations

1. Replace unwrap with length check; ignore or error-log bad sizes  
2. Gate `payload_size == 256` before `add_page`  
3. Watchdog reset to update mode instead of hang  

## Source references

- boot1 USB MSC handlers / page defrag (xous-core)  
