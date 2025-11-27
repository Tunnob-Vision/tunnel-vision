import random
from typing import List, Optional

import streamlit as st

from utils.models import Card, Hand, get_full_deck


def generate_random_hand() -> Hand:
    """Generate a random poker hand (2 unique cards)."""
    deck = get_full_deck()
    cards = random.sample(deck, 2)
    return Hand(cards=cards)


def _resolve_detected_hand(possible_hand: Optional[Hand]) -> Hand:
    """Ensure there is a detected hand stored in the session."""
    if possible_hand is not None:
        st.session_state["detected_hand"] = possible_hand
    elif "detected_hand" not in st.session_state:
        st.session_state["detected_hand"] = generate_random_hand()
    return st.session_state["detected_hand"]


def _default_cards_from_hand(hand: Hand, deck: List[Card]) -> List[Card]:
    """Map detected cards to their deck equivalents for the multiselect default."""
    defaults: List[Card] = []
    for detected_card in hand.cards:
        try:
            defaults.append(deck[deck.index(detected_card)])
        except ValueError:
            continue
    return defaults


def render_hand_selector(detected_hand: Optional[Hand] = None) -> None:
    """Render the hand confirmation multiselect component."""
    st.write("### Confirm your hand")

    active_hand = _resolve_detected_hand(detected_hand)

    deck = get_full_deck()
    default_cards = _default_cards_from_hand(active_hand, deck)

    selected_cards = st.multiselect(
        "Correct your hand if needed",
        options=deck,
        default=default_cards,
        format_func=str,
        max_selections=2,
    )

    st.session_state["selected_cards"] = selected_cards

    st.divider()
    if st.button("Confirm Hand", type="primary", use_container_width=True):
        if len(selected_cards) != 2:
            st.error("Please select exactly 2 cards.")
        else:
            st.session_state["player_hand"] = Hand(cards=selected_cards.copy())
            st.toast("Hand confirmed successfully!")
