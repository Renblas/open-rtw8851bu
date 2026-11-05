# Ghidra post-script: map the firmware's function-pointer table into real functions.
# Adds the data section, reads the ~419 code pointers it holds, and creates a function at
# each (ISA_MODE=1 for MIPS16e targets, =0 for MIPS32), then re-analyzes.
import struct
from java.io import FileInputStream
from java.math import BigInteger

DATA_PATH = "/home/renblas/Programming/open-rtw8851bu/firmware/WOWLAN_cv2_sec1_data1_load0x18e12c00.bin"
DATA_BASE = 0xb8e12c00
CODE_LO   = 0xb8970000
CODE_HI   = 0xb89aebb8

mem = currentProgram.getMemory()

# 1. map the data section (holds the pointer table) if not already present
if mem.getBlock(toAddr(DATA_BASE)) is None:
    raw = open(DATA_PATH, "rb").read()
    fis = FileInputStream(DATA_PATH)
    mem.createInitializedBlock("data", toAddr(DATA_BASE), fis, len(raw), monitor, False)
    fis.close()
    print("added data block: %d bytes @ 0x%08x" % (len(raw), DATA_BASE))

# 2. collect code pointers from the data bytes (mask MIPS16 bit0; remember it)
raw = open(DATA_PATH, "rb").read()
targets = {}
for i in range(0, len(raw) - 3, 4):
    w = struct.unpack_from("<I", raw, i)[0]
    t = w & ~1
    if CODE_LO <= t < CODE_HI:
        targets[t] = (w & 1)
uniq = sorted(targets.keys())
print("candidate function targets: %d" % len(uniq))

# 3. seed a function at each target with the correct ISA mode
ctx = currentProgram.getProgramContext()
isa = ctx.getRegister("ISA_MODE")
print("ISA_MODE register: %s" % ("found" if isa is not None else "NOT FOUND"))
made = 0
for t in uniq:
    a = toAddr(t)
    try:
        if isa is not None:
            ctx.setValue(isa, a, a, BigInteger.valueOf(1 if targets[t] else 0))
        disassemble(a)
        if getFunctionAt(a) is None:
            createFunction(a, None)
        if getFunctionAt(a) is not None:
            made += 1
    except Exception as e:
        pass
print("functions created/confirmed: %d" % made)

# 4. re-analyze so the decompiler and references catch up
analyzeChanges(currentProgram)
print("TOTAL functions now: %d" % currentProgram.getFunctionManager().getFunctionCount())
