#!/bin/bash
# Build the full project: code@0xb8970000 + data@0xb8e12c00, seed the 419 pointer-table
# functions (SeedFunctions.java), re-analyze. New project: wowlan-full.
export JAVA_HOME=/opt/openjdk-bin-21
export PATH="$JAVA_HOME/bin:$PATH"
G=/home/renblas/ghidra-re/ghidra_12.1.4_PUBLIC
P=/home/renblas/Programming/open-rtw8851bu
PROJDIR="$P/ghidra-projects"
BIN="$P/firmware/WOWLAN_cv2_sec0_code0_load0x18970000.bin"
rm -rf "$PROJDIR/wowlan-full.gpr" "$PROJDIR/wowlan-full.rep" 2>/dev/null
echo "[$(date +%T)] import @0xb8970000 + seed pointer-table functions ..."
"$G/support/analyzeHeadless" "$PROJDIR" wowlan-full \
  -import "$BIN" \
  -loader BinaryLoader -loader-baseAddr 0xb8970000 \
  -processor "MIPS:LE:32:default" -cspec default \
  -scriptPath "$P/tools" -postScript SeedFunctions.java \
  -analysisTimeoutPerFile 2400 \
  2>&1 | grep -iE 'data block|candidate|ISA_MODE|functions (created|now)|REPORT|Exception|ERROR' | tail -30
echo "[$(date +%T)] rebuild-full done"
