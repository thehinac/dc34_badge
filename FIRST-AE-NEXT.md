# First production AE — next leads (actionable)

After Chains A–C, virgin production still needs **first code exec** without stolen keys.

---

## Lead 1 — Fresh-swap SPI TOCTOU (highest software+HW hybrid value)

**Where:** `loader/src/platform/bao1x/swap.rs` after zero-key trial decrypt succeeds:

```text
"Fresh swap image found - checking signature..."
validate_image(LOADER_TO_SWAP, Some(flash_spim), ...)
// author: TOCTOU extremely easy if SPI changes under loader
// then pages loaded from SPI for real boot
```

**Attack sketch (needs hardware):**

1. Present **valid signed** fresh swap (zero-key path) so sigcheck passes  
2. Between check and load, **rewrite SPI** (interposer / dual-port / glitch hold)  
3. Loader executes attacker pages  

**Post-`bda6df7`:** non-zero device-key AEAD path does **not** re-check pubkey — TOCTOU there is different (need device SWAP_KEY or break AEAD). Fresh zero-key path is the interesting one for first presentation of updates.

**Lab without interposer:** only partial — confirm loader still emits “Fresh swap…” on factory first-flash style images; cannot complete race.

**Equipment:** SPI flash clip + host that can rewrite mid-boot, or FPGA interposer.

---

## Lead 2 — Custom MSC host sector desync (pure software, medium odds)

**Bug shape:** `Uf2Sector.extend_from_slice`:

- On LBA mismatch: `address = address % 512`  
- **`progress` and partial `data` not cleared**  
- Attacker-controlled USB MSC can deliver half a sector, jump LBA, complete hybrid 512B frame  

**Goal:** force decode of attacker `target_addr` / payload that still passes range+family — likely still limited to storage window (same write oracle). Unlikely to write boot1 unless range bypass emerges from hybrid parse.

**Work:** Windows raw USB MSC initiator (libusb + BOT), or Linux gadget; feed crafted partial CBWs. Offline model: `tools/uf2_sector_sim.py`.

**ROI:** may only re-prove write oracle; still worth short fuzz for surprises (double-apply, RAM confuse).

---

## Lead 3 — Fault injection on `validate_image` / erase policy

Classic. Authors already use delays, bollards, dual reads. Needs glitch rig. Highest cost.

---

## Lead 4 — Stock OS as staging only

`test bootwait enable` + `test k0` are **pre-AE** impacts (update force, key overwrite). They do **not** replace first AE for bootkit on virgin silicon.

---

## Recommended order without new hardware

1. **Stop and package** Chains A+B for notify (FINDINGS-SUMMARY + ATTACK-CHAIN)  
2. Optional: short **libusb MSC desync** prototype (Lead 2)  
3. Optional: **hazardous-test** console build for lab k0check after re-provision `0x42`  
4. Defer Lead 1/3 until SPI/FI gear  

**Active campaign docs (2026-08-07+):**

- `SPI-TOCTOU-LAB-PLAN.md` — lab L0–L4 SPI/FI plan, what gear is needed  
- `kp_verify_workflow.md` + `tools/kp_offline_verify.py` — population k0 via Ko‖Kp + virgin oracle  
- Virgin samples already in `captures/virgin_VIRGIN-PENDING_*/gene/virgin_oracle_index.json`

---

## Current lab state after continue (2026-08-07)

- Baremetal **COM19**  
- Storage markers + **BM1P persist** verified via peek  
- Factory OS available again after: cold bootwait → copy factory UF2s → boot → battery-then-USBC → COM18  
