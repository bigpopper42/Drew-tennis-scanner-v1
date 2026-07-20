from typing import Dict, List, Tuple
from .models import MatchInput

def band(value: float, rows: List[Tuple[float, float]]) -> float:
    for minimum, points in rows:
        if value >= minimum: return points
    return 0.0

def calculate_stability_score(match: MatchInput):
    p: Dict[str,float] = {}
    p["Overall service points won"] = band(match.service_points_won_pct, [(70,28),(68,26),(66,24),(64,21),(63,18),(62,15),(61,12)])
    p["First-serve points won"] = band(match.first_serve_points_won_pct, [(80,14),(76,12),(72,10),(68,8),(64,5),(0,1)])
    p["Breaks suffered"] = {0:14,1:11,2:7,3:3}.get(match.breaks_suffered_total,0)
    b=match.break_points_faced
    p["Break points faced"] = 9 if b<=1 else 8 if b==2 else 7 if b==3 else 5 if b==4 else 3 if b==5 else 1 if b<=7 else 0
    state = 12 if match.break_lead>=2 and match.serving else 10 if match.break_lead>=2 else 8 if match.break_lead==1 and match.serving else 6 if match.break_lead==1 else 0
    if match.break_lead==1 and match.backed_player_games_in_set==4: state=max(0,state-1)
    p["Match-state strength"] = state
    p["Comfortable holds"] = band(match.comfortable_holds_pct,[(75,5),(60,4),(45,2)])
    p["First-serve percentage"] = band(match.first_serve_in_pct,[(70,4),(65,3),(60,2),(55,1)])
    d=match.double_faults_per_service_game
    p["Double-fault rate"] = 3 if d<=.15 else 2 if d<=.30 else 1 if d<=.45 else 0
    p["Recent form and opponent quality"] = {"Excellent":7,"Strong":6,"Good":5,"Mixed":3,"Weak":1,"Very poor":0}.get(match.recent_form_label,3)
    r=match.ranking
    p["Ranking"] = 0 if not r else 2 if r<=10 else 1.5 if r<=40 else 1 if r<=100 else .5 if r<=150 else 0
    p["Tournament level"] = {"Grand Slam":1,"Masters 1000":1,"ATP 500":.75,"ATP 250":.5,"Challenger":.25,"Lower":0}.get(match.tournament_level,0)
    p["Surface evidence"] = {"Strong":1,"Neutral":.5,"Weak":0}.get(match.surface_form_label,.5)
    return round(sum(p.values()),2), p

def price_minimum_score(price):
    return 75 if price>=98 else 80 if price>=96 else 86 if price>=93 else 92 if price>=90 else 101

def position_size(score):
    return .07 if score>=92 else .05 if score>=83 else .03 if score>=75 else 0
