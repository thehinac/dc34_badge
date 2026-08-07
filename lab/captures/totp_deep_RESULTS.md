# TOTP QR deep exploit session — live results (2026-08-07)

**k0 path:** none observed. (Policy: if found later → notify-first, no public post.)

**Log:** `totp_deep_exploit_live.log`  
**Mode:** Token (Password/Totp) — confirmed in `got qr data` lines.

---

## Confirmed live

### 1. Unauthenticated overwrite (same label)
PoC: `CVE-totp-overwrite-leak-demo.png`  
Prior entry `SERIAL:leak-demo@local` secret was `JBSWY3DPEHPK3PXP`.  
After scan serial shows:
```text
secret:ORBITOVERWRITESECRET99
name:SERIAL:leak-demo@local
notes:EVIL
```
**Impact:** Evil otpauth QR replaces victim TOTP under same account name (SHA256 key, `overwrite: true`).

### 2. Newline injection via `secret=` (CRLF/field injection)
PoC: `CVE-totp-inject-secret-newline.png`  
Stored/logged blob:
```text
secret:AAA
name:PWNED-INJECT
notes:INJECTED
name:InjectTest@local
…
```
Parser `push_str` on repeated tags → name/notes pollution.  
**Impact:** Integrity of TOTP records; possible display confusion; still no k0.

### 3. Newline injection via label
PoC: `CVE-totp-inject-label-newline.png`  
```text
secret:REALSECRETBASE32TEST
name:GoodLabel
secret:INJECTEDSECRET99
notes:X
…
```
Second `secret:` **appends** → effective secret becomes concatenation of both values.  
**Impact:** Broken codes + possible secret confusion; integrity issue.

### 4. Double `secret=` query param
PoC: `CVE-totp-double-secret-param.png`  
Stored: `secret:SECONDSECRETBBB` (last-wins HashMap).  
**Impact:** Attacker can hide first param from casual inspection of QR string order.

### 5. Colon in secret (UI split break)
PoC: `CVE-totp-secret-with-colons.png`  
`secret:AAAA:BBBB:CCCC:DDDD:EEEE` stored whole.  
UI `extra.split(':')` expects 5 fields → **broken TOTP code display** (DoS of that entry’s UX).

### 6. Absurd digits accepted
PoC: `CVE-totp-weird-digits-period.png`  
`digits:999999` `timestep:1` stored and re-logged on every reload.  
**Impact:** Logic/display weirdness; potential secondary bugs in code generation path.

### 7. HOTP enroll (counter ignored)
PoC: `CVE-totp-hotp-counter.png`  
```text
hotp:1 timestep:0 name:HotpTest@local
```
`counter=` not parsed by `from_uri` (only `period`); HOTP flag set from path `hotp/`.

### 8. Mass secret re-dump on every Totp reload — reconfirmed
Each subsequent QR in Totp mode re-ran `try_from` and re-logged **all** stored secrets (MFRA, leak-demo, Hotp, Inject, Weird, Colon, Double, Overwrite, …).

### 9. Minimal enroll
`otpauth://totp/x?secret=MFRA&…` enrolled fine.

---

## Not achieved / not scannable
- Huge 400-char secret / huge name: user said only ones that would scan — likely camera limits.
- **No k0 / dc34 dict / GlobalConfig leak** in any line.

---

## Severity ranking (new vs known)

| Finding | Severity | k0? | Publish? |
|---------|----------|-----|----------|
| Serial secret dump (VULN-5 L2) | High | No | Already public |
| Unauthenticated TOTP overwrite | **High** (auth integrity) | No | OK after optional ping |
| Newline field injection | Medium–High (integrity) | No | OK after optional ping |
| Colon UI break | Low–Med DoS | No | OK |
| Double secret last-wins | Low | No | OK |
| digits=999999 | Low | No | OK |

---

## Fixes (for authors)
1. Stop logging full TOTP records / QR payloads at Info.  
2. `overwrite: false` or user confirm on QR enroll.  
3. Reject `\n` / `:` / control chars in secret/name/notes; length caps.  
4. Validate base32 secret; clamp digits to 6–8; parse HOTP `counter`.  
5. Don’t put raw secret in `ListItem.extra` colon-delimited fields.
