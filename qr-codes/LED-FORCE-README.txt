DC34 LED COLOR FORCE — WALKTHROUGH
==================================

FINDING: Production firmware still has factory serial command:
  test k0 <base64(32-byte-key || crc32le(key))>

We confirmed K0.SUCCESS on your badge with key = 0x42 * 32.

CRITICAL SIDE EFFECTS of save_k0():
  - Replaces the shared conference key used for light mating
  - Resets badge type to None
  - After reboot you can forge your own colors, but cannot mate with
    normal badges until the original factory k0 is restored (we cannot
    recover the old key from here)

STEPS TO FORCE LED COLORS
-------------------------
1. (Already done if you ran our probe) Install known key:
   python forge_led_gene.py install-key --port COM18 --key 0x42

2. POWER-CYCLE the badge (vault only reloads k0 from PDDB at boot).

3. Press LEFT or RIGHT so the badge shows the phase-1 nonce QR.

4. Decode that QR (any phone QR app → copy the text string; it is base45):
   python forge_led_gene.py decode-phase1 --b45 "PASTE_HERE"

5. Forge a gene response QR bound to that nonce:
   python forge_led_gene.py forge --nonce-b45 "PASTE_HERE" --preset rainbow -o gene.png
   Presets: red | rainbow | uber-red | cyan | magenta

6. On the badge, scan gene.png (middle button / camera) as if it were
   a donor's light pattern. Keep/confirm the new gene.

7. LEDs should update to the blended phenotype (your egg meiosis + forged sperm).

WHY THIS WORKS
--------------
- LED colors come from light genes, not free serial color commands.
- Gene QR path is the intended write path: AES-GCM-SIV + base45.
- Auth is only the shared k0. Factory left k0 writable over USB serial.
- After you own k0, you are a "seeder" for arbitrary patterns (as bunnie's
  scheme doc predicted for key compromise).

WHAT DID NOT WORK
-----------------
- Production builds strip test hue/mate/transmute/force serial commands.
- BIO upload cannot claim the LED data pin (only SAO pins 21/22/30/31).
- Crash QRs panic; they do not recolor LEDs.

DEMO PNGs with fake nonce (will NOT work until nonce matches your badge):
  forged-*-DEMO.png
