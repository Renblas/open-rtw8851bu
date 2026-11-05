# open-rtw8851bu

Reverse-engineering of the **TP-Link Archer TX10UB Nano** USB Wi-Fi adapter firmware
(Realtek **RTL8851BU**, Linux driver `rtw89_8851bu`).

Leaving source here, and putting my changes on a separate branch.

## Status

The two functional firmware images are fully decompiled and clean:

| Image | Functions | Decompiled source | Role |
|-------|-----------|-------------------|------|
| NORMAL_CE | 1121 | `decompiled/normal_full.c` | normal operation |
| WoWLAN    | 973  | `decompiled/wowlan_full.c` | runs while the host sleeps |

The injection (the self-wake patch) is not done. The timer-arm API and the sleep/wake handshake
are located; the remaining piece is the USB-remote-wakeup trigger. See `docs/FINDINGS.md`.

## Key facts (see docs/FINDINGS.md for the full record)

- **MCU:** MIPS32 + MIPS16e, little-endian (Realtek RLX/Lexra). True base `0xb8970000`.
- **Secure boot: OFF.** The OTP at `0x5EC` reads `0xFF 0xFF`, so the chip runs unsigned firmware.
- **Structure:** position-independent; calls go through a ROM-resident primitive table at
  `0xb8e09xxx` (named by behavior). The data section holds a function-pointer table (used to seed
  the function set) and the firmware's own source-file names (used to map modules).
- **Timer-arm API:** `arm_timer(idx, mode, periodic, duration, callback, cb_arg)`
  (`FUN_b8978c08` and siblings) — the hook for the self-wake.
- **Sleep/wake:** `rpwm_cpwm_handler` (`FUN_b89a535c`) is the host↔chip power handshake; the host
  enables USB remote-wakeup before suspend, and the chip issues it on a wake event.

## Repository layout

- `decompiled/` — the full decompiled C of both images, plus index files (address → name → size).
- `firmware/` — the firmware sections extracted from the container, and `original/` (the full
  `rtw8851b_fw.bin`). `*_sec0_code0_*` load at `0xb8970000`; `*_sec1_data1_*` at `0xb8e12c00`.
- `docs/FINDINGS.md` — the technical record (sections 1–10).
- `docs/live-trace.md` — an annotated walk through the first functions.
- `tools/` — the analysis and build scripts (see below).
- `PROGRESS.log` — a dated, one-line-per-step journal of the whole effort.

Not in git (regenerable or re-downloadable): `ghidra-projects/` (rebuild with the scripts below),
`third_party/ghidra-mcp/` (GhidraMCP 2.0 extension + wheel).

## Tools and how to rebuild the Ghidra projects

Dependencies: Ghidra 12.1.4 (`GHIDRA_INSTALL_DIR`), JDK 21 (`JAVA_HOME`), and — for the live MCP
query server — `uv` plus the GhidraMCP 2.0 extension.

- `tools/fwextract.py`, `fwparse.py` — split the firmware container into sections.
- `tools/SeedFunctions.java` — create functions from the pointer table (arg: data `.bin` path).
- `tools/FixReturns.java` — relabel MIPS16e temp-register returns as returns (not jumptables).
- `tools/DecompileAll.java` — decompile every function (args: output `.c` and index paths).
- `tools/rebuild-full.sh` / `tools/rebuild-normal.sh` — one-pass pipeline per image.
- `tools/serve-full.sh` + `tools/mcpcli.py` — serve a project over the GhidraMCP HTTP interface
  and query it from the shell.

Rebuild example (WoWLAN): `bash tools/rebuild-full.sh`.

## Note

This is reverse-engineering of proprietary Realtek firmware for interoperability (a self-wake
feature on hardware the owner controls). The firmware binaries are Realtek's. This repository is a
private working archive, not a redistribution.
