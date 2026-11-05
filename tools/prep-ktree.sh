#!/bin/bash
# Reconstruct a configured scratch kernel tree for a module-only rtw89 rebuild.
# Unprivileged. Writes only under ~/kernel-explore (not the Portage tree).
set -e
GCC=x86_64-pc-linux-gnu-gcc-15
KTREE=/home/renblas/kernel-explore/dangerous-src
ts(){ date +%T; }
echo "[$(ts)] copy gentoo-sources -> $KTREE"
mkdir -p /home/renblas/kernel-explore
rm -rf "$KTREE"
cp -a /usr/src/linux-6.18.48-gentoo "$KTREE"
echo "[$(ts)] install saved dangerous .config"
cp /home/renblas/kernel-configs/config-6.18.48-dangerous "$KTREE/.config"
cd "$KTREE"
echo "[$(ts)] make olddefconfig"
make olddefconfig CC=$GCC >/dev/null
echo "[$(ts)] kernel.release = $(cat include/config/kernel.release 2>/dev/null || echo '?')"
echo "[$(ts)] make -j4 modules_prepare"
make -j4 modules_prepare CC=$GCC
echo "[$(ts)] modpost built: $([ -x scripts/mod/modpost ] && echo yes || echo NO)"
echo "[$(ts)] DONE prepare"
