import sys,json,subprocess
addr=sys.argv[1]; tail=int(sys.argv[2]) if len(sys.argv)>2 else 0
out=subprocess.run(["python3","-I","mcpcli.py","disassemble_function",json.dumps({"address":addr,"limit":600})],capture_output=True,text=True).stdout
d=json.loads(out); items=d["items"]
sel=items[-tail:] if tail else items
for it in sel:
    print("  %s  %-12s %s" % (it["address"], it["bytes"], it["instruction"]))
print("  (total %d instructions)" % len(items))
