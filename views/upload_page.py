import re
from typing import Dict, List, Optional, Tuple

import streamlit as st

from cv.src.card_detector import run_inference
from utils.models import Card, Hand, get_full_deck
from views.components.hand_selector import render_hand_selector

RANK_ALIASES: Dict[str, str] = {
    "2": "2",
    "02": "2",
    "two": "2",
    "3": "3",
    "03": "3",
    "three": "3",
    "4": "4",
    "04": "4",
    "four": "4",
    "5": "5",
    "05": "5",
    "five": "5",
    "6": "6",
    "06": "6",
    "six": "6",
    "7": "7",
    "07": "7",
    "seven": "7",
    "8": "8",
    "08": "8",
    "eight": "8",
    "9": "9",
    "09": "9",
    "nine": "9",
    "10": "10",
    "t": "10",
    "ten": "10",
    "j": "J",
    "jack": "J",
    "q": "Q",
    "queen": "Q",
    "k": "K",
    "king": "K",
    "a": "A",
    "ace": "A",
}

SUIT_ALIASES: Dict[str, str] = {
    "s": "♠",
    "spade": "♠",
    "spades": "♠",
    "♠": "♠",
    "h": "♥",
    "heart": "♥",
    "hearts": "♥",
    "♥": "♥",
    "d": "♦",
    "diamond": "♦",
    "diamonds": "♦",
    "♦": "♦",
    "c": "♣",
    "club": "♣",
    "clubs": "♣",
    "♣": "♣",
}

SUIT_ALIAS_KEYS_SORTED: List[str] = sorted(SUIT_ALIASES.keys(), key=len, reverse=True)


def _parse_card_label(label: str) -> Optional[Tuple[str, str]]:
    """Try to extract (rank, suit) from a model label."""
    if not label:
        return None

    normalized = label.strip()
    if not normalized:
        return None

    lowered = normalized.lower().replace("of", " ")
    tokens = [tok for tok in re.split(r"[^a-z0-9]+", lowered) if tok]

    rank: Optional[str] = None
    suit: Optional[str] = None

    for token in tokens:
        if rank is None:
            rank = RANK_ALIASES.get(token)
        if suit is None:
            suit = SUIT_ALIASES.get(token)

    if rank and suit:
        return rank, suit

    compact = re.sub(r"[^a-z0-9]", "", normalized.lower())
    for alias in SUIT_ALIAS_KEYS_SORTED:
        alias_compact = re.sub(r"[^a-z0-9]", "", alias.lower())
        if not alias_compact:
            continue
        if compact.endswith(alias_compact):
            rank_part = compact[: -len(alias_compact)]
            rank = RANK_ALIASES.get(rank_part)
            suit = SUIT_ALIASES.get(alias)
            if rank and suit:
                return rank, suit

    return None


def _hand_from_detections(detections: List[Dict[str, object]]) -> Optional[Hand]:
    """Convert detector outputs into a Hand if two valid cards are found."""
    deck_lookup = {(card.rank, card.suit): card for card in get_full_deck()}
    found_cards: List[Card] = []

    for detection in detections:
        label = str(detection.get("class", ""))
        parsed = _parse_card_label(label)
        if not parsed:
            continue
        card = deck_lookup.get(parsed)
        if card and card not in found_cards:
            found_cards.append(card)
        if len(found_cards) == 2:
            break

    if len(found_cards) == 2:
        return Hand(cards=found_cards.copy())
    return None


def show_upload_page():
    """Show the main upload page where users can upload or take a photo."""
    st.title("Welcome to Tunnel Vision!")
    st.write("### Start by adding a photo")

    tab1, tab2 = st.tabs(["Upload Photo", "Take Photo"])

    def process_photo(photo_file):
        """Helper to display and process uploaded/captured photo."""
        st.image(photo_file, caption="Input Photo", use_container_width=True)

        boxes_image, detections = run_inference(photo_file)
        st.image(boxes_image, caption="Detected Cards", use_container_width=True)

        detections = detections or []
        card_count = len(detections)

        if card_count == 0:
            st.error("No cards detected. Try another photo!")
        elif card_count != 2:
            st.error(f"Detected {card_count} cards. Please ensure exactly 2 cards are visible.")
        else:
            detected_hand = _hand_from_detections(detections)
            if detected_hand:
                render_hand_selector(detected_hand)
            else:
                st.error("Detected 2 cards but couldn't interpret them. Please try again.")

    with tab1:
        uploaded_photo = st.file_uploader(
            "Upload a photo from your gallery",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
        )

        if uploaded_photo is not None:
            if "photo" not in st.session_state or uploaded_photo != st.session_state.get(
                "photo"
            ):
                st.toast("Photo uploaded successfully!")
            st.session_state["photo"] = uploaded_photo
            process_photo(uploaded_photo)

    with tab2:
        if "camera_photo_captured" not in st.session_state:
            st.session_state["camera_photo_captured"] = False

        if not st.session_state["camera_photo_captured"]:
            captured_photo = st.camera_input("Capture a photo with your camera")

            if captured_photo is not None:
                st.session_state["photo"] = captured_photo
                st.session_state["camera_photo_captured"] = True
                st.session_state["show_capture_toast"] = True
                st.rerun()
        else:
            if st.button("Take Another Photo"):
                st.session_state["camera_photo_captured"] = False
                st.session_state["show_capture_toast"] = False
                st.rerun()

            if "photo" in st.session_state and st.session_state["photo"] is not None:
                if st.session_state.get("show_capture_toast", False):
                    st.toast("Photo captured successfully!")
                    st.session_state["show_capture_toast"] = False

                process_photo(st.session_state["photo"])
