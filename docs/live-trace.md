# Ghidra live view — open-rtw8851bu

**Watching:** `FUN_00024714` @ `0x00024714`  ·  WOWLAN code image (MIPS32 LE)
**Updated:** 2026-10-27 09:1x

This file shows the function the agent is examining right now: the Ghidra decompiler output
plus the raw MIPS disassembly. It is rewritten each time the focus moves to a new function.

---

## Why this function

A real firmware event handler found by auto-analysis. It reads hardware register `0x8104`,
loops over its bits, and dispatches a 2-byte message through a function-pointer table in the
data region (`0xb8e1xxxx`). It is a good proof that the decompiler works on this image.

## Decompiled C

```c
void FUN_00024714(void)
{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int local_30;
  undefined1 local_2c;
  undefined1 local_2b;

  local_30 = 0;
  uVar5 = 3;
  iVar1 = *(int *)(/* ptr table @0xb8e0a870 */ + 8);
  uVar2 = (*_DAT_b8e094d4)(0x8104);                 /* read reg 0x8104 */
  uVar2 = *(uint *)(*(int *)(/* @0xb8e0a868 */ + 4) + 0x2c) & uVar2;
  (*_DAT_b8e094c8)(0x8104,uVar2);                   /* write reg 0x8104 */
  uVar3 = 8;
  do {
    if ((uVar3 & uVar2) != 0) {
      (*_DAT_b8e09ed4)(0x18);
      local_2c = 2;
      local_2b = (char)uVar5;
      iVar4 = (*_DAT_b8e092f4)(*(undefined4 *)(iVar1 + 0x2c),&local_2c,2,&local_30);
      if (iVar4 != 2) {
        (*_DAT_b8e09ecc)(0,0x4000000,7);
      }
    }
    uVar5 = uVar5 - 1;
    uVar3 = 1 << (uVar5 & 0x1f);
  } while (uVar5 != 1);
  if ((uVar2 & 1) != 0) {
    (*_DAT_b8e09ed4)(0x16);
    (*_DAT_b8e0912c)();
  }
  if ((uVar2 & 0x20) != 0) {
    (*_DAT_b8e091ec)(*(undefined4 *)(iVar1 + 0xc),1,1,0,&local_30);
  }
  if ((uVar2 & 0x100) != 0) {
    (*_DAT_b8e09ed4)(0x19);
    if (*_DAT_b8e0a86c != 0) {
      func_0x08981794();
      (*_DAT_b8e098e4)();
    }
  }
  if (local_30 != 0) {
    (*_DAT_b8e09064)();
  }
  return;
}
```

## Disassembly (first 40 of 213 instructions)

```
00024714  addiu sp,sp,-0x48
00024718  sw    ra,0x44(sp)
0002471c  sw    s8,0x40(sp)
00024720  sw    s7,0x3c(sp)
00024724  sw    s6,0x38(sp)         ; saves s0-s8 + ra: a big non-leaf function
00024728  sw    s5,0x34(sp)
0002472c  sw    s4,0x30(sp)
00024730  sw    s3,0x2c(sp)
00024734  sw    s2,0x28(sp)
00024738  sw    s1,0x24(sp)
0002473c  sw    s0,0x20(sp)
00024740  lui   s0,0xb8e1
00024744  addiu s1,s0,-0x5798        ; s1 = 0xb8e0a868  (a struct pointer in RAM)
00024748  lbu   v1,0x9(s1)
0002474c  lbu   v0,0x8(s1)
00024750  sw    zero,0x18(sp)
00024754  sll   v1,v1,0x8
00024758  or    v1,v1,v0             ; assembling a 32-bit pointer byte-by-byte
0002475c  lbu   v0,0xa(s1)
00024760  ori   a0,zero,0x8104       ; a0 = 0x8104  (the hardware register id)
00024764  li    s3,0x3
00024768  sll   v0,v0,0x10
0002476c  or    v1,v0,v1
00024770  lbu   v0,0xb(s1)
00024774  li    s4,0x1
00024778  lui   s5,0xb8e1
0002477c  sll   v0,v0,0x18
00024780  or    v0,v0,v1
00024784  lbu   v1,0x9(v0)
00024788  lbu   s2,0x8(v0)
0002478c  lui   s6,0xb8e1
00024790  sll   v1,v1,0x8
00024794  or    v1,v1,s2
00024798  lbu   s2,0xa(v0)
0002479c  lui   s7,0xb8e1
000247a0  sll   s2,s2,0x10
000247a4  or    v1,s2,v1
000247a8  lbu   s2,0xb(v0)
000247ac  lui   v0,0xb8e1
000247b0  lw    v0,-0x6b2c(v0)       ; v0 = *(0xb8e094d4) = a function pointer
... (173 more instructions)
```

