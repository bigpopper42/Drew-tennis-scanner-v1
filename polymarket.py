import requests
GAMMA_BASE="https://gamma-api.polymarket.com"
def fetch_active_markets(limit=100):
    r=requests.get(f"{GAMMA_BASE}/markets",params={"active":"true","closed":"false","limit":limit},timeout=20); r.raise_for_status(); d=r.json(); return d if isinstance(d,list) else d.get("data",[])
def search_markets_locally(query,limit=200):
    q=query.lower().strip(); out=[]
    for m in fetch_active_markets(limit):
        h=" ".join([str(m.get("question","")),str(m.get("description","")),str(m.get("slug",""))]).lower()
        if not q or q in h: out.append(m)
    return out
