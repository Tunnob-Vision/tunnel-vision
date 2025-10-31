import pytest
from utils.models import (
    Card,
    Hand,
    Community,
    PokerGameState,
    get_full_deck,
    get_remaining_cards,
    does_contain_duplicate,
)

class TestCard:
    def test_valid_card_creation(self):
        card = Card(rank="A", suit="Spades")
        assert card.rank == "A"
        assert card.suit == "Spades"

    def test_card_normalizes_rank_and_suit(self):
        card1 = Card(rank="a", suit="spades")
        assert card1.rank == "A"
        assert card1.suit == "Spades"

        card2 = Card(rank="  K  ", suit="  hearts  ")
        assert card2.rank == "K"
        assert card2.suit == "Hearts"

    def test_card_invalid_rank(self):
        with pytest.raises(ValueError, match="Invalid rank"):
            Card(rank="X", suit="Spades")

    def test_card_invalid_suit(self):
        with pytest.raises(ValueError, match="Invalid suit"):
            Card(rank="A", suit="Stars")

    def test_card_str_representation(self):
        card = Card(rank="A", suit="Spades")
        assert str(card) == "AS"

        card2 = Card(rank="10", suit="Hearts")
        assert str(card2) == "10H"

    def test_card_is_frozen(self):
        card = Card(rank="A", suit="Spades")
        with pytest.raises(Exception):
            card.rank = "K"


class TestDoesContainDuplicate:
    def test_no_duplicates(self):
        items = [1, 2, 3, 4]
        assert does_contain_duplicate(items) is False

    def test_has_duplicates(self):
        items = [1, 2, 2, 3]
        assert does_contain_duplicate(items) is True

    def test_empty_list(self):
        assert does_contain_duplicate([]) is False

    def test_single_item(self):
        assert does_contain_duplicate([1]) is False


class TestHand:
    def test_valid_hand_creation(self):
        card1 = Card(rank="A", suit="Spades")
        card2 = Card(rank="K", suit="Hearts")
        hand = Hand(cards=[card1, card2])
        assert len(hand.cards) == 2

    def test_hand_too_few_cards(self):
        card = Card(rank="A", suit="Spades")
        with pytest.raises(ValueError, match="exactly 2 cards"):
            Hand(cards=[card])

    def test_hand_too_many_cards(self):
        cards = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
            Card(rank="Q", suit="Diamonds"),
        ]
        with pytest.raises(ValueError, match="exactly 2 cards"):
            Hand(cards=cards)

    def test_hand_duplicate_cards(self):
        card = Card(rank="A", suit="Spades")
        with pytest.raises(ValueError, match="cannot contain duplicate cards"):
            Hand(cards=[card, card])


class TestCommunity:
    def test_valid_community_preflop(self):
        community = Community(cards=[])
        assert community.stage() == "Pre-Flop"

    def test_valid_community_flop(self):
        cards = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
            Card(rank="Q", suit="Diamonds"),
        ]
        community = Community(cards=cards)
        assert community.stage() == "Flop"

    def test_valid_community_turn(self):
        cards = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
            Card(rank="Q", suit="Diamonds"),
            Card(rank="J", suit="Clubs"),
        ]
        community = Community(cards=cards)
        assert community.stage() == "Turn"

    def test_valid_community_river(self):
        cards = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
            Card(rank="Q", suit="Diamonds"),
            Card(rank="J", suit="Clubs"),
            Card(rank="10", suit="Spades"),
        ]
        community = Community(cards=cards)
        assert community.stage() == "River"

    def test_community_too_many_cards(self):
        cards = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
            Card(rank="Q", suit="Diamonds"),
            Card(rank="J", suit="Clubs"),
            Card(rank="10", suit="Spades"),
            Card(rank="9", suit="Hearts"),
        ]
        with pytest.raises(ValueError, match="cannot exceed 5"):
            Community(cards=cards)

    def test_community_duplicate_cards(self):
        card = Card(rank="A", suit="Spades")
        with pytest.raises(ValueError, match="cannot contain duplicate cards"):
            Community(cards=[card, card])

    def test_community_stage_too_many_cards(self):
        cards = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
            Card(rank="Q", suit="Diamonds"),
            Card(rank="J", suit="Clubs"),
            Card(rank="10", suit="Spades"),
            Card(rank="9", suit="Hearts"),
        ]
        community = Community(cards=[Card(rank="A", suit="Spades")])
        object.__setattr__(community, "cards", cards)
        with pytest.raises(ValueError, match="cannot exceed 5"):
            community.stage()


class TestDeckFunctions:
    def test_get_full_deck(self):
        deck = get_full_deck()
        assert len(deck) == 52
        ranks = set(card.rank for card in deck)
        suits = set(card.suit for card in deck)
        assert len(ranks) == 13
        assert len(suits) == 4
        assert not does_contain_duplicate(deck)

    def test_get_remaining_cards(self):
        used = [
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
        ]
        remaining = get_remaining_cards(used)
        assert len(remaining) == 50
        for card in used:
            assert card not in remaining

    def test_get_remaining_cards_empty(self):
        remaining = get_remaining_cards([])
        assert len(remaining) == 52


class TestPokerGameState:
    def test_valid_game_state(self):
        hand = Hand(cards=[
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
        ])
        community = Community(cards=[
            Card(rank="Q", suit="Diamonds"),
            Card(rank="J", suit="Clubs"),
            Card(rank="10", suit="Spades"),
        ])
        state = PokerGameState(
            player_hand=hand,
            community=community,
            player_chips=1000,
            pot_size=500,
        )
        assert state.player_chips == 1000
        assert state.pot_size == 500

    def test_game_state_negative_chips(self):
        hand = Hand(cards=[
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
        ])
        community = Community(cards=[])
        with pytest.raises(ValueError, match="chips cannot be negative"):
            PokerGameState(
                player_hand=hand,
                community=community,
                player_chips=-100,
                pot_size=500,
            )

    def test_game_state_negative_pot(self):
        hand = Hand(cards=[
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
        ])
        community = Community(cards=[])
        with pytest.raises(ValueError, match="pot size cannot be negative"):
            PokerGameState(
                player_hand=hand,
                community=community,
                player_chips=1000,
                pot_size=-100,
            )

    def test_game_state_duplicate_between_hand_and_community(self):
        card = Card(rank="A", suit="Spades")
        hand = Hand(cards=[card, Card(rank="K", suit="Hearts")])
        community = Community(cards=[card, Card(rank="Q", suit="Diamonds")])
        with pytest.raises(ValueError, match="cannot contain duplicate cards"):
            PokerGameState(
                player_hand=hand,
                community=community,
                player_chips=1000,
                pot_size=500,
            )

    def test_game_state_zero_values(self):
        hand = Hand(cards=[
            Card(rank="A", suit="Spades"),
            Card(rank="K", suit="Hearts"),
        ])
        community = Community(cards=[])
        state = PokerGameState(
            player_hand=hand,
            community=community,
            player_chips=0,
            pot_size=0,
        )
        assert state.player_chips == 0
        assert state.pot_size == 0

