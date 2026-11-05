#!/bin/bash
# Open the existing wowlan-full project (no re-analysis) and decompile every function.
export JAVA_HOME=/opt/openjdk-bin-21
export PATH="$JAVA_HOME/bin:$PATH"
G=/home/renblas/ghidra-re/ghidra_12.1.4_PUBLIC
P=/home/renblas/Programming/open-rtw8851bu
echo "[$(date +%T)] decompiling all functions from wowlan-full ..."
"$G/support/analyzeHeadless" "$P/ghidra-projects" wowlan-full \
  -process "WOWLAN_cv2_sec0_code0_load0x18970000.bin" -noanalysis \
  -scriptPath "$P/tools" -postScript DecompileAll.java \
  2>&1 | grep -iE 'decompiled [0-9]|DECOMPILE DONE|Exception|ERROR|error:' | tail -40
echo "[$(date +%T)] run-decompile-all finished"
