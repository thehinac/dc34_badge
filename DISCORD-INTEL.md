# Discord export intel (2026-08-07 scans)

Sources:

- `Downloads/[DiscordKit] dc34_baochip_20260807_160358.json` — Baochip `#dc34` (~557 msgs)
- `Downloads/[DiscordKit] Official DC 34 Badge - General Chat_DEFCON_20260807_160524.json` (~232 msgs)

Full scrape artifacts: `captures/discord_deep_hits.txt`, `captures/discord_k0_context.txt`.

**Policy:** no population `k0` in public docs. Community claims below are **unverified** unless noted.

---

## TL;DR — what moves us forward

| Finding | Usability | Action |
|---------|-----------|--------|
| **No official Kp hex yet** (Bluesky/Mastodon/Discord exports) | Blocks day-N brute | Watch channels below |
| **SHA-256(k0) prefix `dca9ea49`** (community, Diagnostics) | Soft 32-bit filter for candidates | Wired into `kp_offline_verify.py` |
| **“Last byte of k0 is b3”** (ohyou_) | **Untrusted** single claim | Optional filter only after GCM-SIV verify |
| **Gene oracle path is the intended non-wipe win** | Confirmed by jonfen writeup + scheme | We already have 6 virgin samples |
| **BIO → SRAM k0 dump** | Claimed open; **vmfunc measured BDMA whitelist empty** | Do **not** spend lab time unless new firmware/filter proof |
| **SPI TOCTOU / flash dual-image** | Community discussing same angle; post-`bda6df7` | Still our SPI lab plan residual |
| **amattas: THE_FLAG_1 + root store** | Hardware team progress; writeup withheld | FI path exists; not needed if crypto works |
| **gamechangersai claim k0** | Unverified brag | Ignore until hex + sample verify |
| Official hub | **https://defcon.org/34b/** | Updates + latest.zip |

---

## Confirmed / high confidence

### Official

- **defcon.org/34b/** — exchange how-to, update UF2, source links, `dc34@baochip.com` for 0-days.  
- Dev mode = one-way, wipes provisioned secrets (light key).  
- Latest firmware mirrors: CI + `https://defcon.org/34b/latest.zip` (“already a patch”).  
- Bunnie: BIO tools preserve badge functionality while you chase the flag; full Xous reflash does not.

### Bunnie (Discord)

- Developer mode wipes **master keys** and **light exchange key**.  
- After flag recovery you can `test k0` the key back into a **dev-mode** badge; sticky DEVELOPER_MODE remains.  
- Three “flags” provisioned; moving to dev wipes at least one.  
- QR OOB = Xous KP (watchdog), not secret recovery.

### Community research (cross-checked with source / other teams)

- **jonfen/FLAG_HUNT_ANALYSIS.md** (excellent, aligns with our tree):  
  - `K = Ko‖Kp`; non-destructive = **offline GCM-SIV brute** after Kp day drops.  
  - `test k0` write-only; `k0check` not in stock.  
  - About Diagnostics: `k0:` = first 8 hex of **SHA-256(k0)** (32 bits).  
  - BIO BDMA filtered (gutter); flag1 needs FI/IRIS; flag2 survivor dump is destructive.  
  - Kp watch: Mastodon `@bunnie@social.treehouse.systems`, Bluesky `@baochip.com`.  
  - **As of their 2026-08-07 note: no Kp proclaimed yet.**  
- **vmfunc/dc34-badge**: BIO exec real; **memory filter empty** — kills eaglerific’s “BIO can read any address” claim for shipped silicon.  
- Console **1_000_000** baud (not 115200).

---

## Soft intel (use carefully)

| Claim | Who | Notes |
|-------|-----|--------|
| `SHA-256(k0)[:4] = dca9ea49` | eaglerific | Matches About-screen format; **confirm on virgin Diagnostics** |
| Last byte of k0 = `0xb3` | ohyou_ | Single message; may be wrong or partial |
| “51.. 4c…” | ohyou_ | Fragment; ignore unless explained |
| SPI dual-image for k0 | h3xcat | Same class as our SPI plan; they note new FW targets it |
| THE_FLAG_1 + ROOT extracted | amattas | Private writeup later; not our k0 path yet |
| k0 recovered | ogthorne / gamechangersai | No material published in export |

---

## Links worth keeping open

| URL | Why |
|-----|-----|
| https://defcon.org/34b/ | Official updates / FW |
| https://github.com/jonfen/dc34-badge/blob/master/FLAG_HUNT_ANALYSIS.md | Best public analysis + cracker design |
| https://github.com/vmfunc/dc34-badge | BIO/ACL measurements |
| https://github.com/bunnie/dc34-bio | Unsigned BIO load (SAO), not k0 |
| https://github.com/bunnie/dc34-image | Image upload |
| https://bsky.app/profile/baochip.com | Kp drops |
| https://social.treehouse.systems/@bunnie | Kp drops |
| https://badge.sex | Gene social map (no keys) |
| `dc34@baochip.com` | Responsible disclose |

---

## Implications for our campaign

1. **Crypto track remains primary** for production k0 handoff.  
   - We already have 6 virgin oracle samples (stronger than jonfen’s single transcript).  
   - **Blocking input is still official Kp** (or day-4 reduced space).  
   - When Kp appears:  
     `python tools/kp_offline_verify.py verify --ko-hex … --kp-hex …`  
     or brute with hash prefix filter.

2. **BIO AE path is cold** unless someone publishes a filter-bypass PoC that contradicts vmfunc.

3. **SPI TOCTOU** still valid lab science; community agrees post-fix loader is the hard target.

4. **Do not** chase Discord “we have k0” claims without feeding candidates into our verifier.

5. **User task (cheap):** on **virgin**, About → Diagnostics → photo of `k0: ********` line.  
   - If it is `dca9ea49…`, community hash is confirmed.  
   - Never run `test k0` on virgin.

---

## Watch list (for next Discord export / social poll)

- Any hex blob labeled Kp / public key / day 2–4  
- Bunnie or Baochip posts with long hex  
- Confirmed full k0 (verify offline only; private storage)  
- BIO filter reconfiguration from host without wipe  
- New FW changelog on defcon.org/34b  

---

*Generated from local DiscordKit JSON + public pages, 2026-08-07.*

