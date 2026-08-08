# SPI hardware shopping + setup (DEF CON floor)

**Badge:** DC34 core module (`dc34-core-hw`)  
**Target IC:** external **SPI NOR flash** holding swap/PDDB (loader SPI TOCTOU)  
**Policy:** **LAB badge only** for write/TOCTOU. Virgin = photo/ID only, no clip write.

---

## 1 — What is on the board (from schematics)

Source: [bunnie/dc34-core-hw `memory.kicad_sch`](https://github.com/bunnie/dc34-core-hw/blob/main/memory.kicad_sch)

| Ref | Part | Role | Package |
|-----|------|------|---------|
| **U2** | **`ZD25Q64BSIGT`** | **64 Mbit (8 MiB) SPI NOR flash** — **THIS is the TOCTOU target** | **SOIC-8**, 1.27 mm pitch, footprint ~5.3×5.3 mm body |
| U1 / similar | `APS6404L-3SQR-SN` / IS66-class | SPI **PSRAM** (swap RAM), same bus family | Also **SOIC-8** — **do not clip this for flash dumps** |

Bus labels on the schematic (shared QSPI2):

- `QSPI2_SCK`
- `QSPI2_D0` … `QSPI2_D3` (quad SPI; SPI mode uses D0=MOSI, D1=MISO)
- `QSPI2_CS0_N` / `QSPI2_CS1_N` (flash vs RAM chip-selects)

**Standard SOIC-8 SPI flash pinout** (matches the symbol used on the sheet):

```text
        ___________
 CS#  1 |         | 8  VCC   (≈3.0–3.3 V on this design)
  SO  2 |  ZD25   | 7  HOLD# / IO3   (often pull-up)
 WP#  3 |  Q64    | 6  SCK
 GND  4 |_________| 5  SI / IO0
```

Marking to look for on silkscreen / chip top: **`ZD25` / `Q64` / similar** vs RAM (`APS` / `6404` / `IS66`).

Core module is **removable** (T6 on conversion kit path) — work on the **core**, not the big carrier if that is easier.

---

## 2 — Buy list (vendor hall / HHV — priority order)

### Must buy (minimum viable)

| # | Item | Why | What to ask for |
|---|------|-----|-----------------|
| 1 | **SOIC-8 test clip** | Non-solder attach to U2 | “**SOIC-8 Pomona-style clip**” / “**5250/5252 clip**” / “**8-pin SOP/SOIC programmer clip**” |
| 2 | **SPI flash programmer** | Read/write flash offline | **CH341A** (most common at cons) **or** any flashrom-friendly USB SPI dongle |
| 3 | **Dupont / jumper wires** F-F and M-F | Clip → programmer | Pack of 20+ |
| 4 | **Multimeter** | Continuity, VCC, don’t short | Any cheap DMM |

Prefer a CH341A kit that **already includes a SOIC-8 clip + adapter board** (one bag = items 1–3).

### Strongly recommended

| # | Item | Why |
|---|------|-----|
| 5 | **Logic analyzer** 8ch (Saleae clone / DSLogic / “24 MHz LA”) | Confirm CS/SCK during boot; time TOCTOU window |
| 6 | **Extra SOIC-8 clip** | Clips die; second is cheap insurance |
| 7 | **Breadboard + short solid core** | Strain relief so clip doesn’t torque the package |
| 8 | **USB power bank / second USB cable** | Power badge from one port, programmer/PC from another |
| 9 | **Kapton tape + flux pen + fine tip** | Only if you must tack wires (avoid if clip works) |
| 10 | **3.3 V USB–TTL serial** | You may already have CDC; still useful for LA-triggered serial |

### Optional / advanced (only if stocked)

| Item | Use |
|------|-----|
| **Bus Pirate v3/v4**, **FT232H**, **ESP32-S3** board | Scriptable SPI master for mid-boot inject (better than CH341 for race) |
| **Second cheap MCU board** (RP2040/Pico) | Dual-image interposer later |
| **Hot air / fine iron** | Last resort: fly-wires — **not first choice** |

### Do **not** buy / avoid

- **5 V-only** programmers without 3.3 V level select (can damage flash I/O).  
- **SOP-16 / TSOP** clips only (wrong package).  
- Clipping **PSRAM** “because SOIC-8” (wrong chip).  
- Anything that forces **desoldering** the flash for a first pass.

---

## 3 — Voltage rules

- Flash / QSPI I/O on this design is **~3.0–3.3 V** class (schematic notes 3.0 V I/O region).  
- Set CH341A / adapter to **3.3 V** if it has a jumper.  
- **Never** drive SPI pins at 5 V.  
- GND **must** be common between badge power and programmer.

---

## 4 — Floor setup procedure (do this order)

### Step 0 — Policy

1. Label badges: **LAB** vs **VIRGIN**.  
2. SPI work = **LAB only**.  
3. Have factory UF2 triple ready on laptop: `loader.uf2`, `xous.uf2`, `swap.uf2` from https://defcon.org/34b/ or your `factory-fw/extracted/`.

### Step 1 — Identify U2 on the **lab** core

1. Remove core module if needed (T6 / printed kit instructions).  
2. Find **two SOIC-8** parts on the core.  
3. Match top mark / silkscreen to **flash = ZD25Q64…** (U2).  
4. Photo both chips + pin-1 dot (send me photos if unsure).  
5. Pin 1 = CS# (dot / notch end).

### Step 2 — Clip dry-fit (power **off**)

1. Badge **unplugged**, battery out if possible.  
2. Align SOIC-8 clip: pin-1 wire / red mark to chip pin 1.  
3. Clip should sit flat; no pin bridged.  
4. Continuity check (optional): clip pin 4 → GND pad on board.

### Step 3 — Wire clip → CH341A (standard)

| Flash pin | Name | CH341A / SPI header |
|-----------|------|---------------------|
| 1 | CS# | CS |
| 2 | SO (MISO) | MISO / DO |
| 3 | WP# | **3.3 V** (or leave if board pulls up) |
| 4 | GND | GND |
| 5 | SI (MOSI) | MOSI / DI |
| 6 | SCK | CLK / SCK |
| 7 | HOLD# | **3.3 V** (or leave if pulled up) |
| 8 | VCC | **3.3 V** |

Many CH341 “SOP8” boards label the ZIF/clip footprint already — use that.

### Step 4 — First power / ID (passive success criteria)

**Goal:** prove you can **read** JEDEC ID of the flash. No TOCTOU yet.

**Windows options people use at cons:**

- `NeoProgrammer` / `AsProgrammer` with CH341  
- Or WSL/Linux laptop: `flashrom -p ch341a_spi`

Expected class of part: **64 Mbit NOR**, ID should not be blank/0xFF forever.

Record:

```text
JEDEC ID: __ __ __
Tool: ____
Photo of clip orientation: yes/no
```

**If ID fails:**

1. Swap pin-1 orientation 180° (most common).  
2. Confirm 3.3 V not 5 V.  
3. Confirm you are on **flash**, not PSRAM.  
4. Try powering flash from programmer **only** with badge unpowered (some boards allow; some fight).  
5. If badge must be powered: common GND, programmer CS only when CPU is held in reset if possible.

### Step 5 — Offline dump (lab)

Once ID works:

1. Dump full 8 MiB (or at least first 4 MiB swap region).  
2. Save as `lab_spi_full_before.bin`.  
3. Search for known strings / compare to factory `swap.uf2` payload layout offline later.

### Step 6 — Offline write restore test (lab, still not TOCTOU)

1. Re-flash **known-good** image back (or only rewrite a non-critical test page if you know offsets).  
2. Boot badge, confirm OS still lives.  
3. Only then plan mid-boot experiments.

### Step 7 — TOCTOU later (after dump works)

You will need **either**:

- scriptable SPI master (Bus Pirate / Pico / FT232H) while watching serial for  
  `Fresh swap image found` / `ed25519ph verification passed`, **or**  
- dual-boot: present factory swap for hash, then rewrite (hard post-rehash — see `SPI-TOCTOU-LAB-PLAN.md`).

**Do not start Step 7 until Step 4–6 work.** Clip reliability first.

---

## 5 — Exact “walk to the table and say”

> “I need a **CH341A SPI flash programmer kit with SOIC-8 clip**, extra **Dupont wires**, and a **multimeter**. Prefer **3.3 V** capable. If you have a **logic analyzer**, that too. SOIC-8 only — not TSOP.”

If they only have clip **or** only CH341, buy both separately.

Backup ask:

> “Any **SOIC-8 Pomona 5250/5252-style** test clip and an **FT232H** or **Bus Pirate**?”

---

## 6 — What to send me after purchase

1. Photo of **both SOIC-8** chips (markings readable).  
2. Photo of **clip on flash** (pin-1 visible).  
3. JEDEC ID / tool screenshot.  
4. Whether badge still boots with clip attached, power off, and power on.  
5. Which programmer you bought (CH341 / other).

I will then give the **exact** next command sequence (dump offsets, restore, then race plan).

---

## 7 — Safety (quick)

| Risk | Mitigation |
|------|------------|
| Wrong chip (RAM) | Markings + JEDEC; PSRAM ≠ ZD25 |
| 5 V fry | 3.3 V only |
| Lifted pins | Don’t force clip; support board; kapton |
| Brick lab | Factory UF2 ready; dump **before** any write |
| Virgin wipe / damage | **No SPI on virgin** |

---

## 8 — Reality check (honest)

- Clip + CH341 is enough for **L1**: dump/rewrite swap offline, prove fail-closed, map layout.  
- True **mid-boot SPI TOCTOU (E1)** may need a **scriptable** SPI master + serial timing; buy LA + Pico/Bus Pirate if you see them.  
- Even if TOCTOU stays hard, a full flash dump is still gold for analysis.

---

*Schematic refs: U2 `ZD25Q64BSIGT`, SOIC-8, QSPI2, dc34-core-hw.*
