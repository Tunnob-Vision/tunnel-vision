from dataclasses import dataclass
from typing import List, TypeVar

T = TypeVar('T')

@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    def __post_init__(self):
        valid_ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        valid_suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

        object.__setattr__(self, "rank", self.rank.strip().upper())
        object.__setattr__(self, "suit", self.suit.strip().capitalize())

        if self.rank not in valid_ranks:
            raise ValueError(f"Invalid rank '{self.rank}'. Must be one of: {valid_ranks}")
        if self.suit not in valid_suits:
            raise ValueError(f"Invalid suit '{self.suit}'. Must be one of: {valid_suits}")

    def __str__(self):
        return f"{self.rank}{self.suit[0].upper()}"

def does_contain_duplicate(list: List[T]) -> bool:
    return len(set(list)) != len(list)


@dataclass
class Hand:
    cards: List[Card]

    def __post_init__(self):
        if len(self.cards) != 2:
            raise ValueError("A poker hand must have exactly 2 cards.")
        if does_contain_duplicate(self.cards):
            raise ValueError("A hand cannot contain duplicate cards.")

@dataclass
class Community:
    cards: List[Card]

    def stage(self) -> str:
        """Return the current game stage based on the number of community cards."""
        n = len(self.cards)
        if n < 3:
            return "Pre-Flop"
        elif n == 3:
            return "Flop"
        elif n == 4:
            return "Turn"
        elif n == 5:
            return "River"
        else:
            raise ValueError("The number of community cards cannot exceed 5.")

    def __post_init__(self):
        if len(self.cards) > 5:
            raise ValueError("The number of community cards cannot exceed 5.")
        if does_contain_duplicate(self.cards):
            raise ValueError("A community cannot contain duplicate cards.")


def get_full_deck() -> List[Card]:
    """Return a standard 52-card poker deck."""
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [Card(rank, suit) for suit in suits for rank in ranks]

def get_remaining_cards(used: List[Card]) -> List[Card]:
    """Return all cards in the deck that have not been used."""
    deck = get_full_deck()
    return [card for card in deck if card not in used]

@dataclass
class PokerGameState:
    player_hand: Hand
    community: Community
    player_chips: int
    pot_size: int

    def __post_init__(self):
        if self.player_chips < 0:
            raise ValueError("The player's chips cannot be negative.")
        if self.pot_size < 0:
            raise ValueError("The pot size cannot be negative.")
        if does_contain_duplicate(self.player_hand.cards + self.community.cards):
            raise ValueError("A hand and community cannot contain duplicate cards.")
