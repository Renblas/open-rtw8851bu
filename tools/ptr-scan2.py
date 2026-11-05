import struct
P="/home/renblas/Programming/open-rtw8851bu/firmware"
imgs={"code":(P+"/WOWLAN_cv2_sec0_code0_load0x18970000.bin",),
      "data":(P+"/WOWLAN_cv2_sec1_data1_load0x18e12c00.bin",)}
SIZE=0x3ebb8
cands=[0x08970000,0xb8970000,0x98970000,0x18970000,0x08970001,0xb8970001]
# count words (in both images) that fall within [base, base+SIZE) for each candidate base (mask bit0)
for name,(path,) in imgs.items():
    b=open(path,"rb").read()
    words=[struct.unpack_from("<I",b,i)[0] for i in range(0,len(b)-3,4)]
    print(f"== {name} ({len(words)} words) ==")
    for base in cands:
        base0=base & ~1
        hits=[w for w in words if base0 <= (w & ~1) < base0+SIZE]
        if hits:
            odd=sum(1 for w in hits if w&1)
            print(f"   base 0x{base0:08x}: {len(hits):5d} hits  (odd/MIPS16: {odd})")
    # also: what ranges do the large word values cluster in? show top value prefixes
    from collections import Counter
    pref=Counter((w>>24) for w in words if w>0x01000000)
    print("   top byte histogram (value>>24):", dict(sorted(pref.items(), key=lambda x:-x[1])[:6]))
