# Findings — open-rtw8851bu

All dates 2026. This file is the technical record. The newest work is at the bottom.

## 1. Firmware container format

`rtw8851b_fw.bin` is a multi-firmware (MFW) container: signature `0xFF`, 5 sub-firmwares.

| # | Image | Purpose | Code size |
|---|-------|---------|-----------|
| 0 | NORMAL_CE (rev 0) | normal operation | ~278 KiB |
| 1 | NORMAL_CE (rev 1) | normal, other silicon cut | ~278 KiB |
| 2 | WOWLAN (rev 0) | runs while the host sleeps | ~263 KiB |
| 3 | WOWLAN (rev 1) | WoWLAN, other silicon cut | ~263 KiB |
| 4 | LOGFMT | debug format-string table | 51 KiB |

Each sub-firmware: a 32-byte header, then `sec_num` 16-byte section headers, then a dynamic
header, then the section payloads at `shift + hdr_len` (hdr_len = 144 here). Sections: a big
code section (type 2) at load address `0xb8970000`, a small data section (type 1) at
`0xb8e12c00`, and a 960-byte signature section (type 9). The real load address is
`section.w0 & 0x1fffffff`; the code's own pointers use the full `0xB8xxxxxx` form.

## 2. CPU architecture — MIPS32 LE (confirmed)

The entry stub decodes as plain MIPS32, little-endian:

- `27bdffd8` = `addiu sp, sp, -40`
- `afbf0024` = `sw ra, 0x24(sp)`
- `3c02b8e1` = `lui v0, 0xb8e1`
- `0040f809` = `jalr v0` (with a delay slot)

Confirmed with `rz-asm` and Ghidra. The entry is a C runtime: it clears a BSS region from
`0xb8e15ae0` and calls `main` through a pointer. Likely a Realtek RLX/Lexra MIPS core.

## 3. Secure boot — OFF (the chip runs unsigned firmware)

The `rtw89` driver reads two OTP bytes at efuse `0x5EC`. Both `0xFF` means no secure-boot keys.
The running kernel has `CONFIG_RTW89_DEBUGMSG` and `DEBUGFS` off, so the value does not print.
To read it, a 2-line `pr_info` patch was added to `rtw89_efuse_read_fw_secure_ax`, the `rtw89`
modules were rebuilt module-only (GCC 15, `KBUILD_MODPOST_WARN=1`, MODVERSIONS off), and loaded.

Result: `efuse[0x5EC..0x5ED] = 0xFF 0xFF` -> `secure_boot = false`. The chip accepts modified,
unsigned firmware. (The patched module reverts to the stock one on reboot.)

## 4. Code structure — position-independent, with a function-pointer table

The code calls through a pointer table: `lw vN, -off(vN); jalr vN`. Direct calls (`jal`) are
rare. So recursive-descent analysis (rizin `aa`/`aac`, Ghidra default) stalls at the first
indirect call and finds almost no functions. Example: `FUN_00024714` (decompiled in Ghidra) is
a real event handler — it reads hardware register `0x8104`, loops over its bits, and dispatches
2-byte messages through pointers at `0xb8e09xxx`. These pointers live in the data region, which
is not yet mapped in the project.

## 5. The timer / wake subsystem (from LOGFMT strings)

`LOGFMT.bin` holds 1073 format strings. These name the exact code the self-wake needs:

- `Gtimer test, <id>, <mode>, <unit>, <duration>` — a general-purpose timer.
- `PStimer test, <band>, <id>, <mode>, <tsf>` — a power-save timer, keyed to the TSF
  (the chip's microsecond clock).
- `WDT_timer start ...`, `Deauth wake up!`, `Wowlan rekey ...`.

So the chip already has timer facilities that run during host sleep (in the WoWLAN image).
The wake idea is to arm one of these for ~30 minutes and raise a USB remote-wakeup.

## 6. Ghidra MCP — installed and working

GhidraMCP 2.0, headless (PyGhidra, no GUI), on Ghidra 12.1.4 + JDK 21. The MCP server exposes
28 tools (`get_program_info`, `list_functions`, `decompile_function_by_address`,
`disassemble_function`, `get_xrefs_to/from`, `list_strings`, ...). `get_program_info` returns:
Raw Binary, `MIPS:LE:32:default`, LE, image base 0, size 256952, 3 functions found.

Open question: only 3 functions auto-found. The cause is the position-independent calls (sect. 4),
not certainly a compressed ISA — at least `FUN_00024714` is clean MIPS32. Whether the bulk is
MIPS32 (with data interspersed) or microMIPS is **not settled**; a re-import with
`--language MIPS:LE:32:micro` and a function-count compare is the test to run.

## Next steps

1. Settle the ISA question: re-analyze as microMIPS, compare function count to the default run.
2. Map the data section (`0xb8e12c00`) and the pointer table region (`0xb8e09xxx`) into the
   Ghidra project, so indirect calls and data references resolve.
3. Raise function coverage: seed functions at MIPS prologues across the code, or use a Ghidra
   analysis script, since the PIC pattern blocks auto-discovery.
4. Find the `Gtimer`/`PStimer` arm functions and the host-sleep entry (use the LOGFMT strings
   as landmarks).
5. Design the 30-minute self-wake, repack the WoWLAN section (fix the checksum; no signature
   needed), and test.

Boundary held throughout: no help with defeating RF regulatory limits (power/frequency).

## 7. Full map (2026-10-27)

Real base is 0xb8970000 (KSEG1), not 0x08970000. The data section (0xb8e12c00) holds the
firmware's 419-entry function-pointer table (396 MIPS16e) AND its source-file names (assert
strings). Seeding functions at the pointer table + re-analysis -> 973 functions (project
ghidra-projects/wowlan-full). Modules found by xref to their filename string:
- TIMER: HAL8851B_Timer_RAM.c -> b8978738/a20/c08/df8/fec
- Sleep/wake: WlanComm_RPWM_CPWM_RAM.c -> rpwm_cpwm_handler @ b89a535c, b89a5424
- WoWLAN: WlanComm_WoWLAN_RAM.c -> b89a94b0/9638/b5e8/c60c/c8bc
rpwm_cpwm_handler reads the host RPWM word; on a sleep request (bit 0x100) it enters the
sleep/WoWLAN path (FUN_b899f038); else it sets the power mode and acks via CPWM. Named
primitives: p_read_rpwm @b8e09984, p_ack_cpwm @b8e0997c, p_set_power_mode @b8e09980,
p_timer_read @b8e09474. NEXT: trace FUN_b899f038 (sleep entry) and the host-wake raise;
find the timer-arm API; design the 30-min self-wake.

