"""
Monte Carlo Simulation for NFL Game Prediction
Panthers vs Buccaneers - Week 18, January 3, 2026

This module runs thousands of simulated games to provide:
- Win probability distributions
- Score range predictions
- Confidence intervals
"""

import random
import math
from collections import Counter
from typing import Tuple, List, Dict

from game_data import PANTHERS, BUCCANEERS, BETTING_DATA


class MonteCarloSimulator:
    """
    Run Monte Carlo simulations for game outcome prediction
    """

    def __init__(self, num_simulations: int = 10000):
        self.num_simulations = num_simulations

        # Base parameters derived from weighted model
        self.base_panthers_win_prob = 0.56
        self.expected_panthers_score = 22.5
        self.expected_bucs_score = 21.0

        # Score variance parameters (NFL games typically have std dev of ~10 points)
        self.score_std_dev = 9.5

        # Factor uncertainty ranges
        self.uncertainty_factors = {
            "game_script_variance": 0.08,      # Play calling changes based on score
            "turnover_luck": 0.10,             # Turnovers are somewhat random
            "weather_variance": 0.02,          # Minor for indoor-like conditions
            "ref_variance": 0.03,              # Penalties can swing games
            "injury_game_day": 0.05,           # In-game injuries
        }

    def simulate_game(self) -> Tuple[int, int, str]:
        """
        Simulate a single game, returning (panthers_score, bucs_score, winner)
        """
        # Add uncertainty to base win probability
        uncertainty = sum(random.gauss(0, v) for v in self.uncertainty_factors.values())
        adjusted_win_prob = self.base_panthers_win_prob + uncertainty
        adjusted_win_prob = max(0.25, min(0.75, adjusted_win_prob))

        # Simulate scores with correlation
        # Higher probability of winning correlates with higher expected score
        panthers_adjustment = (adjusted_win_prob - 0.5) * 6
        bucs_adjustment = -panthers_adjustment

        panthers_score = random.gauss(
            self.expected_panthers_score + panthers_adjustment,
            self.score_std_dev
        )
        bucs_score = random.gauss(
            self.expected_bucs_score + bucs_adjustment,
            self.score_std_dev
        )

        # Round and ensure non-negative
        panthers_score = max(0, round(panthers_score))
        bucs_score = max(0, round(bucs_score))

        # Determine winner (handle ties with OT simulation)
        if panthers_score > bucs_score:
            winner = "Panthers"
        elif bucs_score > panthers_score:
            winner = "Buccaneers"
        else:
            # Overtime - 50/50 with slight edge to momentum
            if random.random() < adjusted_win_prob:
                panthers_score += 3  # Field goal
                winner = "Panthers"
            else:
                bucs_score += 3
                winner = "Buccaneers"

        return panthers_score, bucs_score, winner

    def run_simulations(self) -> Dict:
        """
        Run all simulations and compile results
        """
        results = []
        panthers_wins = 0
        bucs_wins = 0
        panthers_covers = 0
        overs = 0

        panthers_scores = []
        bucs_scores = []
        margins = []

        for _ in range(self.num_simulations):
            p_score, b_score, winner = self.simulate_game()
            results.append((p_score, b_score, winner))

            panthers_scores.append(p_score)
            bucs_scores.append(b_score)

            margin = p_score - b_score
            margins.append(margin)

            if winner == "Panthers":
                panthers_wins += 1
            else:
                bucs_wins += 1

            # Against the spread (Panthers +2.5)
            if margin > -2.5:
                panthers_covers += 1

            # Over/Under (43.5)
            if p_score + b_score > 43.5:
                overs += 1

        # Calculate statistics
        return {
            "simulations": self.num_simulations,
            "panthers_win_pct": panthers_wins / self.num_simulations,
            "bucs_win_pct": bucs_wins / self.num_simulations,
            "panthers_cover_pct": panthers_covers / self.num_simulations,
            "over_pct": overs / self.num_simulations,
            "avg_panthers_score": sum(panthers_scores) / len(panthers_scores),
            "avg_bucs_score": sum(bucs_scores) / len(bucs_scores),
            "avg_margin": sum(margins) / len(margins),
            "margin_std_dev": self.calculate_std_dev(margins),
            "score_distribution": self.get_score_distribution(results),
            "margin_percentiles": self.calculate_percentiles(margins),
            "most_common_scores": self.get_most_common_scores(results),
        }

    def calculate_std_dev(self, values: List[float]) -> float:
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

    def calculate_percentiles(self, margins: List[float]) -> Dict:
        sorted_margins = sorted(margins)
        n = len(sorted_margins)
        return {
            "5th": sorted_margins[int(n * 0.05)],
            "25th": sorted_margins[int(n * 0.25)],
            "50th (median)": sorted_margins[int(n * 0.50)],
            "75th": sorted_margins[int(n * 0.75)],
            "95th": sorted_margins[int(n * 0.95)],
        }

    def get_score_distribution(self, results: List[Tuple]) -> Dict:
        """Get distribution of game outcomes"""
        outcomes = {
            "panthers_blowout": 0,  # Win by 14+
            "panthers_comfortable": 0,  # Win by 7-13
            "panthers_close": 0,  # Win by 1-6
            "bucs_close": 0,  # Win by 1-6
            "bucs_comfortable": 0,  # Win by 7-13
            "bucs_blowout": 0,  # Win by 14+
        }

        for p_score, b_score, _ in results:
            margin = p_score - b_score
            if margin >= 14:
                outcomes["panthers_blowout"] += 1
            elif margin >= 7:
                outcomes["panthers_comfortable"] += 1
            elif margin > 0:
                outcomes["panthers_close"] += 1
            elif margin > -7:
                outcomes["bucs_close"] += 1
            elif margin > -14:
                outcomes["bucs_comfortable"] += 1
            else:
                outcomes["bucs_blowout"] += 1

        # Convert to percentages
        return {k: v / len(results) for k, v in outcomes.items()}

    def get_most_common_scores(self, results: List[Tuple], top_n: int = 5) -> List[Tuple]:
        """Get most common final scores"""
        score_counter = Counter((r[0], r[1]) for r in results)
        return score_counter.most_common(top_n)


