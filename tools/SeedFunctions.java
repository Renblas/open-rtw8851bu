// Ghidra post-script (Java): map the firmware's function-pointer table into real functions.
// Loads the data section, reads the code pointers it holds, and creates a function at each
// (ISA_MODE=1 for MIPS16e targets, =0 for MIPS32), then re-analyzes.
// Arg 0 (optional): path to the data section .bin. Default = WoWLAN cv2 data.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import java.io.ByteArrayInputStream;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;
import java.util.TreeMap;

public class SeedFunctions extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        String dataPath = (a.length > 0) ? a[0] :
            "/home/renblas/Programming/open-rtw8851bu/firmware/WOWLAN_cv2_sec1_data1_load0x18e12c00.bin";
        long DATA_BASE = 0xb8e12c00L;
        long CODE_LO = 0xb8970000L;

        Memory mem = currentProgram.getMemory();
        MemoryBlock codeBlk = mem.getBlock(toAddr(CODE_LO));
        long CODE_HI = codeBlk.getEnd().getOffset() + 1;   // derive from the loaded code block
        println("code range: 0x" + Long.toHexString(CODE_LO) + " .. 0x" + Long.toHexString(CODE_HI));

        byte[] raw = Files.readAllBytes(Paths.get(dataPath));
        if (mem.getBlock(toAddr(DATA_BASE)) == null) {
            mem.createInitializedBlock("data", toAddr(DATA_BASE),
                new ByteArrayInputStream(raw), raw.length, monitor, false);
            println("added data block: " + raw.length + " bytes @ 0x" + Long.toHexString(DATA_BASE));
        }

        TreeMap<Long,Integer> targets = new TreeMap<>();
        for (int i = 0; i + 4 <= raw.length; i += 4) {
            long w = (raw[i]&0xffL) | ((raw[i+1]&0xffL)<<8) | ((raw[i+2]&0xffL)<<16) | ((raw[i+3]&0xffL)<<24);
            long t = w & ~1L;
            if (t >= CODE_LO && t < CODE_HI) targets.put(t, (int)(w & 1));
        }
        println("candidate function targets: " + targets.size());

        Register isa = currentProgram.getProgramContext().getRegister("ISA_MODE");
        println("ISA_MODE register: " + (isa != null ? "found" : "NOT FOUND"));

        int made = 0;
        for (Map.Entry<Long,Integer> e : targets.entrySet()) {
            Address addr = toAddr(e.getKey());
            try {
                if (isa != null)
                    currentProgram.getProgramContext().setValue(isa, addr, addr,
                        BigInteger.valueOf(e.getValue() == 1 ? 1 : 0));
                disassemble(addr);
                if (getFunctionAt(addr) == null) createFunction(addr, null);
                if (getFunctionAt(addr) != null) made++;
            } catch (Exception ex) { /* skip bad targets */ }
        }
        println("functions created/confirmed: " + made);
        analyzeChanges(currentProgram);
        println("TOTAL functions now: " + currentProgram.getFunctionManager().getFunctionCount());
    }
}
