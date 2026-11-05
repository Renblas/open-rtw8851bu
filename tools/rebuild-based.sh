#!/bin/bash
# Rebuild the WoWLAN code image in Ghidra at its TRUE base 0x08970000, so jalx calls
# resolve and the MIPS16e bulk gets decoded. Headless analyzeHeadless; saves a new project.
export JAVA_HOME=/opt/openjdk-bin-21
export PATH="$JAVA_HOME/bin:$PATH"
G=/home/renblas/ghidra-re/ghidra_12.1.4_PUBLIC
P=/home/renblas/Programming/open-rtw8851bu
PROJDIR="$P/ghidra-projects"
BIN="$P/firmware/WOWLAN_cv2_sec0_code0_load0x18970000.bin"
rm -rf "$PROJDIR/wowlan-based.gpr" "$PROJDIR/wowlan-based.rep" 2>/dev/null
echo "[$(date +%T)] analyzeHeadless import at base 0x08970000 ..."
"$G/support/analyzeHeadless" "$PROJDIR" wowlan-based \
  -import "$BIN" \
  -loader BinaryLoader -loader-baseAddr 0x08970000 \
  -processor "MIPS:LE:32:default" -cspec default \
  -analysisTimeoutPerFile 1200 \
  2>&1 | grep -viE 'WARN |^(INFO)? *$' | tail -40
echo "[$(date +%T)] done. functions in project:"
