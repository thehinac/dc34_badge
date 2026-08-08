# VULN-14 / VULN-15 — Stock OS console factory surfaces

## Summary

Factory `dc34-console` on production-class images exposes USB serial commands that can (1) **overwrite** the application light key `k0` without authentication (**VULN-14**) and (2) **enable bootloader bootwait**, forcing the next cold boot into boot1 update mode (**VULN-15**). Read-only `k0` dump is feature-gated; **write is not**.

## Affected

- Stock Xous baosec-lite console (lab: `v0.10.2-beta1-71-gf3e687b2b`)  
- USB serial after OS boot (lab: **1_000_000** baud, `VID:PID 1d50:6198`)

## VULN-14 — `test k0 <base64>`

### Details

- Decodes base64 → 32-byte key + 4-byte little-endian CRC32  
- On success calls `save_k0` — **no feature flag**, no password  
- Intended factory provisioner; remains reachable on stock production builds  
- Side effects in source: can reset badge type / tour flags depending on path  

### Impact

- **Integrity of mating / gene light-exchange keying** on units that still hold population material  
- Attacker does **not** learn the previous key (write-only)  
- Requires USB serial (physical or compromised host)  

### Reproduction

```text
test k0 <base64(key32 || crc32_le(key32))>
```

**Do not run this on someone else’s badge or on a unit whose population key you care about.**

### Not in stock (good)

- `test k0check` / `k0dump` — behind `hazardous-test` / `misc-test` only  

## VULN-15 — `test bootwait enable|disable|check`

### Details

- Via keystore opcode; any serial party can enable  
- Next **cold** boot stays in boot1 update mode  
- Enables VULN-10 UF2 oracle **without** holding the physical PROG button  

### Impact

- Staging for firmware integrity / DoS attacks  
- Local USB only  

## Other stock verbs (lower risk)

| Verb | Notes |
|------|--------|
| `test jig` | Vault factory jig UX |
| `test hw` / `test temp` | Factory selftest / sensor |
| `ver` / `echo` / `image` / `bio` | Normal / BIO upload surface |

## Recommendations

1. Gate `test k0` behind `cfg(feature = "factory-provision")` **off** in production  
2. Gate or remove `test bootwait` from production; or require physical confirmation  
3. Production help text should not imply factory verbs are available  
4. Consider USB serial disable or ACL after factory provision  

## Ops note (USB)

OS serial often fails if USBC is plugged before battery boot completes. Recovery: battery boot UI first, then USBC.

## Source

- `dc34-console/src/cmds/test.rs` (`k0`, `bootwait`)  
- `dc34-api` `save_k0` / `get_k0`  
