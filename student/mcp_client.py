"""
Minimal MCP HTTP client wrapper (stub-friendly).
"""
import os, requests
MCP_HTTP_URL = os.environ.get("MCP_HTTP_URL", "").rstrip("/")

def _local_stub(tool, payload):
    if tool == "web.search":
        return {"results": [
            {"url": "https://example.com/article1", "title": "Example Article 1", "snippet": "Short snippet 1"},
            {"url": "https://example.org/post", "title": "Example Org Post", "snippet": "Short snippet 2"},
            {"url": "https://iana.org/about", "title": "IANA About", "snippet": "Short snippet 3"}
        ]}
    if tool == "web.fetch":
        url = payload.get("url","")
        html = f"<html><body><h1>{url}</h1><p>Sample page content for {url}.</p></body></html>"
        return {"url": url, "text": html}
    if tool == "notes.upsert":
        return {"ok": True}
    if tool == "notes.query":
        return {"rows":[{"k":"stub","v":"val"}]}
    if tool == "guard.pii_check":
        text = payload.get("text","")
        flagged = any(tok in text.lower() for tok in ["ssn","passport","aadhar"])
        return {"pii": flagged}
    return {"result":None}

def _post(tool, payload):
    if not MCP_HTTP_URL:
        return _local_stub(tool, payload)
    try:
        resp = requests.post(MCP_HTTP_URL + "/tool_call", json={"tool": tool, "input": payload}, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def web_search(q, max_results=5): return _post("web.search", {"q": q, "max_results": max_results})
def web_fetch(url): return _post("web.fetch", {"url": url})
def notes_upsert(key, text): return _post("notes.upsert", {"key": key, "text": text})
def notes_query(q): return _post("notes.query", {"q": q})
def guard_pii_check(text): return _post("guard.pii_check", {"text": text})
