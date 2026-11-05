# Insert two unconditional pr_info lines into rtw89_efuse_read_fw_secure_ax (efuse.c),
# so the driver prints the raw secure-boot OTP bytes and the computed secure_boot flag,
# without needing CONFIG_RTW89_DEBUGMSG. Idempotent-ish: refuses if already patched.
import sys
f = "/home/renblas/kernel-explore/dangerous-src/drivers/net/wireless/realtek/rtw89/efuse.c"
s = open(f).read()
if "FUSEPROBE" in s:
    print("already patched"); sys.exit(0)

# 1) print raw bytes right after they are read (covers the b1==b2==0xFF early return)
anchor1 = "\tb1 = sec_map[0];\n\tb2 = sec_map[1];\n"
assert s.count(anchor1) == 1, "anchor1 not found uniquely"
add1 = anchor1 + '\tpr_info("rtw89 FUSEPROBE: efuse[0x5EC..0x5ED] = 0x%02x 0x%02x\\n", b1, b2);\n'
s = s.replace(anchor1, add1)

# 2) print the driver's final decision at the out: label (non-early-return path)
anchor2 = "out:\n\trtw89_debug(rtwdev, RTW89_DBG_FW,\n"
assert s.count(anchor2) == 1, "anchor2 not found uniquely"
add2 = ('out:\n'
        '\tpr_info("rtw89 FUSEPROBE: secure_boot=%d can_mss_v0=%d can_mss_v1=%d dev_type=%d\\n",\n'
        '\t\tsec->secure_boot, sec->can_mss_v0, sec->can_mss_v1, sec->mss_dev_type);\n'
        '\trtw89_debug(rtwdev, RTW89_DBG_FW,\n')
s = s.replace(anchor2, add2)

open(f, "w").write(s)
print("patched OK")
