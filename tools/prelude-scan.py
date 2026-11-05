import struct, glob, os
D="/home/renblas/.local/share/hw-advisor/fw-sections"
for f in sorted(glob.glob(D+"/*_sec0_code0_*.bin")):
    b=open(f,"rb").read()
    n=len(b)//4
    prologues=0
    for i in range(0,len(b)-3,4):
        w=struct.unpack_from("<I",b,i)[0]
        if (w & 0xffff0000)==0x27bd0000 and (w & 0x8000):  # addiu sp,sp,-N
            prologues+=1
    # jalr (indirect call) count: special, funct=0x09, rd=31 -> 0x0000f809 with rs in bits21-25
    jalr=sum(1 for i in range(0,len(b)-3,4)
             if (struct.unpack_from("<I",b,i)[0] & 0xfc1fffff)==0x0000f809)
    jal=sum(1 for i in range(0,len(b)-3,4)
            if (struct.unpack_from("<I",b,i)[0] & 0xfc000000)==0x0c000000)  # jal direct
    print(f"{os.path.basename(f):42} words={n:6d} fn-prologues={prologues:5d} jalr={jalr:5d} jal={jal:5d}")
