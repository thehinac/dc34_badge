# Kp / Ko offline verify workflow — population k0 without wiping virgin

**Goal:** Recover or validate population light key  
`K = Ko || Kp` (32 bytes, AES-256-GCM-SIV for gene protocol)  
using **only** already-captured virgin gene samples + publicly disclosed (or leaked) key material.

**Does not require first AE.** Complements SPI TOCTOU plan.

**Policy:** Never publish full `K` / `Ko`. Never `test k0` on virgin. Lab install only after multi-sample verify.

---

## 1 — Scheme (from `src/dc34-vault/defcon-scheme.md`)

| Piece | Role | Size (design) |
|-------|------|----------------|
| **Ko** | Shared secret all badges; erased on developer mode | ~**96 bits** day 1 (12 bytes) |
| **Kp** | Public / progressively disclosed | ~**160 bits** day 1 (20 bytes) |
| **K** | `Ko ‖ Kp` | **256 bits** (32 bytes) |

Gene response (donor QR):

```text
C || tag = AES-256-GCM-SIV(K, Nonce1, haploid[9] || pad || badge_type@15, AD=null)
```

Challenge phase-1 QR: `header || Nonce1` (we generate Nonce1 offline).

Day schedule (scheme — confirm against live DEF CON announcements):

| Day | Remaining Ko strength (claimed) |
|-----|----------------------------------|
| 1 | 96 bits |
| 2 | 64 bits |
| 3 | 56 bits |
| 4 | 48 bits |

Brute force is only practical once **unknown Ko bits** drop (day schedule, partial leak, or known prefix/suffix).

---

## 2 — What we already have

| Asset | Location |
|-------|----------|
| 6 virgin oracle samples | `captures/(local virgin capture dir — not published)/gene/virgin_oracle_index.json` |
| Per-session jsonl | same `gene/` folder + `captures/session_*` |
| Lab known key | `0x42` × 32 (not population) |
| Verify tool | `tools/extract_k0_lab.py verify` + **`tools/kp_offline_verify.py`** (this workflow) |
| Soft hash filter | Community claim: `SHA256(k0)[:4] = dca9ea49` (About Diagnostics). Confirm on virgin. |
| Discord intel | `DISCORD-INTEL.md` — no official Kp in exports as of 2026-08-07 |

All virgin ciphertexts: **32 bytes**, **do not** decrypt under lab `0x42`.

### Where Kp will appear (not in repos)

Per scheme + community watch list:

- Bluesky: https://bsky.app/profile/baochip.com  
- Mastodon: https://social.treehouse.systems/@bunnie  
- Discord / Matrix from https://defcon.org/34b/  
- **Status 2026-08-07:** no Kp hex on those public feeds yet (checked).

---

## 3 — Workflow overview

```text
                    ┌─────────────────────┐
  Kp hex (public) ──┤                     │
  Ko candidate ─────┤  kp_offline_verify  ├──► OK on all samples
  full K hex ───────┤                     │         │
  partial mask ─────┘                     │         ▼
                                          │   SHA-256(K) vs About
                                          │   install on LAB only
                                          └─────────────────────
```

1. **Ingest Kp** when released (Discord / stage / tweet / file).  
2. **Compose** candidates: full K, or Kp + Ko search.  
3. **Verify** against **all 6** virgin samples (MAC must pass).  
4. Optional: match About-screen `k0` hash if photographed.  
5. **Install only on lab** (`extract_k0_lab.py install --yes`) to join mating as population peer.  
6. Hand validated material to DEF CON under private channel rules.

---

## 4 — Commands

Use Python 3.12 if `python` is a Store stub:

