import sys,json,subprocess
addr=sys.argv[1]
out=subprocess.run(["python3","-I","mcpcli.py","get_xrefs_to",json.dumps({"address":addr,"limit":80})],capture_output=True,text=True).stdout
d=json.loads(out)
seen={}
for it in d.get("items",[]):
    f=it.get("from_function")
    if f: seen[f["address"]]=f["name"]
for a,n in sorted(seen.items()): print("  ",a,n)
print("  -> %d functions in this module"%len(seen))
