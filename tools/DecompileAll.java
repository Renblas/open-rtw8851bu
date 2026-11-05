// Ghidra script: decompile every function to a .c file with an index.
// Arg 0 (optional): output .c path. Arg 1 (optional): output index path.
// Defaults = decompiled/wowlan_full.c + decompiled/index.txt.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.decompiler.DecompiledFunction;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

public class DecompileAll extends GhidraScript {
    public void run() throws Exception {
        String[] a = getScriptArgs();
        String base = "/home/renblas/Programming/open-rtw8851bu/decompiled";
        String cPath   = (a.length > 0) ? a[0] : base + "/wowlan_full.c";
        String idxPath = (a.length > 1) ? a[1] : base + "/index.txt";
        new File(cPath).getParentFile().mkdirs();
        BufferedWriter c   = new BufferedWriter(new FileWriter(cPath));
        BufferedWriter idx = new BufferedWriter(new FileWriter(idxPath));

        DecompInterface di = new DecompInterface();
        di.setOptions(new DecompileOptions());
        di.openProgram(currentProgram);

        FunctionManager fm = currentProgram.getFunctionManager();
        int total = fm.getFunctionCount();
        c.write("// Full decompilation of the rtw8851bu firmware image.\n");
        c.write("// " + total + " functions, base 0xb8970000, MIPS32 + MIPS16e.\n");

        int n = 0, ok = 0, fail = 0;
        FunctionIterator it = fm.getFunctions(true);
        while (it.hasNext() && !monitor.isCancelled()) {
            Function f = it.next();
            n++;
            String code;
            try {
                DecompileResults r = di.decompileFunction(f, 45, monitor);
                DecompiledFunction dfu = (r != null) ? r.getDecompiledFunction() : null;
                if (dfu != null && dfu.getC() != null) { code = dfu.getC(); ok++; }
                else { code = "// [decompile failed: " + (r != null ? r.getErrorMessage() : "null") + "]\n"; fail++; }
            } catch (Exception e) {
                code = "// [exception: " + e.getMessage() + "]\n"; fail++;
            }
            long sz = f.getBody().getNumAddresses();
            c.write("\n/* ===== " + f.getName() + " @ " + f.getEntryPoint() + "  (" + sz + " bytes) ===== */\n");
            c.write(code);
            c.flush();
            idx.write(f.getEntryPoint() + "  " + f.getName() + "  " + sz + "\n");
            if (n % 50 == 0) { idx.flush(); println("decompiled " + n + "/" + total + "  (ok=" + ok + " fail=" + fail + ")"); }
        }
        c.close(); idx.close();
        println("DECOMPILE DONE: " + n + " functions  ok=" + ok + " fail=" + fail);
    }
}
