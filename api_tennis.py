import requests
BASE_URL="https://api.api-tennis.com/tennis/"
def get_live_events(api_key):
    if not api_key: raise ValueError("API Tennis key is missing.")
    r=requests.get(BASE_URL,params={"method":"get_livescore","APIkey":api_key},timeout=20); r.raise_for_status(); p=r.json()
    if not p.get("success"): raise RuntimeError(p.get("error","API Tennis request failed."))
    return p.get("result",[])
