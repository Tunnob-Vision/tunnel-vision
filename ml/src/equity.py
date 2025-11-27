"""Monte Carlo equity estimation utilities."""
from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, List, Optional, Sequence, Tuple

from utils.models import Card, Community, Hand, PokerGameState, get_remaining_cards

RANK_ORDER = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


@dataclass(frozen=True, order=True)
class HandScore:
    """Comparable representation of a 5-card poker hand."""

    category: int  # higher is better
    ranks: Tuple[int, ...]


@dataclass
class EquityEstimate:
    equity: float
    wins: int
    ties: int
    trials: int


@dataclass
class HandStrengthDetails:
    label: str
    category: int
    percentile: Optional[float]
    score: HandScore


def estimate_equity(
    state: PokerGameState,
    opponents: int = 1,
    trials: int = 2000,
) -> EquityEstimate:
    """Monte Carlo estimate of hero equity versus `opponents` random hands."""

    if opponents < 1:
        raise ValueError("Number of opponents must be at least 1.")
    hero_cards = state.player_hand.cards
    board_cards = state.community.cards
    remaining = get_remaining_cards(hero_cards + board_cards)
    missing_board = 5 - len(board_cards)
    cards_needed = opponents * 2 + missing_board

    if cards_needed > len(remaining):
        raise ValueError("Not enough cards remaining to complete simulation.")

    total_combos = math.comb(len(remaining), cards_needed)
    run_all = total_combos <= trials
    wins = ties = 0
    actual_trials = total_combos if run_all else trials

    if run_all:
        samples = combinations(remaining, cards_needed)
    else:
        samples = (_random_sample(remaining, cards_needed) for _ in range(trials))

    for sample in samples:
        board_extra = sample[:missing_board]
        idx = missing_board
        board = board_cards + list(board_extra)
        hero_score = evaluate_best_hand(hero_cards + board)
        best_villain = None
        for _ in range(opponents):
            villain_cards = sample[idx : idx + 2]
            idx += 2
            score = evaluate_best_hand(list(villain_cards) + board)
            if best_villain is None or score > best_villain:
                best_villain = score
        if hero_score > best_villain:
            wins += 1
        elif hero_score == best_villain:
            ties += 1

    equity = (wins + ties / 2) / actual_trials if actual_trials else 0.0
    return EquityEstimate(equity=equity, wins=wins, ties=ties, trials=actual_trials)


def evaluate_best_hand(cards: Sequence[Card]) -> HandScore:
    """Return the best 5-card score from up to 7 cards."""

    if len(cards) < 5:
        raise ValueError("Need at least 5 cards to evaluate a hand.")

    best = None
    for combo in combinations(cards, 5):
        score = _score_five_cards(combo)
        if best is None or score > best:
            best = score
    return best


def _score_five_cards(cards: Iterable[Card]) -> HandScore:
    ranks = sorted((RANK_ORDER[card.rank] for card in cards), reverse=True)
    suits = [card.suit for card in cards]
    counts = Counter(ranks)
    is_flush = len(set(suits)) == 1
    straight_high = _straight_high(ranks)

    if is_flush and straight_high:
        return HandScore(8, (straight_high,))

    max_count = max(counts.values())
    if max_count == 4:
        quad_rank = max(rank for rank, cnt in counts.items() if cnt == 4)
        kicker = max(rank for rank, cnt in counts.items() if cnt == 1)
        return HandScore(7, (quad_rank, kicker))

    if sorted(counts.values(), reverse=True)[:2] == [3, 2]:
        trip_rank = max(rank for rank, cnt in counts.items() if cnt == 3)
        pair_rank = max(rank for rank, cnt in counts.items() if cnt == 2)
        return HandScore(6, (trip_rank, pair_rank))

    if is_flush:
        return HandScore(5, tuple(sorted(ranks, reverse=True)))

    if straight_high:
        return HandScore(4, (straight_high,))

    if max_count == 3:
        trip_rank = max(rank for rank, cnt in counts.items() if cnt == 3)
        kickers = sorted((rank for rank, cnt in counts.items() if cnt == 1), reverse=True)[:2]
        return HandScore(3, (trip_rank, *kickers))

    pair_ranks = sorted((rank for rank, cnt in counts.items() if cnt == 2), reverse=True)
    if len(pair_ranks) >= 2:
        kicker = max(rank for rank, cnt in counts.items() if cnt == 1)
        return HandScore(2, (pair_ranks[0], pair_ranks[1], kicker))

    if len(pair_ranks) == 1:
        pair_rank = pair_ranks[0]
        kickers = sorted((rank for rank, cnt in counts.items() if cnt == 1), reverse=True)[:3]
        return HandScore(1, (pair_rank, *kickers))

    return HandScore(0, tuple(sorted(ranks, reverse=True)))


def _straight_high(ranks: List[int]) -> int | None:
    unique = sorted(set(ranks))
    if 14 in unique:
        unique.append(1)
    unique = sorted(unique)
    run = 1
    best = None
    for prev, curr in zip(unique, unique[1:]):
        if curr - prev == 1:
            run += 1
            if run >= 5:
                best = curr
        else:
            run = 1
    if best == 1:
        return 5  # wheel straight
    return best


def _random_sample(seq: Sequence[Card], n: int) -> Tuple[Card, ...]:
    return tuple(random.sample(list(seq), n))


HAND_CATEGORY_LABELS = {
    8: "Straight Flush",
    7: "Four of a Kind",
    6: "Full House",
    5: "Flush",
    4: "Straight",
    3: "Three of a Kind",
    2: "Two Pair",
    1: "One Pair",
    0: "High Card",
}


def describe_made_hand(
    hand: Hand,
    community: Community,
    percentile_samples: int = 4000,
) -> Optional[HandStrengthDetails]:
    """Return a label and percentile for the player's current made hand."""

    total_cards = hand.cards + community.cards
    if len(total_cards) < 5:
        return None
    score = evaluate_best_hand(total_cards)
    label = _score_to_label(score)
    percentile = _estimate_percentile_against_other_hands(
        score=score,
        hand=hand,
        community=community,
        samples=percentile_samples,
    )
    return HandStrengthDetails(
        label=label,
        category=score.category,
        percentile=percentile,
        score=score,
    )


def _score_to_label(score: HandScore) -> str:
    if score.category == 8 and score.ranks and score.ranks[0] == 14:
        return "Royal Flush"
    return HAND_CATEGORY_LABELS.get(score.category, "Unknown")


def _estimate_percentile_against_other_hands(
    score: HandScore,
    hand: Hand,
    community: Community,
    samples: int,
) -> Optional[float]:
    board = community.cards
    if len(board) < 3:
        return None
    remaining = get_remaining_cards(hand.cards + board)
    total_combos = math.comb(len(remaining), 2)
    if total_combos == 0:
        return None
    run_all = total_combos <= samples
    iterator: Iterable[Tuple[Card, ...]]
    if run_all:
        iterator = combinations(remaining, 2)
        denom = total_combos
    else:
        iterator = (_random_sample(remaining, 2) for _ in range(samples))
        denom = samples

    better = ties = 0
    for combo in iterator:
        opp_score = evaluate_best_hand(list(combo) + board)
        if opp_score > score:
            better += 1
        elif opp_score == score:
            ties += 1

    percentile = 1 - (better + ties / 2) / denom if denom else None
    if percentile is None:
        return None
    return max(0.0, min(1.0, percentile))


__all__ = [
    "EquityEstimate",
    "HandScore",
    "estimate_equity",
    "evaluate_best_hand",
    "HandStrengthDetails",
    "describe_made_hand",
]
