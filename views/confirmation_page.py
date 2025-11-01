import streamlit as st
import random
from utils.models import Hand, get_full_deck


def generate_random_hand() -> Hand:
    """Generate a random poker hand (2 cards)."""
    deck = get_full_deck()
    cards = random.sample(deck, 2)
    return Hand(cards=cards)


def show_confirmation_page():
    st.title("Confirm your hand! ✅")

    if 'detected_hand' not in st.session_state:
        st.session_state['detected_hand'] = generate_random_hand()

    st.write("### We've detected the following cards:")
    st.write(", ".join(card.__str__() for card in st.session_state['detected_hand'].cards))

    full_deck = get_full_deck()

    default_cards = []
    for detected_card in st.session_state['detected_hand'].cards:
        matching_card = next(
            (card for card in full_deck if card.rank == detected_card.rank and card.suit == detected_card.suit),
            None
        )
        if matching_card:
            default_cards.append(matching_card)

    selected_cards = st.multiselect(
        "Correct your hand if needed",
        full_deck,
        default=default_cards,
        format_func=lambda card: str(card),
        max_selections=2
    )

    if 'selected_cards' not in st.session_state:
        st.session_state['selected_cards'] = []
    st.session_state['selected_cards'] = selected_cards

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Confirm Hand", type="primary", use_container_width=True):
            if len(selected_cards) != 2:
                st.error("Please select exactly 2 cards.")
            else:
                st.session_state['player_hand'] = Hand(cards=selected_cards.copy())
                st.toast("Hand confirmed successfully!", icon="✅")

    with col2:
        if st.button("🔄 Retry Analysis", use_container_width=True):
            st.session_state['current_page'] = 'upload'
            if 'detected_hand' in st.session_state:
                del st.session_state['detected_hand']
            if 'selected_cards' in st.session_state:
                del st.session_state['selected_cards']
            if 'player_hand' in st.session_state:
                del st.session_state['player_hand']
            if 'camera_photo_captured' in st.session_state:
                st.session_state['camera_photo_captured'] = False
            if 'photo' in st.session_state:
                del st.session_state['photo']
            st.rerun()
