import streamlit as st
import random
from utils.models import Hand, get_full_deck

def generate_random_hand() -> Hand:
    """Generate a random poker hand (2 cards)."""
    deck = get_full_deck()
    cards = random.sample(deck, 2)
    return Hand(cards=cards)

def show_game_input_page():
    st.title("Game Input")