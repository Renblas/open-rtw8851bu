import struct, sys
data = open("/lib/firmware/rtw89/rtw8851b_fw.bin","rb").read()
print(f"file size: {len(data)} bytes ({len(data)/1024:.1f} KiB)\n")
FWTYPE = {1:"NORMAL (STA)",3:"WOWLAN",5:"NORMAL_CE",64:"BBMCU0 (baseband)",65:"BBMCU1",255:"LOGFMT"}
SECTYPE = {9:"SECURITY (signature)"}
def g(v,hi,lo): return (v >> lo) & ((1<<(hi-lo+1))-1)

assert data[0]==0xFF, "not an MFW container"
fw_nr = data[1]
mj,mn,sub,idx = data[4],data[5],data[6],data[7]
print(f"MFW container: sig=0xFF  sub-firmwares={fw_nr}  packed-ver={mj}.{mn}.{sub}.{idx}")
print("="*70)
# mfw_info entries: cv(1) type(1) mp(1) rsvd(1) shift(le32) size(le32) rsvd2(4) = 16 bytes
off = 16
subs = []
for i in range(fw_nr):
    cv,typ,mp,_ = data[off],data[off+1],data[off+2],data[off+3]
    shift,size = struct.unpack_from("<II", data, off+4)
    off += 16
    subs.append((typ,mp,shift,size,cv))
    print(f"[{i}] type={FWTYPE.get(typ,typ):22} cv={cv} mp={mp}  offset={shift:#9x}  size={size:7d} ({size/1024:5.1f} KiB)")

print("="*70)
# Parse the inner header of each sub-firmware (format-0 rtw89_fw_hdr: 32-byte hdr + 16-byte sections)
for typ,mp,shift,size,cv in subs:
    if typ not in (1,3,5): continue  # MCU code images
    b = data[shift:shift+size]
    w = struct.unpack_from("<8I", b, 0)
    major=g(w[1],7,0); minor=g(w[1],15,8); subv=g(w[1],23,16)
    hdr_ver=g(w[3],31,24); sec_num=g(w[6],15,8); dyn=g(w[7],16,16)
    yr=w[5]; mon=g(w[4],7,0); day=g(w[4],15,8)
    print(f"\n{FWTYPE.get(typ,typ)}: ver {major}.{minor}.{subv}  hdr_ver={hdr_ver}  built {yr}-{mon:02d}-{day:02d}  sections={sec_num}  dyn_hdr={dyn}")
    so = 32
    code_total=0; data_total=0
    for s in range(sec_num):
        sw = struct.unpack_from("<4I", b, so); so += 16
        dl_addr = sw[0]
        sectype = g(sw[1],27,24); secsize = g(sw[1],23,0)
        has_ck = g(sw[1],28,28); redl = g(sw[1],29,29)
        label = SECTYPE.get(sectype, f"CODE/DATA type{sectype}")
        where = "signature" if sectype==9 else ("IMEM/code" if dl_addr < 0x40000 else f"@{dl_addr:#x}")
        print(f"   sec[{s}] load_addr={dl_addr:#010x}  size={secsize:6d}  type={sectype} {label} {'+chksum' if has_ck else ''}{' REDL' if redl else ''}")
        if sectype==9: pass
        else: code_total += secsize
    print(f"   -> non-signature section bytes: {code_total} ({code_total/1024:.1f} KiB)")
