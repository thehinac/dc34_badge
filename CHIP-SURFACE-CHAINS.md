# Chip-maker surface × QR / existing exploits — deep chain analysis

> **Hardware note (2026-08-07):** VULN-1 and VULN-5 (L1/L2) are **VERIFIED** — see  
> `qr-codes/exploits-real/VERIFIED.md`. QR panic → boot1 auto-escalation was **falsified**.  
> boot1 `audit` identity dump **verified** with bootwait + serial.

Sources reviewed (2026-08-07):

| Repo | What we used |
|------|----------------|
| [betrusted-io/xous-core](https://github.com/betrusted-io/xous-core) `dev` | `README-baochip.md`, `bao1x-boot/boot1`, `devkey/`, `services/keystore`, `bao-video` |
| [bunnie/dc34-vault](https://github.com/bunnie/dc34-vault) | QR / HandleQr / factory / jig |
| [bunnie/dc34-console](https://github.com/bunnie/dc34-console) | `test *` serial surface |
| [baochip/baochip-1x](https://github.com/baochip/baochip-1x) | silicon docs (HW; no app hooks) |

Local mirrors: `C:\Users\thehinac\dc34-lab\src\{xous-core,dc34-*}`.

**Lab fact:** `test bootwait check` → **`bootwait is true`** on COM18. That is the hinge for several chains below.

---

## Mental model: three trust layers

```text
┌─────────────────────────────────────────────────────────┐
│ Layer C — Application (dc34-vault / console)            │
│   QR camera, gene crypto, password/TOTP, serial REPL    │
│   ★ Our QR vulns + serial log dumps live here           │
└───────────────────────┬─────────────────────────────────┘
                        │ reboot / panic / WFI
┌───────────────────────▼─────────────────────────────────┐
│ Layer B — boot1 (factory-programmed, USB MSC + serial)  │
│   UF2 flash, audit, bootwait, lockdown, self_destruct   │
│   ★ Reachable if bootwait OR PROG-held power-on         │
└───────────────────────┬─────────────────────────────────┘
                        │ verified next stage
┌───────────────────────▼─────────────────────────────────┐
│ Layer A — boot0 (immutable RoT) + KEYROM / OWC / RRAM   │
│   Mutual distrust, developer key wipe policy            │
│   ★ No QR path; only glitch/factory ATE / signed boot   │
└─────────────────────────────────────────────────────────┘
```

**There is no QR opcode that talks to boot1 or KEYROM directly.**  
Every “one step further” path is: **QR/app bug → side effect → serial/boot1/custom FW**.

---

## Chip-maker hooks left “open” (intentional platform surface)

### 1. Public **developer signing key** (by design)

Path: `xous-core/devkey/dev.key` (+ PQ `dev-pq.key`, README).

- Anyone can sign images with the well-known Ed25519 (and PQ) **dev** key.
- Boot policy: **developer image ⇒ Baochip secrets erased**, DEVELOPER_MODE OWC bumps.
- `baosec` factory runs **`lockdown`** on many units (revokes dev key slot) — **not all research units may match**.
- **Does not give free k0**: by the time your code runs, chip secrets for light game / attestation are gone.

**Use for us:** full lab reflash, hazardous-test builds, custom vault with intentional serial dumps — **after** accepting secret wipe.

Docs: [README-baochip.md § Security Model](https://github.com/betrusted-io/xous-core/blob/dev/README-baochip.md).

### 2. **boot1** serial command shell (CPU bring-up / factory)

Listed help string in `bao1x-boot/boot1/src/repl.rs`:

```text
altboot, audit, boot, boardtype, bootwait, echo, idmode, ifr,
localecho, lockdown, paranoid, require-pq, reset, self_destruct,
skipping, uf2, usb_speed
(+ feature-gated: ate, qe, bogomips, publock, …)
```

| Command | What it does | Risk / value |
|---------|----------------|--------------|
| **`audit`** | SN, UUID, USB serial#, board type, stepping A0/A1, revocations, boot0/1 validate, hashes | **Identity dump to serial** |
| **`bootwait`** | Enable/disable stop-in-boot1 | **Persistence of attack surface** |
| **`uf2`** | Base64 UF2 block write to RRAM/swap | Full firmware rewrite |
| **`boot` / `reset`** | Continue or hard reset | Lifecycle |
| **`ifr`** | Hexdump fixed IFR window `0x6040_0000` (sealed → often zeros in USER) | Limited memory window |
| **`lockdown`** | Permanently revoke developer key slots (+ paranoid/pq) | Irreversible; refuses if boot1 is already **dev-signed** |
| **`self_destruct void_my_warrantee`** | Permanent RRAM wipe / brick | Nuclear |
| **`baosec-init confirm`** | Erase external flash, set board type | Factory provisioning |
| **`ate` / `atecheck`** | Wafer/ATE probe path → write ATE blob to slot | Factory test residue |
| **`paranoid` / `require-pq`** | One-way policy flags | Irreversible hardening |
| **`boardtype` / `altboot` / `idmode` / `usb_speed`** | OWC lifecycle knobs | Misconfig / research |

Flashing script: `bao1x-boot/uf2send.py` (serial UF2 with CRC).  
CI UF2s: `https://ci.betrusted.io/latest-ci/baochip/bootloader/`.  
Hold **PROG** on USB plug → mass storage `BAOCHIP` / `ALTCHIP` for UF2 drag-drop.

### 3. OS serial debug still open on production DC34

| Surface | Origin | Notes |
|---------|--------|--------|
| `test k0 <b64+crc>` | dc34-console (factory left in) | **Write** light key; wipe badge type |
| `test bootwait …` | keystore OWC via console | **Lab has bootwait=true** |
| `test proc` / `freemem` / `interrupts` | PlatformSpecific syscalls | Process map / RAM sizes |
| `test jig` → vault opcode 1025 | Factory retest UI | Mode FactoryTest |
| `image` / `bio` upload | Console | Pixel / BIO co-proc code |
| `test wfi` / `deep` | Power | USB drop |
| `k0check` / `transmute` / `reset` | Source only | **Not** in production binary (`hazardous-test` / `misc-test` / `qa-test` flags) |

### 4. bao-video / camera

- QR decode path used by vault `acquire_qr` — production feature.
- Comment in bao-video: `todo!("Need to write this for factory testing");` — incomplete factory camera hook, **not** an extra open door we can call from QR today.

### 5. Mutual-distrust / collateral keys

Third-party `boot1` can keep `collateral` if OEM pubkeys differ; OEM images erase collateral.  
**No QR path.** Relevant only if building third-party secure boot after dev wipe.

---

## Attack chains: QR / known vulns → one step further

### Chain 1 — QR DoS → boot1 (**LIVE TESTED 2026-08-07 — partial**)

```text
Preconditions: bootwait enabled (LAB: TRUE), USB serial attached

1. Scan CVE-oob-short-15-aa.png  (VULN-1 HandleQr OOB panic)
2. Observed: vault PID panics — NOT full SoC reboot
3. bootwait does NOT engage (no boot1)
4. OS console (dc34-console) and other PIDs stay up; vault is dead
```

**Live capture:** `dc34-lab/captures/chain1_live.log`

```text
got qr data: +PL+PL+PL+PL+PL+PL+PLZ3, mode: GeneScan
mode: GeneScan, s: +PL+PL+PL+PL+PL+PL+PLZ3
PANIC in PID 13: … main.rs:624:40: range end index … length 15
fatal runtime error: failed to initiate panic, error 5, aborting
```

Post-panic `test proc`: **PID 13 dc34-vault missing**; kernel…console still present.  
`bootwait is true` still, but unit never left Xous.

**Revised value of VULN-1:**
- Hard DoS of badge UI / lights / QR / FIDO vault process until **manual full reboot**
- Full QR payload + panic traceback on serial (info disclosure + reliability crash)
- **Does not** auto-escalate to boot1 on this firmware

**Still valid paths to boot1 (not QR-only):**
- Power cycle / reset while `bootwait` enabled
- Hold PROG on USB plug
- Possibly other reboot vectors (`test deep`? physical button) — not QR panic

PoCs: `exploits-real/CVE-oob-*.png`.

---

### Chain 2 — Serial dump while mating / TOTP (app layer only)

```text
serial_qr_watch.py COM18 -o log.txt
+ Totp mode + any QR     → all TOTP secrets (VULN-5 L2)
+ pwauth://new           → password line
+ gene mate / phase-1    → nonce + egg/sperm + Received gene
```

**No boot1 needed.** Highest secret yield **without** reflash.  
Does not dump population `k0`.

---

### Chain 3 — Serial `test k0` + gene forge (owned light crypto)

```text
test k0 <provision blob>   # already did 0x42… on lab
forge_led_gene.py → QR → LEDs
```

**Intentional factory surface**, not a chip bug.  
**Destroys** original factory light key on that unit.

---

### Chain 4 — boot1 + public **devkey** → custom firmware

```text
Enter boot1 (PROG or bootwait+reboot or Chain 1)
Sign image with xous-core/devkey/dev.key
Flash loader/xous/swap UF2 (uf2send.py or MSC)
```

**Get:** arbitrary code, can add `k0` read, PDDB dump, etc.  
**Lose:** chip secrets wiped on developer image (by design).  
**Cannot:** recover wiped population k0 from KEYROM after wipe.

Useful for **lab instrumentation** (prove PDDB layout, log every IPC), not for “steal factory k0 from stock badge.”

---

### Chain 5 — Social QR + serial sniffer (con floor)

```text
Attacker has brief USB access OR victim plugs into “charger” with serial mux
Victim scans any QR / mates lights
→ serial captures phase-1 Base45 (nonce) + optional gene CT + TOTP if token mode
```

Offline: decode Base45 → nonce; with future k0 leak/crack, decrypt gene captures.

---

### Chain 6 — What does **not** chain (dead ends for k0)

| Idea | Why it fails |
|------|----------------|
| QR → read k0 | No code path; only SHA-256 prefix on About |
| QR → boot1 without bootwait/PROG | No |
| Dev-signed UF2 → dump factory secrets | Secrets erased **before** app runs |
| `ifr` dump → k0 | IFR sealed; prints zeros / non-k0 region |
| `test proc` → secrets | Addresses only |
| Factory UF2 restore | Restores OS image, **not** PDDB k0 |
| baochip-1x RTL | Simulation / silicon; no runtime QR hook |

---

## “CPU-specific” / hardening notes

- **Stepping probe** in `audit` (A0 vs A1) flips RRCR bit 12 — research interest, not QR-reachable.
- **`skipping` / `paranoid` / `require-pq`** — one-way security policy OWCs; boot1 only.
- **PlatformSpecific** syscalls (1=freemem, 2=proc, 3=interrupts) — debug ABI still callable from **production** console `test` (intentional debug left in).

---

## Recommended next lab experiments (ordered)

1. **Prove Chain 1 on this unit**  
   - Serial watch → scan short OOB QR → confirm boot1 prompt / `BAOCHIP` volume / `audit` output.  
   - Document exact reboot behavior (vault-only restart vs full SoC reset).

2. **boot1 `audit` capture**  
   - Save SN/UUID/revocation table; compare to About-screen k0 hash (correlation research only).

3. **Instrument, don’t wipe (if secrets still matter)**  
   - Prefer serial TOTP/gene dumps over devkey reflash.

4. **If lab disposable**  
   - Devkey-signed vault with `log::info!` of `get_k0()` after PDDB mount — only works if k0 still in PDDB **and** wipe policy didn’t clear PDDB (verify: developer mode wipe scope is KEYROM/chip secrets; PDDB may still hold application `dc34/k0` written by factory!).  

   **Critical open question:** Does developer-image entry erase **PDDB `dc34/k0`** or only silicon KEYROM secrets?  
   - Scheme doc: “master keys wiped,” “Ko erased upon developer mode.”  
   - Implementation: keystore `is_developer` / chaff — **need to confirm whether PDDB dict `dc34` key `k0` survives.**  
   - If PDDB survives, **Chain 4 is the k0 dump path on a second stock badge** (enter boot1 without overwriting k0 via `test k0`, flash instrumented image that only *reads* PDDB — **but** loading developer-signed image may still set DEVELOPER_MODE and wipe Ko depending on policy).  
   - **Safe experiment:** read keystore source path for what is erased on developer transition before flashing anything valuable.

5. **Second unmodified badge**  
   - Never `test k0`.  
   - Capture mate oracle on serial.  
   - Only then consider instrumented firmware after wipe policy is clear.

---

## Code pointers (for re-audit)

```text
xous-core/bao1x-boot/boot1/src/repl.rs     # full command surface
xous-core/bao1x-boot/boot1/src/audit.rs    # identity / hash dump
xous-core/bao1x-boot/uf2send.py            # serial flash
xous-core/devkey/README.md + dev.key       # public dev signing
xous-core/README-baochip.md                # trust model
dc34-vault HandleQr                        # VULN-1 OOB, VULN-5 logs
dc34-console cmds/test.rs                  # k0 write, bootwait, proc
```

---

## Bottom line

| Goal | Reachable? | Path |
|------|------------|------|
| More serial dumps of app secrets | **Yes** | VULN-5 TOTP/QR/gene (no chip maker needed) |
| QR → bootloader shell | **Yes on this lab** | VULN-1 + **bootwait already true** |
| boot1 identity dump | **Yes** | `audit` after boot1 |
| Arbitrary code | **Yes** | Public devkey + UF2 (wipes chip secrets) |
| Factory population k0 via QR alone | **No** | — |
| Factory k0 via instrumented FW | **Maybe** | Only if PDDB k0 survives developer entry — **verify before burning second badge** |

The chip makers left a **rich factory/dev plane** (boot1 + public devkey + UF2 + audit). It is mostly **gated by physical USB + bootwait/PROG**, not by QR.  
Our QR work **does** reach that plane on a bootwait-enabled unit via **panic→reboot**, and separately maxes **application log exfil** over the same serial cable.
