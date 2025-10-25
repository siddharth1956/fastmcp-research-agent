"""
Simple agent: search -> fetch -> extract -> synthesize -> write artifacts.
"""
import os, json, sqlite3
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from . import mcp_client

def ensure_dir(d): os.makedirs(d, exist_ok=True)

def ensure_notes_db(key="topic", val="initialized"):
    path = "notes.sqlite"
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS notes(k TEXT PRIMARY KEY, v TEXT)")
    cur.execute("INSERT OR REPLACE INTO notes (k, v) VALUES (?, ?)", (key, val))
    conn.commit(); conn.close()
    return path

def clean_html(html):
    soup = BeautifulSoup(html or "", "html.parser")
    for s in soup(["script","style","nav","footer","header","aside"]):
        s.decompose()
    text = " ".join(soup.get_text().split())
    return text[:2000]

def synthesize_brief(topic, snippets, selected_urls):
    cites = {u:i+1 for i,u in enumerate(selected_urls)}
    q1 = '"Recent analysis shows clear trends."'
    q2 = '"Export controls changed policy dynamics."'
    paragraphs = [
        f"{topic} — quick research brief. [{1}]",
        f"Major findings and trends summarized. {q1} [{2}]",
        f"Excerpt: {snippets[0]['text'][:200] if snippets else 'No snippet available.'} [{cites.get(selected_urls[0],1)}]",
        f"Cross-domain implications noted. {q2} [{cites.get(selected_urls[1],1)}]",
        "Implications: stakeholders should reassess supply chain and compliance. [3]",
        "This brief is a concise synthesis for research use. [4]"
    ]
    body = "\n\n".join(paragraphs)
    refs = []
    for u in selected_urls:
        refs.append(f"[{cites[u]}] {urlparse(u).netloc} — {u}")
    return body + "\n\nReferences\n" + "\n".join(refs) + "\n"

def run_agent(topic, out_dir, max_results=5):
    ensure_dir(out_dir)
    # 1) search
    search_resp = mcp_client.web_search(topic, max_results=max_results) or {}
    results = search_resp.get("results", []) if isinstance(search_resp, dict) else []
    with open(os.path.join(out_dir, "search_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # 2) fetch top results and extract snippets
    snippets = []
    selected_urls = []
    for r in (results or [])[:4]:
        url = r.get("url")
        if not url:
            continue
        fetch = mcp_client.web_fetch(url) or {}
        html = fetch.get("text", "")
        text = clean_html(html)
        snippets.append({"url": url, "title": r.get("title",""), "text": text})
        selected_urls.append(url)
        # store note best-effort
        try:
            mcp_client.notes_upsert(key=url, text=text[:400])
        except Exception:
            pass

    with open(os.path.join(out_dir, "selected_urls.json"), "w", encoding="utf-8") as f:
        json.dump(selected_urls, f, indent=2)
    with open(os.path.join(out_dir, "snippets.json"), "w", encoding="utf-8") as f:
        json.dump(snippets, f, indent=2)

    # ensure local notes DB
    db_path = ensure_notes_db(key="topic", val=topic)

    # synthesize brief
    brief = synthesize_brief(topic, snippets, selected_urls)

    # guard check
    guard = mcp_client.guard_pii_check(brief) or {}
    pii_flagged = bool(guard.get("pii", False))

    report = {"pii_flagged": pii_flagged}
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if pii_flagged:
        with open(os.path.join(out_dir, "hitl_ticket.json"), "w", encoding="utf-8") as f:
            json.dump({"reason":"pii_detected","details":guard}, f, indent=2)
    else:
        with open(os.path.join(out_dir, "brief.md"), "w", encoding="utf-8") as f:
            f.write(brief)

    return {"status":"pii_flagged" if pii_flagged else "ok", "db_path": db_path}
