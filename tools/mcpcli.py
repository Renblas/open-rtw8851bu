import sys, json, urllib.request
URL="http://127.0.0.1:8099/mcp"
def post(body, sid=None):
    h={"content-type":"application/json","accept":"application/json, text/event-stream"}
    if sid: h["mcp-session-id"]=sid
    req=urllib.request.Request(URL, data=json.dumps(body).encode(), headers=h, method="POST")
    r=urllib.request.urlopen(req, timeout=620)
    sid2=r.headers.get("mcp-session-id")
    raw=r.read().decode(errors="replace")
    # SSE or plain json: take last data: line or whole body
    obj=None
    for ln in raw.splitlines():
        ln=ln.strip()
        if ln.startswith("data:"): ln=ln[5:].strip()
        if ln.startswith("{"):
            try: obj=json.loads(ln)
            except: pass
    return obj, sid2
def main():
    tool=sys.argv[1]; args=json.loads(sys.argv[2]) if len(sys.argv)>2 else {}
    _,sid=post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"cli","version":"0"}}})
    post({"jsonrpc":"2.0","method":"notifications/initialized"}, sid)
    obj,_=post({"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":tool,"arguments":args}}, sid)
    if obj and "result" in obj:
        c=obj["result"].get("content",[])
        for item in c:
            if item.get("type")=="text": print(item["text"])
            else: print(json.dumps(item))
        if obj["result"].get("isError"): print("[isError=true]")
    else:
        print(json.dumps(obj, indent=2)[:2000])
main()
