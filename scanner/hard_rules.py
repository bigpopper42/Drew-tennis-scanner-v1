from dataclasses import dataclass
from typing import List
from .models import MatchInput

@dataclass
class HardRuleResult:
    status: str
    passed: List[str]
    failed: List[str]
    waiting: List[str]

def evaluate_hard_rules(match: MatchInput) -> HardRuleResult:
    passed, failed, waiting = [], [], []
    if match.match_closing_set: passed.append("Current set is match-closing")
    else: failed.append("Current set is not match-closing")
    if match.break_lead >= 1: passed.append(f"Backed player leads by {match.break_lead} break(s)")
    else: waiting.append("Backed player is not ahead by a break")
    if match.tiebreak: failed.append("Current set is in a tiebreak")
    else: passed.append("Not in a tiebreak")
    if match.break_lead == 1 and match.backed_player_games_in_set < 4:
        waiting.append("One-break lead is not mature enough; fewer than four games won in closing set")
    else: passed.append("Break lead is mature enough")
    normalized = match.current_game_score.strip().replace("–", "-")
    if match.break_lead == 1 and match.serving and normalized in {"0-40", "15-40"}:
        waiting.append(f"One-break lead is under immediate break danger at {normalized}")
    else: passed.append("No immediate one-break danger")
    if match.completed_sets > 0:
        completed = match.breaks_suffered_by_set[:match.completed_sets]
        if len(completed) >= match.completed_sets and all(x >= 2 for x in completed):
            failed.append("Backed player was broken at least twice in every completed set")
        else: passed.append("Excessive-volatility rule passed")
    else: passed.append("No completed-set volatility failure")
    status = "NO TRADE" if failed else ("WAIT" if waiting else "ELIGIBLE")
    return HardRuleResult(status, passed, failed, waiting)
