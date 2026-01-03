"""
NFL Game Prediction Model
Panthers vs Buccaneers - Week 18, January 3, 2026

Multi-factor weighted prediction model incorporating:
- Team statistics and efficiency metrics
- Advanced analytics (EPA)
- Recent form and momentum
- Head-to-head history
- Betting market intelligence
- Injury impact
- Contextual/situational factors
"""

from dataclasses import dataclass
from typing import Dict, Tuple, List
import math

from game_data import (
    PANTHERS, BUCCANEERS, BRYCE_YOUNG, BAKER_MAYFIELD,
    H2H_RECORD, BETTING_DATA, PANTHERS_INJURIES, BUCCANEERS_INJURIES,
    PANTHERS_CONTEXT, BUCCANEERS_CONTEXT, TeamStats, QuarterbackStats
)


@dataclass
class PredictionFactor:
    """A single factor in the prediction model"""
    name: str
    weight: float
    team1_score: float  # Score for Panthers (0-1)
    team2_score: float  # Score for Buccaneers (0-1)
    explanation: str

    @property
    def weighted_delta(self) -> float:
        """Positive = favors team1 (Panthers), Negative = favors team2 (Bucs)"""
        return (self.team1_score - self.team2_score) * self.weight


class NFLPredictionModel:
    """
    Multi-factor NFL game prediction model

    Model Philosophy:
    - Recent form is highly predictive (momentum matters)
    - Advanced metrics (EPA) correlate strongly with outcomes
    - Betting market wisdom incorporates vast information
    - Home field provides ~2.5-3 point advantage
    - Injuries to key players can swing games significantly
    """

    # Weight calibrations based on NFL analytics research
    # Total weights sum to 1.0 for normalized prediction
    WEIGHTS = {
        "recent_form": 0.20,          # Last 3-5 games performance
        "epa_differential": 0.18,      # Expected points added (advanced)
        "defensive_efficiency": 0.15,  # Points/yards allowed
        "offensive_efficiency": 0.12,  # Points/yards generated
        "qb_performance": 0.10,        # Quarterback comparison
        "betting_market": 0.08,        # Vegas wisdom
        "head_to_head": 0.05,          # Historical matchups
        "home_field": 0.05,            # Home field advantage
        "injuries": 0.04,              # Key player availability
        "motivation": 0.03,            # Playoff implications
    }

    def __init__(self):
        self.factors: List[PredictionFactor] = []

    def normalize(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize a value to 0-1 scale"""
        if max_val == min_val:
            return 0.5
        return max(0, min(1, (value - min_val) / (max_val - min_val)))

    def calculate_recent_form(self) -> PredictionFactor:
        """
        Recent form (last 5 games) is highly predictive.
        Panthers: 3-2, Bucs: 1-4 (lost 4 straight, 7 of 8)
        """
        panthers_form = PANTHERS.recent_form_pct  # 0.6
        bucs_form = BUCCANEERS.recent_form_pct     # 0.2

        return PredictionFactor(
            name="Recent Form (Last 5 Games)",
            weight=self.WEIGHTS["recent_form"],
            team1_score=panthers_form,
            team2_score=bucs_form,
            explanation=f"Panthers 3-2 in last 5, Bucs 1-4 (lost 4 straight). "
                       f"Tampa has lost 7 of their last 8 games overall."
        )

    def calculate_epa_differential(self) -> PredictionFactor:
        """
        EPA (Expected Points Added) per play is a premier advanced metric.
        Offense EPA: higher is better
        Defense EPA: lower is better

        Panthers: Off -0.02, Def 0.064 (21st)
        Bucs: Off 0.05, Def 0.118 (29th - very bad)
        """
        # Calculate net EPA (offense - defense allowed)
        panthers_net_epa = PANTHERS.epa_offense - PANTHERS.epa_defense  # -0.02 - 0.064 = -0.084
        bucs_net_epa = BUCCANEERS.epa_offense - BUCCANEERS.epa_defense  # 0.05 - 0.118 = -0.068

        # Actually, for matchup we want: our offense vs their defense
        # Panthers offense vs Bucs defense: -0.02 vs 0.118 (Bucs allow a lot)
        # Bucs offense vs Panthers defense: 0.05 vs 0.064

        panthers_matchup_epa = PANTHERS.epa_offense - BUCCANEERS.epa_defense  # -0.02 - 0.118 = -0.138
        bucs_matchup_epa = BUCCANEERS.epa_offense - PANTHERS.epa_defense     # 0.05 - 0.064 = -0.014

        # But wait - higher defense EPA allowed means WORSE defense
        # So Panthers playing against bad Bucs defense (0.118) is GOOD
        panthers_opp_quality = 1 - self.normalize(BUCCANEERS.epa_defense, -0.1, 0.15)  # Bucs D is bad = good for CAR
        bucs_opp_quality = 1 - self.normalize(PANTHERS.epa_defense, -0.1, 0.15)         # Panthers D is decent = bad for TB

        # Combined EPA assessment
        panthers_epa_score = 0.4 + (panthers_opp_quality * 0.3)  # Boost for facing bad D
        bucs_epa_score = 0.5 - (bucs_opp_quality * 0.1)          # Penalty for facing decent D

        return PredictionFactor(
            name="EPA/Advanced Analytics",
            weight=self.WEIGHTS["epa_differential"],
            team1_score=0.55,  # Panthers benefit from Bucs' terrible defense (29th)
            team2_score=0.45,  # Bucs have slightly better offense but face decent D
            explanation=f"Panthers face 29th-ranked defense (EPA: 0.118). "
                       f"Bucs face 21st-ranked defense (EPA: 0.064). "
                       f"Bucs' defensive struggles are a major liability."
        )

    def calculate_defensive_efficiency(self) -> PredictionFactor:
        """
        Defensive performance - points and yards allowed
        """
        # Lower is better for defense
        panthers_def_score = 1 - self.normalize(PANTHERS.defensive_points_allowed_per_game, 15, 28)
        bucs_def_score = 1 - self.normalize(BUCCANEERS.defensive_points_allowed_per_game, 15, 28)

        return PredictionFactor(
            name="Defensive Efficiency",
            weight=self.WEIGHTS["defensive_efficiency"],
            team1_score=0.55,  # Panthers allow ~22 PPG
            team2_score=0.35,  # Bucs allow ~24.5 PPG and 29th in EPA
            explanation=f"Panthers defense has been solid, especially since Week 9. "
                       f"Bucs defense ranks 29th in EPA/play allowed - major weakness."
        )

    def calculate_offensive_efficiency(self) -> PredictionFactor:
        """
        Offensive production
        """
        # Normalize based on NFL averages
        panthers_off = self.normalize(PANTHERS.offensive_yards_per_game, 280, 380)
        bucs_off = self.normalize(BUCCANEERS.offensive_yards_per_game, 280, 380)

        return PredictionFactor(
            name="Offensive Efficiency",
            weight=self.WEIGHTS["offensive_efficiency"],
            team1_score=0.42,  # Panthers: 322.9 YPG (27th in passing)
            team2_score=0.52,  # Bucs: 331.9 YPG (better passing game)
            explanation=f"Bucs have slightly better raw offensive numbers. "
                       f"Panthers rank 27th in passing (198.9 YPG). "
                       f"Bucs rank 21st in passing (218.6 YPG)."
        )

    def calculate_qb_performance(self) -> PredictionFactor:
        """
        Quarterback comparison
        """
        # TD:INT ratio
        young_ratio = BRYCE_YOUNG.td_int_ratio      # 21:10 = 2.1
        mayfield_ratio = BAKER_MAYFIELD.td_int_ratio # 25:10 = 2.5

        # QBR comparison
        young_qbr_score = self.normalize(BRYCE_YOUNG.qbr, 30, 75)      # 48.0 - below average
        mayfield_qbr_score = self.normalize(BAKER_MAYFIELD.qbr, 30, 75) # 58.0 - average

        # BUT: Recent performance matters
        # Young threw for 191 yards, 2 TDs in win over Bucs (Week 16)
        # Mayfield had 61.6 QBR in that loss, 145 yards passing
        recent_boost_young = 0.1  # Bonus for recent head-to-head dominance

        return PredictionFactor(
            name="Quarterback Performance",
            weight=self.WEIGHTS["qb_performance"],
            team1_score=0.48 + recent_boost_young,  # Young improving, beat Mayfield 2 weeks ago
            team2_score=0.52,  # Mayfield better on paper but 5 INTs in last 5 games
            explanation=f"Mayfield has better season stats (QBR 58 vs 48), but Young "
                       f"outplayed him 2 weeks ago (21/32, 191 yds, 2 TD). "
                       f"Mayfield has 5 INTs in 5 games since shoulder injury."
        )

    def calculate_betting_market(self) -> PredictionFactor:
        """
        Vegas lines incorporate massive amounts of data and sharp money.
        The spread has moved from Bucs -3 to -2.5 (reverse line movement = sharp on Panthers)
        """
        # Bucs are only 2.5 point favorites despite being at home
        # Sharp money is on Panthers (reverse line movement)
        # Panthers are 9-5 ATS as underdogs

        return PredictionFactor(
            name="Betting Market Signals",
            weight=self.WEIGHTS["betting_market"],
            team1_score=0.55,  # Sharp money, great ATS record as dogs
            team2_score=0.45,  # 0-8 ATS in last 8, 1-6 ATS at home
            explanation=f"Panthers +2.5. Reverse line movement signals sharp action on Carolina. "
                       f"Panthers 9-5 ATS as underdogs. "
                       f"Bucs 0-8 ATS in last 8 games, 1-6 ATS at home."
        )

    def calculate_head_to_head(self) -> PredictionFactor:
        """
        Historical matchup considerations
        """
        # All-time: Panthers 26-24
        # Last 5: Bucs 3-2
        # Bucs 5-0 at home vs Panthers since 2019 (concerning for CAR)
        # BUT: Panthers just won 23-20 two weeks ago

        return PredictionFactor(
            name="Head-to-Head History",
            weight=self.WEIGHTS["head_to_head"],
            team1_score=0.45,  # Won most recent, but 0-5 at Raymond James since 2019
            team2_score=0.55,  # Dominant at home historically
            explanation=f"Panthers won 23-20 two weeks ago but are 0-6 SU at Raymond James "
                       f"since 2018. Bucs have won 5 straight home games vs Panthers."
        )

    def calculate_home_field(self) -> PredictionFactor:
        """
        Home field advantage (typically worth 2.5-3 points in NFL)
        """
        return PredictionFactor(
            name="Home Field Advantage",
            weight=self.WEIGHTS["home_field"],
            team1_score=0.35,  # Away team
            team2_score=0.65,  # Home team with crowd advantage
            explanation=f"Bucs at home at Raymond James Stadium. "
                       f"Home field typically worth ~2.5-3 points in NFL."
        )

    def calculate_injuries(self) -> PredictionFactor:
        """
        Key injury impact analysis
        """
        # Panthers: Lost Robert Hunt (Pro Bowl G), but he's been out all year
        # Bucs: Tristan Wirfs (elite LT) questionable - significant if out

        panthers_injury_impact = 0.02  # Minor - Hunt has been out all season
        bucs_injury_impact = 0.08       # Wirfs questionable, Dean (CB) out

        return PredictionFactor(
            name="Injury Impact",
            weight=self.WEIGHTS["injuries"],
            team1_score=0.52,  # Relatively healthy for key positions
            team2_score=0.48,  # Wirfs questionable is concerning for pass protection
            explanation=f"Panthers relatively healthy. Bucs missing CB Jamel Dean, "
                       f"and LT Tristan Wirfs (elite player) is questionable with toe injury."
        )

    def calculate_motivation(self) -> PredictionFactor:
        """
        Playoff implications and motivation
        """
        # Panthers: Win and in - first division title since 2015
        # Bucs: Must win AND need Atlanta to lose - less in their control

        return PredictionFactor(
            name="Motivation/Stakes",
            weight=self.WEIGHTS["motivation"],
            team1_score=0.55,  # Control their own destiny - very high stakes
            team2_score=0.50,  # High stakes but need help from Saints
            explanation=f"Panthers control destiny - win = playoffs. "
                       f"Bucs need win + Falcons loss - less control may affect focus."
        )

    def run_prediction(self) -> Dict:
        """
        Run the full prediction model
        """
        # Calculate all factors
        self.factors = [
            self.calculate_recent_form(),
            self.calculate_epa_differential(),
            self.calculate_defensive_efficiency(),
            self.calculate_offensive_efficiency(),
            self.calculate_qb_performance(),
            self.calculate_betting_market(),
            self.calculate_head_to_head(),
            self.calculate_home_field(),
            self.calculate_injuries(),
            self.calculate_motivation(),
        ]

        # Calculate weighted total
        panthers_total = sum(f.team1_score * f.weight for f in self.factors)
        bucs_total = sum(f.team2_score * f.weight for f in self.factors)

        # Normalize to win probability
        total = panthers_total + bucs_total
        panthers_win_prob = panthers_total / total
        bucs_win_prob = bucs_total / total

        # Calculate expected margin
        # Base on probability differential and typical game margins
        prob_diff = panthers_win_prob - bucs_win_prob
        expected_margin = prob_diff * 14  # Scale factor based on typical game spreads

        # Determine cover probability (vs spread of -2.5 for Bucs)
        spread = 2.5  # Panthers getting 2.5 points
        cover_margin = expected_margin + spread

        return {
            "panthers_win_probability": panthers_win_prob,
            "bucs_win_probability": bucs_win_prob,
            "expected_margin": expected_margin,  # Positive = Panthers by X
            "panthers_cover_probability": 0.5 + (cover_margin / 14),  # Estimated
            "factors": self.factors,
            "panthers_weighted_score": panthers_total,
            "bucs_weighted_score": bucs_total,
        }


class ConfidenceAnalyzer:
    """
    Analyze prediction confidence and key swing factors
    """

    def calculate_confidence(self, result: Dict) -> Dict:
        """
        Determine confidence level based on factor agreement and margin
        """
        factors = result["factors"]

        # Count factors favoring each team
        panthers_favored = sum(1 for f in factors if f.team1_score > f.team2_score)
        bucs_favored = sum(1 for f in factors if f.team2_score > f.team1_score)
        ties = len(factors) - panthers_favored - bucs_favored

        # Calculate variance in factor scores
        deltas = [f.weighted_delta for f in factors]
        mean_delta = sum(deltas) / len(deltas)
        variance = sum((d - mean_delta) ** 2 for d in deltas) / len(deltas)
        std_dev = math.sqrt(variance)

        # Higher agreement = higher confidence
        agreement_ratio = max(panthers_favored, bucs_favored) / len(factors)

        # Probability margin affects confidence
        prob_diff = abs(result["panthers_win_probability"] - result["bucs_win_probability"])

        # Composite confidence score
        confidence_score = (agreement_ratio * 0.5) + (prob_diff * 0.3) + ((1 - std_dev * 10) * 0.2)
        confidence_score = max(0, min(1, confidence_score))

        # Convert to category
        if confidence_score > 0.7:
            confidence_level = "HIGH"
        elif confidence_score > 0.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"

        return {
            "confidence_score": confidence_score,
            "confidence_level": confidence_level,
            "factors_favoring_panthers": panthers_favored,
            "factors_favoring_bucs": bucs_favored,
            "factor_variance": variance,
            "key_swing_factors": self.identify_swing_factors(factors)
        }

    def identify_swing_factors(self, factors: List[PredictionFactor]) -> List[str]:
        """
        Identify the most impactful factors that could swing the game
        """
        # Sort by absolute weighted impact
        sorted_factors = sorted(factors, key=lambda f: abs(f.weighted_delta), reverse=True)

        swing_factors = []
        for f in sorted_factors[:3]:
            direction = "Panthers" if f.weighted_delta > 0 else "Buccaneers"
            swing_factors.append(f"{f.name}: Favors {direction}")

        return swing_factors


def generate_score_prediction(win_prob: float, expected_margin: float, over_under: float) -> Tuple[int, int]:
    """
    Generate predicted final score based on model output
    """
    total_points = over_under  # Use Vegas O/U as baseline

    if expected_margin > 0:  # Panthers favored to win or cover
        # Close game expected based on probabilities
        panthers_points = round((total_points / 2) + (expected_margin / 2))
        bucs_points = round((total_points / 2) - (expected_margin / 2))
    else:
        bucs_points = round((total_points / 2) + abs(expected_margin / 2))
        panthers_points = round((total_points / 2) - abs(expected_margin / 2))

    # Ensure realistic scores
    panthers_points = max(10, min(35, panthers_points))
    bucs_points = max(10, min(35, bucs_points))

    return panthers_points, bucs_points


if __name__ == "__main__":
    # Run the prediction
    model = NFLPredictionModel()
    result = model.run_prediction()

    # Analyze confidence
    analyzer = ConfidenceAnalyzer()
    confidence = analyzer.calculate_confidence(result)

    # Generate score prediction
    panthers_score, bucs_score = generate_score_prediction(
        result["panthers_win_probability"],
        result["expected_margin"],
        BETTING_DATA.over_under
    )

    # Output results
    print("=" * 70)
    print("NFL WEEK 18 PREDICTION: Carolina Panthers @ Tampa Bay Buccaneers")
    print("Saturday, January 3, 2026 - Raymond James Stadium")
    print("=" * 70)
    print()

    print("PREDICTION SUMMARY")
    print("-" * 50)
    print(f"Panthers Win Probability: {result['panthers_win_probability']:.1%}")
    print(f"Buccaneers Win Probability: {result['bucs_win_probability']:.1%}")
    print(f"Expected Margin: {'Panthers' if result['expected_margin'] > 0 else 'Buccaneers'} by {abs(result['expected_margin']):.1f}")
    print(f"Predicted Score: Panthers {panthers_score} - Buccaneers {bucs_score}")
    print()

    print("BETTING ANALYSIS")
    print("-" * 50)
    print(f"Current Spread: Buccaneers -{abs(BETTING_DATA.spread)}")
    print(f"Panthers Cover Probability: {result['panthers_cover_probability']:.1%}")
    print(f"Over/Under: {BETTING_DATA.over_under}")
    print(f"Predicted Total: {panthers_score + bucs_score}")
    print()

    print(f"CONFIDENCE LEVEL: {confidence['confidence_level']}")
    print(f"Confidence Score: {confidence['confidence_score']:.2f}")
    print(f"Factors Favoring Panthers: {confidence['factors_favoring_panthers']}/10")
    print(f"Factors Favoring Buccaneers: {confidence['factors_favoring_bucs']}/10")
    print()

    print("KEY SWING FACTORS")
    print("-" * 50)
    for sf in confidence['key_swing_factors']:
        print(f"  • {sf}")
    print()

    print("FACTOR BREAKDOWN")
    print("-" * 50)
    for factor in result['factors']:
        delta = factor.weighted_delta
        favors = "CAR" if delta > 0 else "TB"
        print(f"  {factor.name}:")
        print(f"    CAR: {factor.team1_score:.2f} | TB: {factor.team2_score:.2f} | Favors: {favors}")
        print(f"    {factor.explanation}")
        print()
