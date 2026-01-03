"""
NFL Game Prediction Data Module
Panthers vs Buccaneers - Week 18, January 3, 2026

This module contains all gathered data for the prediction model.
Data sources: ESPN, Pro Football Reference, CBS Sports, Odds Shark, NFL.com
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

@dataclass
class TeamStats:
    """Team statistics for the 2025 season"""
    name: str
    record_wins: int
    record_losses: int

    # Offensive stats
    total_offensive_yards: int
    rushing_yards: int
    passing_yards: int
    points_per_game: float
    offensive_yards_per_game: float
    rushing_yards_per_game: float
    passing_yards_per_game: float
    third_down_conversions: int
    third_down_attempts: int
    touchdowns: int
    turnovers_committed: int

    # Defensive stats (yards/points allowed)
    defensive_yards_allowed: int
    defensive_points_allowed_per_game: float
    defensive_rushing_allowed: int
    defensive_passing_allowed: int
    sacks_made: int
    interceptions_made: int

    # Advanced metrics
    epa_offense: float  # EPA per play (higher is better)
    epa_defense: float  # EPA per play allowed (lower is better)

    # Recent form (last 5 games)
    last_5_wins: int
    last_5_losses: int

    # ATS (Against The Spread) record
    ats_record_wins: int
    ats_record_losses: int

    @property
    def win_pct(self) -> float:
        return self.record_wins / (self.record_wins + self.record_losses)

    @property
    def third_down_pct(self) -> float:
        return self.third_down_conversions / self.third_down_attempts

    @property
    def recent_form_pct(self) -> float:
        return self.last_5_wins / 5


@dataclass
class QuarterbackStats:
    """Quarterback statistics"""
    name: str
    passing_yards: int
    passing_tds: int
    interceptions: int
    qbr: float
    games_played: int
    completion_pct: float

    @property
    def td_int_ratio(self) -> float:
        return self.passing_tds / max(self.interceptions, 1)

    @property
    def yards_per_game(self) -> float:
        return self.passing_yards / self.games_played


@dataclass
class HeadToHeadRecord:
    """Head-to-head historical record"""
    total_games: int
    team1_wins: int
    team2_wins: int
    last_5_team1_wins: int
    last_5_team2_wins: int
    home_team_wins_last_5: int  # At this specific venue
    most_recent_winner: str
    most_recent_score: str


@dataclass
class BettingData:
    """Current betting market data"""
    spread: float  # Negative means favorite
    favorite: str
    over_under: float
    moneyline_favorite: int
    moneyline_underdog: int
    public_money_pct_favorite: float
    sharp_money_indicator: str  # "favorite" or "underdog"


@dataclass
class InjuryReport:
    """Key injury information"""
    team: str
    out: List[str]
    questionable: List[str]
    key_player_status: Dict[str, str]


@dataclass
class ContextualFactors:
    """Game context and situational factors"""
    is_home_game: bool
    weather_temp_f: int
    weather_conditions: str
    rest_days: int
    playoff_implications: str
    motivation_level: str  # "high", "medium", "low"


# =============================================================================
# ACTUAL DATA - Gathered from web searches on January 3, 2026
# =============================================================================

# Carolina Panthers Stats (8-8)
PANTHERS = TeamStats(
    name="Carolina Panthers",
    record_wins=8,
    record_losses=8,

    # Offensive stats
    total_offensive_yards=4740,
    rushing_yards=1958,
    passing_yards=3038,  # Bryce Young: 2745 + others
    points_per_game=19.5,  # Estimated from yards and TD data
    offensive_yards_per_game=322.9,
    rushing_yards_per_game=123.9,
    passing_yards_per_game=198.9,
    third_down_conversions=73,
    third_down_attempts=197,
    touchdowns=32,  # Estimated
    turnovers_committed=18,  # Estimated from Young's 10 INTs + fumbles

    # Defensive stats
    defensive_yards_allowed=5225,
    defensive_points_allowed_per_game=22.0,  # Estimated
    defensive_rushing_allowed=1956,
    defensive_passing_allowed=3454,
    sacks_made=38,  # Estimated
    interceptions_made=12,  # Estimated

    # Advanced metrics (from search: Panthers 21st in EPA/play allowed at 0.064)
    epa_offense=-0.02,  # Slightly below average offense
    epa_defense=0.064,  # 21st ranked defense

    # Recent form
    last_5_wins=3,  # Won 3 of last 5 including TB win
    last_5_losses=2,

    # ATS record (9-5 as underdog per search)
    ats_record_wins=9,
    ats_record_losses=7
)

# Tampa Bay Buccaneers Stats (7-9)
BUCCANEERS = TeamStats(
    name="Tampa Bay Buccaneers",
    record_wins=7,
    record_losses=9,

    # Offensive stats
    total_offensive_yards=5109,
    rushing_yards=1807,
    passing_yards=3552,
    points_per_game=22.0,  # Estimated
    offensive_yards_per_game=331.9,
    rushing_yards_per_game=113.2,
    passing_yards_per_game=218.6,
    third_down_conversions=86,
    third_down_attempts=213,
    touchdowns=40,
    turnovers_committed=20,  # 10 INTs from Mayfield + fumbles

    # Defensive stats
    defensive_yards_allowed=5448,
    defensive_points_allowed_per_game=24.5,  # Estimated from allowing 45 TDs
    defensive_rushing_allowed=1665,
    defensive_passing_allowed=4066,
    sacks_made=32,  # Estimated
    interceptions_made=12,

    # Advanced metrics (from search: Bucs 29th in EPA/play allowed at 0.118)
    epa_offense=0.05,  # Slightly above average offense
    epa_defense=0.118,  # 29th ranked defense - VERY BAD

    # Recent form (lost 4 straight, 1-7 in last 8)
    last_5_wins=1,
    last_5_losses=4,

    # ATS record (0-8 ATS in last 8 per search)
    ats_record_wins=5,
    ats_record_losses=11
)

# Quarterback Stats
BRYCE_YOUNG = QuarterbackStats(
    name="Bryce Young",
    passing_yards=2745,
    passing_tds=21,
    interceptions=10,
    qbr=48.0,
    games_played=15,
    completion_pct=64.5  # Estimated
)

BAKER_MAYFIELD = QuarterbackStats(
    name="Baker Mayfield",
    passing_yards=2999,
    passing_tds=25,  # Estimated from team's 25 passing TDs
    interceptions=10,
    qbr=58.0,  # Estimated, had 61.6 QBR in loss to Panthers
    games_played=16,
    completion_pct=62.5  # 335/536 attempts
)

# Head-to-Head Record
H2H_RECORD = HeadToHeadRecord(
    total_games=50,
    team1_wins=26,  # Panthers all-time
    team2_wins=24,  # Buccaneers all-time
    last_5_team1_wins=2,  # Panthers won 2 of last 5
    last_5_team2_wins=3,  # Bucs won 3 of last 5
    home_team_wins_last_5=5,  # Bucs 5-0 at home vs Panthers since 2019
    most_recent_winner="Panthers",
    most_recent_score="23-20"
)

# Current Betting Data
BETTING_DATA = BettingData(
    spread=-2.5,  # Bucs favored by 2.5
    favorite="Tampa Bay Buccaneers",
    over_under=43.5,
    moneyline_favorite=-144,
    moneyline_underdog=122,
    public_money_pct_favorite=60.0,  # Estimated
    sharp_money_indicator="underdog"  # Reverse line movement to Panthers
)

# Injury Reports
PANTHERS_INJURIES = InjuryReport(
    team="Carolina Panthers",
    out=["Robert Hunt (G)", "David Moore (WR)", "Robert Rochell (CB)", "Claudin Cherelus"],
    questionable=[],
    key_player_status={
        "Bryce Young": "Healthy - Full Go",
    }
)

BUCCANEERS_INJURIES = InjuryReport(
    team="Tampa Bay Buccaneers",
    out=["Jamel Dean (CB)", "Anthony Nelson (DE)"],
    questionable=["Tristan Wirfs (T) - Toe", "Luke Goedeke (T) - Ankle", "Calijah Kancey (DL)"],
    key_player_status={
        "Baker Mayfield": "Healthy - Removed from injury report",
        "Mike Evans": "Expected to play (rest day)",
        "Tristan Wirfs": "Questionable - Toe injury"
    }
)

# Contextual Factors
PANTHERS_CONTEXT = ContextualFactors(
    is_home_game=False,
    weather_temp_f=65,  # Typical January Tampa weather
    weather_conditions="Clear, mild",
    rest_days=6,  # Standard week
    playoff_implications="Win and in - Clinch NFC South with victory",
    motivation_level="high"
)

BUCCANEERS_CONTEXT = ContextualFactors(
    is_home_game=True,
    weather_temp_f=65,
    weather_conditions="Clear, mild",
    rest_days=6,
    playoff_implications="Must win + Atlanta loss to make playoffs",
    motivation_level="high"
)
