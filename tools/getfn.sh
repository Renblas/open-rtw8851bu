#!/bin/bash
# extract one function's decompiled C from decompiled/wowlan_full.c by name
awk -v n="$1" '
  $0 ~ ("===== " n " @") {p=1}
  p {print}
  p && /^\/\* ===== / && $0 !~ ("===== " n " @") && seen {exit}
  p && /^\/\* ===== / {seen=1}
' decompiled/wowlan_full.c
