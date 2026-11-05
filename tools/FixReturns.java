// Ghidra script: MIPS16e functions return via a temp register (e.g. "lw a3,X(sp); jr a3"),
// which Ghidra mislabels as an unrecovered jumptable. Set FlowOverride.RETURN on every such
// jr whose target register was restored from the stack (the saved return address).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.FlowOverride;
import ghidra.program.model.lang.Register;
import java.util.ArrayList;
import java.util.List;

public class FixReturns extends GhidraScript {
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        int fixed = 0, funcs = 0;
        for (Function f : fm.getFunctions(true)) {
            if (monitor.isCancelled()) break;
            funcs++;
            List<Instruction> ins = new ArrayList<>();
            InstructionIterator it = listing.getInstructions(f.getBody(), true);
            while (it.hasNext()) ins.add(it.next());
            for (int i = 0; i < ins.size(); i++) {
                Instruction in = ins.get(i);
                String m = in.getMnemonicString();
                if (!m.equals("jr") && !m.equals("jrc")) continue;
                Register tgt = in.getRegister(0);
                if (tgt == null) continue;
                boolean isReturn = false;
                for (int j = i - 1; j >= 0 && j >= i - 8; j--) {
                    Instruction p = ins.get(j);
                    if (p.getMnemonicString().equals("lw")) {
                        Register d = p.getRegister(0);
                        if (d != null && d.equals(tgt)) {
                            String rep = p.getDefaultOperandRepresentation(1);
                            if (rep != null && rep.contains("sp")) { isReturn = true; break; }
                        }
                    }
                }
                if (isReturn && in.getFlowOverride() != FlowOverride.RETURN) {
                    in.setFlowOverride(FlowOverride.RETURN);
                    fixed++;
                }
            }
        }
        println("FixReturns: set RETURN on " + fixed + " jr instructions across " + funcs + " functions");
    }
}
