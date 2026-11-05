#!/bin/bash
# Full pipeline for the NORMAL_CE image: import @0xb8970000, seed pointer-table functions,
# fix MIPS16e returns, decompile all -> decompiled/normal_full.c. New project: normal-full.
export JAVA_HOME=/opt/openjdk-bin-21
export PATH="$JAVA_HOME/bin:$PATH"
G=/home/renblas/ghidra-re/ghidra_12.1.4_PUBLIC
P=/home/renblas/Programming/open-rtw8851bu
PROJDIR="$P/ghidra-projects"
CODE="$P/firmware/NORMAL_CE_cv0_sec0_code0_load0x18970000.bin"
DATA="$P/firmware/NORMAL_CE_cv0_sec1_data1_load0x18e12c00.bin"
rm -rf "$PROJDIR/normal-full.gpr" "$PROJDIR/normal-full.rep" 2>/dev/null
echo "[$(date +%T)] NORMAL_CE: import + seed + fix-returns + decompile ..."
"$G/support/analyzeHeadless" "$PROJDIR" normal-full \
  -import "$CODE" \
  -loader BinaryLoader -loader-baseAddr 0xb8970000 \
  -processor "MIPS:LE:32:default" -cspec default \
  -scriptPath "$P/tools" \
  -postScript SeedFunctions.java "$DATA" \
  -postScript FixReturns.java \
  -postScript DecompileAll.java "$P/decompiled/normal_full.c" "$P/decompiled/normal_index.txt" \
  -analysisTimeoutPerFile 2400 \
  2>&1 | grep -iE 'code range|candidate|ISA_MODE|functions (created|now)|FixReturns:|decompiled [0-9]|DECOMPILE DONE|REPORT|Exception|ERROR|error:' | tail -40
echo "[$(date +%T)] rebuild-normal done"