## 8. Timer-arm API decoded (2026-10-27) — injection linchpin

HAL timer module (HAL8851B_Timer_RAM.c). Three near-identical arm functions, one per timer
channel (differ only in the alloc id 0xf103000{2,3,4}):
  FUN_b8978c08 (id ...04), FUN_b8978df8 (id ...03), FUN_b8978fec (id ...02)

Signature (from FUN_b8978c08):
  arm_timer(int idx{2,3}, uint mode{0,1}, int periodic, uint duration28,
            void* callback, void* cb_arg)
  - validates idx in {2,3}, mode in {0,1}
  - allocs/zeroes a 0x40-byte timer block (via _DAT_b8e09474(0x40, id) + _DAT_b8e09e80 memset)
  - stores callback (param_5) + cb_arg (param_6) as 8 bytes in the per-idx entry (idx*0x10)
  - control word = (mode? 0xe0000000 : 0xa0000000) | (duration & 0x0fffffff)
                   | (periodic? 0x10000000 : 0)
  - writes it to the timer hw register via _DAT_b8e094c8(timer_reg[idx], ctrl)
  => arms a one-shot/periodic HW timer that calls `callback(cb_arg)` on fire.
FUN_b8978738 does a 64-bit duration compare vs 1800000000 (range/unit boundary).
OPEN: the timer tick unit (duration field is 28 bits; mode bit picks the unit). Need this to
size a 30-min wait (may chain timers). NEXT: find the host-wake primitive (what the callback
must do to raise a USB remote-wakeup / signal the host), then design the injection.
Primitives seen: _DAT_b8e09474 (timer-block alloc/read), _DAT_b8e094c8 (reg write),
_DAT_b8e09e80 (memset), _DAT_b8e09118 (assert).

## 9. Jumptable resolution (2026-10-27) — #1

The 1005 UNRECOVERED_JUMPTABLE / 504 "could not recover jumptable" were NOT broken calls:
MIPS16e functions here return by restoring the saved return address into a temp register and
doing `jr <reg>` (prologue `sw ra,X(sp)`; epilogue `lw a3,X(sp); jr a3; addiu sp,N`). Ghidra only
treats `jr ra` as a return. tools/FixReturns.java sets FlowOverride.RETURN on every `jr`/`jrc`
whose target reg was restored from the stack: 705 fixed across 973 funcs. Result:
UNRECOVERED_JUMPTABLE 1005->0, real switches 504->2, decompile 40,489->38,519 lines, all 973
functions decompile cleanly. The decompile (decompiled/wowlan_full.c) is now correct and readable.
NOT a jumptable issue: indirect CALLS go through the 0xb8e09xxx primitive table (ISR dispatcher
reads handlers from base 0xb8e09000; only 7 writes to that region exist, all data vars) -> the
table is ROM-resident / loader-populated, not in our image. Those primitives are named by behavior
(read_mac_reg @b8e094d4, write_mac_reg @b8e094c8, fw_send_msg @b8e092f4, ack_cpwm @b8e0997c,
set_power_mode @b8e09980, read_rpwm @b8e09984, timer_read @b8e09474, assert @b8e09118, memset
@b8e09e80). NEXT: trace the wake path by behavioral inference; find the USB-remote-wakeup trigger.

## 10. Whole firmware decompiled (2026-11-05)

Ran the same pipeline (SeedFunctions + FixReturns + DecompileAll, parameterized) on the NORMAL_CE
image. Project normal-full (code @0xb8970000, data @0xb8e12c00). 444 pointer-table seeds cascaded
to 1121 functions; 793 MIPS16e returns fixed; 1121/1121 decompiled, 0 fail, 0 UNRECOVERED_JUMPTABLE.
Output: decompiled/normal_full.c (43,949 lines) + normal_index.txt. Both functional images are now
decompiled: WoWLAN 973 (wowlan_full.c) + NORMAL_CE 1121 (normal_full.c). NORMAL adds modules absent
from the stripped WoWLAN image: BTC8851B_BTCoex, HAL8851B_HCI/GPIO/EFUSE/MAC_TX/PPS, Intl8851B_
C2HPKT/H2CPKT/MCC/P2P/ScanOfld/STA_Role/FWOfld/PKTOfld, RF8851B_RFComm_API, Wlan8851B_Beacon/Csi/
TWT/Power_Ctrl. cv1 (NORMAL) and cv3 (WoWLAN) are alternate silicon-cut builds, near-identical, not
decompiled. LOGFMT is a string table, not code.
