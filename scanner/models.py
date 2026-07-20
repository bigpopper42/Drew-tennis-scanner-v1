from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

@dataclass
class MatchInput:
    player: str
    opponent: str
    tournament: str
    tournament_level: str
    surface: str
    market_price_cents: float
    bankroll: float
    match_closing_set: bool
    break_lead: int
    serving: bool
    tiebreak: bool
    backed_player_games_in_set: int
    current_game_score: str
    completed_sets: int
    breaks_suffered_by_set: List[int]
    service_points_won_pct: float
    first_serve_points_won_pct: float
    first_serve_in_pct: float
    breaks_suffered_total: int
    break_points_faced: int
    comfortable_holds_pct: float
    double_faults_per_service_game: float
    recent_form_label: str
    ranking: Optional[int]
    surface_form_label: str
    notes: str = ""
    def to_dict(self) -> Dict:
        return asdict(self)
