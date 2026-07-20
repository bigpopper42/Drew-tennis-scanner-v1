from dataclasses import dataclass
from typing import Dict, List
from .models import MatchInput
from .hard_rules import evaluate_hard_rules
from .scoring import calculate_stability_score, price_minimum_score, position_size

@dataclass
class Decision:
    status:str; score:float; minimum_score:float; stake_pct:float; stake_amount:float; passed:List[str]; concerns:List[str]; score_parts:Dict[str,float]; reason:str

def evaluate_match(match: MatchInput) -> Decision:
    hard=evaluate_hard_rules(match)
    if hard.status=="NO TRADE": return Decision("NO TRADE",0,0,0,0,hard.passed,hard.failed,{},"One or more hard rules failed.")
    if hard.status=="WAIT": return Decision("WAIT",0,0,0,0,hard.passed,hard.waiting,{},"The setup is developing but is not eligible yet.")
    score,parts=calculate_stability_score(match); minimum=price_minimum_score(match.market_price_cents)
    if match.market_price_cents<90: status,reason,pct="NO TRADE","Version 1 does not trade prices below 90 cents.",0
    elif score<minimum: status,reason,pct="NO TRADE",f"Stability Score {score:.1f} is below the required {minimum:.1f} for this price.",0
    else: status,reason,pct="TRADE","All hard rules passed and the Stability Score meets the price-adjusted threshold.",position_size(score)
    concerns=[]
    if match.service_points_won_pct<64: concerns.append("Overall service points won is in the 61–63.9% tolerance range")
    if match.first_serve_points_won_pct<68: concerns.append("First-serve points won is below the preferred range")
    if match.break_points_faced>=5: concerns.append("Five or more break points faced")
    if match.breaks_suffered_total>=2: concerns.append("Two or more breaks suffered")
    if match.tournament_level in {"Challenger","Lower"}: concerns.append("Lower tournament-level confidence")
    if not concerns: concerns.append("No major soft-rule concerns detected")
    return Decision(status,score,minimum,pct,round(match.bankroll*pct,2),hard.passed,concerns,parts,reason)
