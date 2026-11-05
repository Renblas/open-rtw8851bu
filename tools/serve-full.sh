#!/bin/bash
# Serve the base-0x08970000 project (wowlan-full) over the MCP HTTP interface for querying.
export PATH="$HOME/.local/bin:$PATH"
export GHIDRA_INSTALL_DIR=/home/renblas/ghidra-re/ghidra_12.1.4_PUBLIC
export JAVA_HOME=/opt/openjdk-bin-21
P=/home/renblas/Programming/open-rtw8851bu
WHL="ghidra-mcp[headless] @ file://$P/third_party/ghidra-mcp/GhidraMCP-release-2-0/ghidra_mcp-2.0.0-py3-none-any.whl"
JAR="$P/third_party/ghidra-mcp/extension/GhidraMCP/lib/GhidraMCP.jar"
BIN="$P/firmware/WOWLAN_cv2_sec0_code0_load0x18970000.bin"
exec uvx --python 3.13 --from "$WHL" ghidra-mcp \
  --headless --binary "$BIN" --extension-jar "$JAR" \
  --project "$P/ghidra-projects" --project-name wowlan-full \
  --transport streamable-http --mcp-host 127.0.0.1 --mcp-port 8099 --ready-timeout 600
