import struct, os
data=open("/lib/firmware/rtw89/rtw8851b_fw.bin","rb").read()
OUT="/home/renblas/.local/share/hw-advisor/fw-sections"
FWTYPE={1:"NORMAL",3:"WOWLAN",5:"NORMAL_CE",64:"BBMCU0",65:"BBMCU1",255:"LOGFMT"}
def g(v,hi,lo): return (v>>lo)&((1<<(hi-lo+1))-1)
fw_nr=data[1]
subs=[]
off=16
for i in range(fw_nr):
    typ=data[off+1]; shift,size=struct.unpack_from("<II",data,off+4); off+=16
    subs.append((typ,shift,size))
for idx,(typ,shift,size) in enumerate(subs):
    if typ not in (1,3,5): 
        print(f"[{idx}] {FWTYPE.get(typ,typ)}: skip (not MCU code image)"); continue
    b=data[shift:shift+size]
    w=struct.unpack_from("<8I",b,0)
    sec_num=g(w[6],15,8); dyn=g(w[7],16,16)
    base_hdr=32+sec_num*16
    hdr_len=g(w[3],23,16) if dyn else base_hdr
    yr=w[5]; mon=g(w[4],7,0); day=g(w[4],15,8)
    name=f"{FWTYPE.get(typ,typ)}_cv{idx}"
    print(f"\n[{idx}] {name}: sec_num={sec_num} dyn_hdr={dyn} base_hdr={base_hdr} hdr_len={hdr_len} built {yr}-{mon:02d}-{day:02d}")
    pos=hdr_len
    for s in range(sec_num):
        sw=struct.unpack_from("<4I",b,32+s*16)
        raw_addr=sw[0]; dladdr=raw_addr & 0x1fffffff
        sectype=g(sw[1],27,24); secsize=g(sw[1],23,0); ck=g(sw[1],28,28)
        seglen=secsize+(8 if ck else 0)
        payload=b[pos:pos+seglen]
        tag={2:"code0",1:"data1",9:"sig"}.get(sectype,f"t{sectype}")
        fn=f"{OUT}/{name}_sec{s}_{tag}_load{dladdr:#010x}.bin"
        if sectype!=9:  # skip writing the signature blob
            open(fn,"wb").write(payload)
        print(f"   sec{s} type={sectype}({tag}) raw_addr={raw_addr:#010x} load={dladdr:#010x} size={seglen} ck={ck} -> {os.path.basename(fn) if sectype!=9 else '(signature, not written)'}")
        pos+=seglen
