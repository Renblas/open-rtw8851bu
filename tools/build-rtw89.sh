#!/bin/bash
set -e
GCC=x86_64-pc-linux-gnu-gcc-15
KTREE=/home/renblas/kernel-explore/dangerous-src
M=$KTREE/drivers/net/wireless/realtek/rtw89
ts(){ date +%T; }
echo "[$(ts)] building rtw89 modules (-j4, gcc-15)"
make -C "$KTREE" M="$M" CC=$GCC -j4 modules
echo "[$(ts)] built:"; ls -l "$M"/rtw89_core.ko "$M"/rtw89_8851bu.ko "$M"/rtw89_8851b.ko "$M"/rtw89_usb.ko
echo "[$(ts)] new vermagic: $(modinfo -F vermagic "$M"/rtw89_core.ko)"
echo "[$(ts)] running  vermagic: $(modinfo -F vermagic rtw89_core)"
echo "[$(ts)] FUSEPROBE string in new module: $(strings "$M"/rtw89_core.ko | grep -c FUSEPROBE)"
