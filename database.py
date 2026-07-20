import sqlite3
from pathlib import Path
import pandas as pd
DB_PATH=Path("data/scanner.db")
def _connect():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True); return sqlite3.connect(DB_PATH)
def init_db():
    with _connect() as c: c.execute("""CREATE TABLE IF NOT EXISTS recommendations (id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, player TEXT, opponent TEXT, tournament TEXT, market_price_cents REAL, status TEXT, stability_score REAL, required_score REAL, stake_pct REAL, stake_amount REAL, bankroll REAL, notes TEXT, result TEXT DEFAULT 'OPEN', pnl REAL DEFAULT 0)""")
def save_recommendation(r):
    cols=["player","opponent","tournament","market_price_cents","status","stability_score","required_score","stake_pct","stake_amount","bankroll","notes"]
    with _connect() as c: c.execute(f"INSERT INTO recommendations ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})",[r.get(x) for x in cols])
def load_recommendations():
    init_db()
    with _connect() as c: return pd.read_sql_query("SELECT * FROM recommendations ORDER BY id DESC",c)
def update_result(row_id,result,pnl):
    with _connect() as c: c.execute("UPDATE recommendations SET result=?, pnl=? WHERE id=?",(result,pnl,row_id))