================================================================================
UPDATE 2026-10-27 — 3 interrupt handlers named; ISA puzzle cracked
================================================================================

Named the firmware's core primitives (the function-pointer table at 0xb8e09xxx):
  p_read_mac_reg(reg)          read a MAC hardware register
  p_write_mac_reg(reg, val)    write a MAC hardware register
  p_fw_send_msg(q, buf, len,&st)  push a message/report (returns bytes sent)
  p_log_err(0, 0x4000000, code)   error log
  p_msg_commit()               flush queued messages
  p_dbg_mark(id)               debug trace marker

Three auto-found functions, all interrupt/event dispatchers (now renamed):
  isr_dispatch_reg8104  @ 0x24714   reads reg 0x8104, dispatches per-bit
  event_report_dispatch @ 0x24a68   builds and sends event reports (big flag switch)
  isr_dispatch_regc104  @ 0x253d8   reads reg 0xc104, dispatches per-bit

isr_dispatch_reg8104 (now readable):
  uVar2 = (*p_read_mac_reg)(0x8104);
  uVar2 &= *(mask from device ctx);
  (*p_write_mac_reg)(0x8104, uVar2);     // ack handled bits
  for each set bit -> (*p_fw_send_msg)(queue, &msg, len, &st);
  if (anything queued) (*p_msg_commit)();

KEY FINDING — mixed ISA + real base address:
  The handlers make direct calls to 0x0898xxxx (e.g. func_0x08981794, func_0x089ae000).
  Read of offset 0x11794 and 0x3e000 shows: fa 63 0b 62 0a d1 09 d0 f7 f0 ...
  -> that is a MIPS16e prologue, not MIPS32. The bulk of the firmware is MIPS16e;
     the ISRs/startup are MIPS32; calls between them use jalx (mode switch).
  -> The code's true base is 0x08970000 (so 0x08981794 = image offset 0x11794).
     At base 0 those targets fall outside the image, so analysis never followed
     them -> only 3 functions found.

NEXT: rebuild the Ghidra project with the code based at 0x08970000 (and the data
section at 0xb8e12c00). Then jalx targets resolve and Ghidra decodes the MIPS16e
bulk -> the full function set, incl. the Gtimer/PStimer timer code we need.

================================================================================
UPDATE 2026-10-27 — base-correct rebuild done
================================================================================
Re-analyzed at true base 0x08970000 (project: ghidra-projects/wowlan-based).
  image base/range : 0x08970000 - 0x089aebb7
  functions found  : 14  (was 3)
The direct-call targets now DECODE. Example FUN_08981794 (MIPS16e) reads reg 0x8140,
and on a fault condition spins forever kicking a watchdog -> a reset/recovery path.

Still partial: only directly-called (jal/jalx) functions are discovered. Most of the
firmware is reached ONLY through the runtime function-pointer table (0xb8e09xxx), which
static analysis cannot follow. To get the full function set (incl. Gtimer/PStimer) we
need a prologue-seeding pass: scan for MIPS16e/MIPS32 prologues and define a function at
each, then re-analyze. The MCP's read-only tools have no create-function op, so that is
a Ghidra post-script (next step).

================================================================================
UPDATE 2026-10-27 — FULL MAP (973 functions) + timer & sleep/wake located
================================================================================
Corrected base to 0xb8970000. Seeded 370 functions from the firmware's own 419-entry
pointer table (in the data section); call-following cascaded to 973 FUNCTIONS TOTAL.

The data section also holds the firmware's SOURCE FILE NAMES (used in assert()), which
map the module structure. Functions located by xref to their module's filename string:

  TIMER  (HAL8851B_Timer_RAM.c): b8978738 b8978a20 b8978c08 b8978df8 b8978fec
  RPWM/CPWM sleep-wake handshake (WlanComm_RPWM_CPWM_RAM.c): b89a535c b89a5424
  WoWLAN (WlanComm_WoWLAN_RAM.c): b89a94b0 b89a9638 b89ab5e8 b89ac60c b89ac8bc

rpwm_cpwm_handler @ 0xb89a535c  (THE host<->chip sleep/wake path):
  rpwm = (*p_read_rpwm)();                 // host's power-request word
  if ((rpwm & 0x100) == 0) {               // normal power-mode change
      mode = rpwm & 7;
      (*p_set_power_mode)(rpwm>>0xc & 3);
      (*p_ack_cpwm)(mode, ...);            // acknowledge via CPWM
  } else {                                 // sleep / WoWLAN request
      if (FUN_b8974be4(2)) assert(...);
      FUN_b899f038();                      // enter sleep/wowlan state
  }

-> To self-wake: arm a HAL timer (timer module) during the sleep path, and on fire,
   assert a wake toward the host (CPWM / USB remote wakeup). Next: trace FUN_b899f038
   (sleep entry) and how the chip raises a host wake, then find the timer-arm API.
