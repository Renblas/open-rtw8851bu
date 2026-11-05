import sys
targets=[int(x,16) for x in sys.argv[1:]]
rows=[]
for ln in open("/home/renblas/Programming/open-rtw8851bu/decompiled/index.txt"):
    p=ln.split()
    if len(p)>=3:
        try: a=int(p[0],16); sz=int(p[2])
        except: continue
        rows.append((a,p[1],sz))
rows.sort()
for t in targets:
    hit=None
    for a,n,sz in rows:
        if a<=t<a+sz: hit=(a,n,sz); break
    print(f"0x{t:08x} -> {hit[1]} @ 0x{hit[0]:08x} (size {hit[2]})" if hit else f"0x{t:08x} -> (none)")
