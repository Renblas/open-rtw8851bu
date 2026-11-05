import struct, sys, collections
P="/home/renblas/Programming/open-rtw8851bu/firmware"
CODE=P+"/WOWLAN_cv2_sec0_code0_load0x18970000.bin"
DATA=P+"/WOWLAN_cv2_sec1_data1_load0x18e12c00.bin"
LO, HI = 0x08970000, 0x089aebb8   # code range (base .. base+size)
def scan(path, base):
    b=open(path,"rb").read()
    hits=[]
    for i in range(0, len(b)-3, 4):
        w=struct.unpack_from("<I", b, i)[0]
        t=w & ~1                      # clear MIPS16 bit0
        if LO <= t < HI:
            hits.append((base+i, w, w & 1))
    return b, hits
cb, chits = scan(CODE, 0x08970000)
db, dhits = scan(DATA, 0x08e12c00)   # note: our data sec loads at 0xb8e12c00; low 0x08e12c00 alias
print(f"code image: {len(chits)} words point into code range")
print(f"data image: {len(dhits)} words point into code range")
allt = [h[1]&~1 for h in chits] + [h[1]&~1 for h in dhits]
uniq = sorted(set(allt))
m16 = sum(1 for h in chits+dhits if h[2])
print(f"unique targets: {len(uniq)}   (with MIPS16 bit0 set: {m16} of {len(chits)+len(dhits)})")
# contiguous pointer-array runs in the code image (>=8 consecutive pointer words)
runs=[]; start=None; last=None
for (addr,w,bit) in chits:
    if last is not None and addr-last==4: 
        pass
    else:
        if start is not None and (last-start)>=28: runs.append((start,last))
        start=addr
    last=addr
if start is not None and (last-start)>=28: runs.append((start,last))
print(f"pointer-array runs in code (>=8 entries): {len(runs)}")
for s,e in runs[:12]: print(f"   table @0x{s:08x}..0x{e:08x}  ({(e-s)//4+1} ptrs)")
# save unique targets for the seeder
open("/home/renblas/Programming/open-rtw8851bu/tools/fn_targets.txt","w").write("\n".join(f"0x{t:08x}" for t in uniq))
print(f"wrote {len(uniq)} targets -> tools/fn_targets.txt")
