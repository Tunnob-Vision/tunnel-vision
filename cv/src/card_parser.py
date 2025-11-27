"""Utilities for converting detection labels into `Card` objects."""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from utils.models import Card

RankToken = str
SuitToken = str
Detection = Dict[str, float]

RANK_ALIASES: Dict[str, str] = {
    "2": "2",
    "3": "3",
    "4": "4",
    "5": "5",
    "6": "6",
    "7": "7",
    "8": "8",
    "9": "9",
    "10": "10",
    "T": "10",
    "J": "J",
    "JACK": "J",
    "Q": "Q",
    "QUEEN": "Q",
    "K": "K",
    "KING": "K",
    "A": "A",
    "ACE": "A",
}

SUIT_ALIASES: Dict[str, str] = {
    "H": "♥",
    "HEART": "♥",
    "HEARTS": "♥",
    "D": "♦",
    "DIAMOND": "♦",
    "DIAMONDS": "♦",
    "C": "♣",
    "CLUB": "♣",
    "CLUBS": "♣",
    "S": "♠",
    "SPADE": "♠",
    "SPADES": "♠",
}


def parse_card_label(label: str) -> Optional[Card]:
    """Best-effort parser turning detector labels into `Card` objects."""

    if not label:
        return None

    label_clean = label.strip()
    card = _parse_compact_form(label_clean)
    if card:
        return card

    tokens = re.split(r"[\s_/-]+", label_clean.lower())
    tokens = [tok for tok in tokens if tok and tok not in {"of", "the"}]
    if not tokens:
        return None

    rank = _find_rank(tokens)
    suit = _find_suit(tokens)

    if rank and suit:
        return _build_card(rank, suit)

    return None


def detections_to_cards(
    detections: Sequence[Detection],
    max_cards: int = 2,
) -> List[Tuple[Card, float]]:
    """Deduplicate detections and keep highest-confidence cards."""

    best: Dict[str, Tuple[Card, float]] = {}
    for det in detections:
        label = det.get("class") if isinstance(det, dict) else None
        conf = float(det.get("confidence", 0.0)) if isinstance(det, dict) else 0.0
        if not label:
            continue
        card = parse_card_label(str(label))
        if not card:
            continue
        key = str(card)
        if key not in best or conf > best[key][1]:
            best[key] = (card, conf)

    ordered = sorted(best.values(), key=lambda pair: pair[1], reverse=True)
    return ordered[:max_cards]


def _parse_compact_form(label: str) -> Optional[Card]:
    compact = re.sub(r"[^0-9A-Za-z]", "", label).upper()
    if not compact:
        return None
    match = re.fullmatch(r"(10|[2-9]|[TJQKA])([CDHS])", compact)
    if match:
        rank_token, suit_token = match.groups()
        return _build_card(rank_token, suit_token)
    return None


def _find_rank(tokens: Iterable[str]) -> Optional[str]:
    for tok in tokens:
        candidate = tok.upper()
        if candidate.isdigit() and candidate == "1":
            continue
        if candidate in RANK_ALIASES:
            return RANK_ALIASES[candidate]
    return None


def _find_suit(tokens: Iterable[str]) -> Optional[str]:
    for tok in tokens:
        candidate = tok.upper()
        if candidate in SUIT_ALIASES:
            return SUIT_ALIASES[candidate]
    return None


def _build_card(rank_token: RankToken, suit_token: SuitToken) -> Optional[Card]:
    rank = RANK_ALIASES.get(rank_token.upper(), rank_token.upper())
    suit = SUIT_ALIASES.get(suit_token.upper())
    if not suit:
        return None
    try:
        return Card(rank=rank, suit=suit)
    except ValueError:
        return None


__all__ = ["detections_to_cards", "parse_card_label"]
