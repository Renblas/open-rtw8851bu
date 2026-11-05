import sys,re
base=0xb8970000; buckets={}
for line in sys.stdin:
    m=re.search(r'0x([0-9a-f]{8})\s+(\S+)',line)
    if not m: continue
    a=int(m.group(1),16); mnem=m.group(2); b=(a-base)//8192
    d=buckets.setdefault(b,[0,0]); d[1]+=1
    if mnem in ('invalid','unaligned','.byte','.word'): d[0]+=1
print("8KiB buckets: valid-instruction %  (low = data/tables, high = code)")
for b in sorted(buckets):
    inv,tot=buckets[b]; good=100*(tot-inv)/tot if tot else 0
    print(f"  0x{base+b*8192:08x}  valid={good:5.1f}%  {'#'*int(good/4)}")