```powershell
cd (local lab tree)
$py = "python"  # or full path to Python 3.12+

# Crypto plumbing selftest (synthetic 0x42 + real index load)
& $py tools/kp_offline_verify.py selftest

# Show virgin sample count / first nonce
& $py tools/kp_offline_verify.py status

# Full 32-byte key candidate
& $py tools/kp_offline_verify.py verify --key-hex <64 hex chars>

# Known Kp (20 bytes) + known Ko (12 bytes)
& $py tools/kp_offline_verify.py verify --ko-hex <24 hex> --kp-hex <40 hex>

# Kp known; brute remaining Ko bits (ONLY when space is small)
# Example: 24 unknown bits with fixed Ko prefix
& $py tools/kp_offline_verify.py brute --kp-hex <40 hex> --ko-prefix-hex <...> --ko-unknown-bits 24

# Match About-screen hash only
& $py tools/kp_offline_verify.py hash --key-hex <64 hex>
```

Also still works:

```powershell
& $py tools/extract_k0_lab.py verify --key-hex <64 hex>
```

Default sample source: virgin index. Override:

```powershell
& $py tools/kp_offline_verify.py verify --key-hex ... --samples path\to\index.json
```

---

## 5 — When Kp appears

1. Paste full public blob into a local file only (not git):  
   `(private local only) (create `private/` if needed; keep out of public repos).  
2. Confirm length: design is **20 bytes** for day-1 Kp (160 bits). If they release a different layout, record endianness and whether K is `Ko‖Kp` or `Kp‖Ko` (scheme says **Ko then Kp**).  
3. Run verify with trial Ko = zeros / common test patterns first (expect fail).  
4. If day-N reduces Ko to ≤40 bits, run `brute`. Above ~40 bits pure Python is slow; use GPU/hashcat-class only if you build a GCM-SIV checker (not shipped).  
5. On first **all-samples OK**:  
   - Print `k0_hash = SHA256(K)`  
   - Save privately: `(private local only) (mode 600 mindset)  
   - **Do not** commit  
   - Notify path per `PRIVATE-NOTES.md` before any public claim  

---

## 6 — Partial-Kp / odd ideas

If only **partial** Kp is known:

| Situation | Action |
|-----------|--------|
| Kp known, Ko unknown 96-bit | Wait for day schedule or AE leak; do not thrash CPU on 2^96 |
| Kp known, Ko unknown 48-bit (day 4) | GPU/cluster territory; script supports small brute only |
| Known Ko prefix from glitch/side channel | `--ko-prefix-hex` + `--ko-unknown-bits` |
| Bit-flip hypotheses | `--key-hex` for each candidate; batch via `--candidates-file` |
| Lab 0x42 decrypts a “virgin” sample | That sample is not population — re-check badge |

Odd ideas when stuck (you said you’re here for these):

- Photograph every official “key leak” slide; OCR carefully (Base45 rules already bit us).  
- Check if Kp is embedded in badge art / audio / IRIS story (unlikely but free).  
- Cross-badge: second virgin gene sample set should decrypt under **same** K (population shared).  
- If AE later dumps any 32-byte PDDB `k0`, verify against index **before** trusting dump.

---

## 7 — Install on lab (after full verify)

```powershell
# ONLY lab COM port. NEVER virgin.
& $py tools/extract_k0_lab.py install --key-hex <validated 64 hex> --port COM18 --yes
# power-cycle lab; confirm gene mate with virgin donor
```

Lab was often on `0x42`; overwriting with population K is intentional for mating tests.

---

## 8 — What I need from you for this track

| Need | Priority |
|------|----------|
| Any **Kp** hex / announcement / photo | **Critical** |
| Day-number confirmation of strength schedule | High |
| Virgin About `k0:` hash if UI shows it | Medium |
| Extra gene samples if any sample OCR was flaky | Low (6 is enough for verify) |
| GPU box if we hit day-4 48-bit brute | Optional |

No more gene captures required for verify plumbing — samples already in the index.

---

## 9 — Mapping to DEF CON handover

| Deliverable | Source |
|-------------|--------|
| Population `K` (or Ko + Kp) | Offline verify OK × 6 samples |
| Proof | Script transcript + hashes (not full key in public ticket) |
| Vuln writeups | `disclosure/` (no k0) |
| First AE | Separate SPI/FI track; optional for k0 if crypto wins first |

---

*Virgin oracle complete 2026-08-07. Waiting on Kp / reduced Ko / AE.*

