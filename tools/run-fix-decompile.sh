#!/bin/bash
# Open wowlan-full, set RETURN overrides on the MIPS16e temp-register returns, then
# re-decompile everything cleanly.
export JAVA_HOME=/opt/openjdk-bin-21
export PATH="$JAVA_HOME/bin:$PATH"
G=/home/renblas/ghidra-re/ghidra_12.1.4_PUBLIC
P=/home/renblas/Programming/open-rtw8851bu
echo "[$(date +%T)] FixReturns + re-decompile ..."
"$G/support/analyzeHeadless" "$P/ghidra-projects" wowlan-full \
  -process "WOWLAN_cv2_sec0_code0_load0x18970000.bin" -noanalysis \
  -scriptPath "$P/tools" -postScript FixReturns.java -postScript DecompileAll.java \
  2>&1 | grep -iE 'FixReturns:|decompiled [0-9]|DECOMPILE DONE|Exception|ERROR|error:' | tail -30
echo "[$(date +%T)] fix-decompile done"
