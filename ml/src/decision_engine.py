"""Decision-making scaffold for Tunnel Vision's poker assistant.

This module exposes a simple API that converts a structured
`PokerGameState` plus contextual metadata into an actionable
recommendation. The current implementation uses lightweight heuristics
so the UI can be wired end-to-end before the real ML/RL models land.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Literal, Optional

from utils.models import Card, Community, Hand, PokerGameState
from ml.src.equity import EquityEstimate, estimate_equity

StrategyProfile = Literal["tight", "balanced", "aggressive"]
ActionType = Literal["fold", "call", "raise"]


class Street(Enum):
    PRE_FLOP = "Pre-Flop"
    FLOP = "Flop"
    TURN = "Turn"
    RIVER = "River"

    @staticmethod
    def from_community(community: Community) -> "Street":
        return Street(community.stage())


@dataclass
class DecisionContext:
    """Optional metadata used by the decision engine."""

    opponent_range: Optional[Dict[str, float]] = None
    pot_to_call: Optional[int] = None
    min_raise: Optional[int] = None
    strategy_profile: StrategyProfile = "balanced"
    equity_samples: int = 2000
    num_opponents: int = 1
    notes: Optional[str] = None


@dataclass
class DecisionResult:
    """Structured output consumed by the UI."""

    action: ActionType
    confidence: float
    recommended_bet: Optional[int] = None
    rationale: List[str] = field(default_factory=list)
    strategy_profile: StrategyProfile = "balanced"
    equity: Optional[float] = None


class DecisionEngine:
    """Placeholder decision engine until ML models are trained."""

    def __init__(self) -> None:
        self._rank_strength = {
            "2": 0.05,
            "3": 0.08,
            "4": 0.11,
            "5": 0.14,
            "6": 0.18,
            "7": 0.22,
            "8": 0.26,
            "9": 0.3,
            "10": 0.36,
            "J": 0.42,
            "Q": 0.5,
            "K": 0.58,
            "A": 0.68,
        }

    def recommend_action(
        self,
        state: PokerGameState,
        context: Optional[DecisionContext] = None,
    ) -> DecisionResult:
        context = context or DecisionContext()
        street = Street.from_community(state.community)
        rationale = [f"Street: {street.value}"]
        equity_info = self._maybe_estimate_equity(state, context)
        if equity_info:
            strength = equity_info.equity
            rationale.append(
                f"Equity vs {context.num_opponents} opp(s): {strength:.0%} "
                f"(samples: {equity_info.trials})"
            )
        else:
            strength = self._estimate_strength(state.player_hand, state.community)
            rationale.append("Equity fallback: heuristic strength used.")
        pot_odds = self._compute_pot_odds(state.pot_size, context.pot_to_call)
        rationale.append(f"Effective strength: {strength:.0%}")

        if pot_odds is not None:
            rationale.append(f"Pot odds: {pot_odds:.2f}")

        action, confidence = self._apply_policy(
            strength=strength,
            pot_odds=pot_odds,
            strategy=context.strategy_profile,
        )

        bet = None
        if action == "raise":
            bet = self._suggest_bet(state, context)
            if bet:
                rationale.append(f"Suggested bet: {bet}")

        rationale.extend(self._strategy_notes(action, context.strategy_profile))

        return DecisionResult(
            action=action,
            confidence=confidence,
            recommended_bet=bet,
            rationale=rationale,
            strategy_profile=context.strategy_profile,
            equity=strength if equity_info else None,
        )

    # --- Heuristic helpers -------------------------------------------------

    def _maybe_estimate_equity(
        self, state: PokerGameState, context: DecisionContext
    ) -> Optional[EquityEstimate]:
        try:
            return estimate_equity(
                state,
                opponents=max(1, context.num_opponents),
                trials=max(200, context.equity_samples),
            )
        except ValueError:
            return None

    def _estimate_strength(self, hand: Hand, community: Community) -> float:
        """Very rough estimate of hero strength in [0, 1]."""

        ranks = [card.rank for card in hand.cards]
        base = sum(self._rank_strength.get(rank, 0.1) for rank in ranks) / 2

        if hand.cards[0].rank == hand.cards[1].rank:
            base += 0.2  # pocket pair bonus
        if hand.cards[0].suit == hand.cards[1].suit:
            base += 0.05  # suited bonus

        # Community adjustments
        board = community.cards
        if not board:
            return min(base, 0.95)

        board_ranks = [card.rank for card in board]
        board_values = sum(self._rank_strength.get(rank, 0.1) for rank in board_ranks)
        base += board_values / 10

        # simple made-hand checks
        combined = hand.cards + board
        if self._has_pair(combined):
            base += 0.05
        if self._has_flush_draw(combined):
            base += 0.04
        if self._has_straight_draw(combined):
            base += 0.04

        return max(0.05, min(base, 0.99))

    @staticmethod
    def _has_pair(cards: List[Card]) -> bool:
        ranks = [card.rank for card in cards]
        return len(ranks) != len(set(ranks))

    @staticmethod
    def _has_flush_draw(cards: List[Card]) -> bool:
        if len(cards) < 4:
            return False
        suits = {}
        for card in cards:
            suits[card.suit] = suits.get(card.suit, 0) + 1
        return max(suits.values()) >= 4

    def _has_straight_draw(self, cards: List[Card]) -> bool:
        rank_order = list(self._rank_strength.keys())
        indices = sorted({rank_order.index(card.rank) for card in cards})
        run = 1
        best = 1
        for prev, curr in zip(indices, indices[1:]):
            if curr - prev == 1:
                run += 1
                best = max(best, run)
            else:
                run = 1
        return best >= 4

    @staticmethod
    def _compute_pot_odds(pot_size: int, to_call: Optional[int]) -> Optional[float]:
        if to_call is None or to_call <= 0:
            return None
        return to_call / (pot_size + to_call)

    def _apply_policy(
        self,
        strength: float,
        pot_odds: Optional[float],
        strategy: StrategyProfile,
    ) -> tuple[ActionType, float]:
        fold_thresh = 0.38
        raise_thresh = 0.65

        if strategy == "tight":
            fold_thresh += 0.05
            raise_thresh += 0.05
        elif strategy == "aggressive":
            fold_thresh -= 0.05
            raise_thresh -= 0.08

        if strength <= fold_thresh and (pot_odds is None or strength < pot_odds):
            confidence = 1 - strength
            return "fold", max(0.2, min(confidence, 0.95))
        if strength >= raise_thresh:
            confidence = strength
            return "raise", max(0.4, min(confidence, 0.95))
        confidence = 0.5 + (strength - fold_thresh) / (raise_thresh - fold_thresh + 1e-6) * 0.3
        return "call", max(0.3, min(confidence, 0.9))

    def _suggest_bet(self, state: PokerGameState, context: DecisionContext) -> Optional[int]:
        min_raise = context.min_raise or max(int(state.pot_size * 0.5), 1)
        pot_goal = int(state.pot_size * 0.75)
        return max(min_raise, pot_goal)

    @staticmethod
    def _strategy_notes(action: ActionType, profile: StrategyProfile) -> List[str]:
        notes = [f"Profile: {profile.title()}"]
        if profile == "tight" and action != "fold":
            notes.append("Tight mode still allows aggression when strength is solid.")
        if profile == "aggressive" and action != "raise":
            notes.append("Aggressive mode tempered due to low confidence.")
        return notes


def get_decision_engine() -> DecisionEngine:
    """Convenience factory for Streamlit caching."""

    return DecisionEngine()


__all__ = [
    "DecisionEngine",
    "DecisionContext",
    "DecisionResult",
    "StrategyProfile",
    "get_decision_engine",
]
