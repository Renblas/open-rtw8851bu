#!/bin/bash
# Swap in the patched rtw89 modules, read the secure-boot OTP bytes from the kernel log,
# then let the adapter reconnect. Self-restoring: if the adapter does not return in ~110 s,
# hand Wi-Fi back to the internal card so the machine is never left offline.
M=/home/renblas/kernel-explore/dangerous-src/drivers/net/wireless/realtek/rtw89
ts(){ date +%T; }
IFACE=$(for x in /sys/class/net/*/device/driver; do \
  [ "$(basename "$(readlink -f "$x")")" = rtw89_8851bu ] && basename "$(dirname "$(dirname "$x")")"; done)
echo "[$(ts)] adapter iface = ${IFACE:-none}"
[ -n "$IFACE" ] && nmcli device disconnect "$IFACE" >/dev/null 2>&1

echo "[$(ts)] unloading stock rtw89 modules"
modprobe -r rtw89_8851bu rtw89_8851b rtw89_usb rtw89_core 2>&1
echo "[$(ts)] loading patched modules from $M"
insmod "$M/rtw89_core.ko"   && echo "  core ok"
insmod "$M/rtw89_8851b.ko"  && echo "  8851b ok"
insmod "$M/rtw89_usb.ko"    && echo "  usb ok"
insmod "$M/rtw89_8851bu.ko" && echo "  8851bu ok"

echo "[$(ts)] waiting for the fuse read..."
for i in $(seq 1 15); do
  dmesg | grep -q FUSEPROBE && break
  sleep 1
done
echo "===== FUSEPROBE ====="; dmesg | grep FUSEPROBE | tail -4; echo "====================="

echo "[$(ts)] waiting for adapter to reconnect"
ok=no
for i in $(seq 1 22); do
  st=$(nmcli -t -f DEVICE,STATE device 2>/dev/null | grep '^wlp.*:connected$')
  [ -n "$st" ] && { ok=yes; break; }
  sleep 5
done
if [ "$ok" = no ]; then
  echo "[$(ts)] adapter did not return: enabling internal card"
  nmcli device set wlp3s0 managed yes; nmcli device connect wlp3s0 2>&1
fi
echo "[$(ts)] final device state:"; nmcli -f DEVICE,TYPE,STATE,CONNECTION device | grep -E 'DEVICE|wl'
loaded=$(cat /sys/module/rtw89_core/srcversion 2>/dev/null); echo "[$(ts)] loaded core srcversion=$loaded (patched=$(modinfo -F srcversion "$M/rtw89_core.ko"))"