def run_full_analysis():
    """Run complete Monte Carlo analysis and display results"""

    print("=" * 70)
    print("MONTE CARLO SIMULATION ANALYSIS")
    print("Panthers @ Buccaneers - Week 18, January 3, 2026")
    print("=" * 70)
    print()

    simulator = MonteCarloSimulator(num_simulations=10000)
    results = simulator.run_simulations()

    print(f"Simulations Run: {results['simulations']:,}")
    print()

    print("WIN PROBABILITIES")
    print("-" * 40)
    print(f"Panthers Win: {results['panthers_win_pct']:.1%}")
    print(f"Buccaneers Win: {results['bucs_win_pct']:.1%}")
    print()

    print("BETTING ANALYSIS")
    print("-" * 40)
    print(f"Panthers Cover +2.5: {results['panthers_cover_pct']:.1%}")
    print(f"Over 43.5: {results['over_pct']:.1%}")
    print(f"Under 43.5: {1 - results['over_pct']:.1%}")
    print()

    print("SCORE PREDICTIONS")
    print("-" * 40)
    print(f"Average Panthers Score: {results['avg_panthers_score']:.1f}")
    print(f"Average Buccaneers Score: {results['avg_bucs_score']:.1f}")
    print(f"Average Margin: {'Panthers' if results['avg_margin'] > 0 else 'Buccaneers'} by {abs(results['avg_margin']):.1f}")
    print(f"Margin Std Dev: {results['margin_std_dev']:.1f} points")
    print()

    print("MARGIN PERCENTILES (Panthers perspective)")
    print("-" * 40)
    for pct, value in results['margin_percentiles'].items():
        direction = "Panthers +" if value > 0 else "Buccaneers +"
        print(f"  {pct}: {direction}{abs(value)}")
    print()

    print("OUTCOME DISTRIBUTION")
    print("-" * 40)
    dist = results['score_distribution']
    print(f"  Panthers Blowout (14+): {dist['panthers_blowout']:.1%}")
    print(f"  Panthers Comfortable (7-13): {dist['panthers_comfortable']:.1%}")
    print(f"  Panthers Close (1-6): {dist['panthers_close']:.1%}")
    print(f"  Buccaneers Close (1-6): {dist['bucs_close']:.1%}")
    print(f"  Buccaneers Comfortable (7-13): {dist['bucs_comfortable']:.1%}")
    print(f"  Buccaneers Blowout (14+): {dist['bucs_blowout']:.1%}")
    print()

    print("MOST COMMON FINAL SCORES")
    print("-" * 40)
    for (p_score, b_score), count in results['most_common_scores']:
        pct = count / results['simulations'] * 100
        print(f"  Panthers {p_score} - Buccaneers {b_score}: {pct:.1f}%")
    print()

    return results


if __name__ == "__main__":
    run_full_analysis()
