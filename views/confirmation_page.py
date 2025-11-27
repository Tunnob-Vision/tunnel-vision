import random
import streamlit as st
from typing import List, Optional

from utils.models import Card, Community, Hand, PokerGameState, get_full_deck, get_remaining_cards
from ml.src.decision_engine import (
    DecisionContext,
    DecisionResult,
    get_decision_engine,
)
from ml.src.equity import describe_made_hand


def validate_card_selection(
    player_cards: List[Card],
    community_cards: List[Card]
) -> tuple[bool, Optional[str]]:
    """Validate that there are no duplicate cards between player hand and community.

    Returns:
        Tuple of (is_valid, error_message)
    """
    all_cards = player_cards + community_cards

    seen = set()
    for card in all_cards:
        card_str = str(card)
        if card_str in seen:
            return False, f"Duplicate card detected: {card_str}"
        seen.add(card_str)

    return True, None


def get_street_from_card_count(count: int) -> str:
    """Get the poker street name based on community card count."""
    if count == 0:
        return "Pre-Flop"
    elif count == 3:
        return "Flop"
    elif count == 4:
        return "Turn"
    elif count == 5:
        return "River"
    else:
        return f"{count} cards"


def generate_random_hand() -> Hand:
    """Generate a random poker hand (2 cards)."""
    deck = get_full_deck()
    cards = random.sample(deck, 2)
    return Hand(cards=cards)

@st.cache_resource
def _get_engine():
    return get_decision_engine()


def show_confirmation_page():
    # Check if coming from photo upload or manual entry
    from_photo_upload = 'detected_cards' in st.session_state and st.session_state.get('detected_cards')

    if from_photo_upload:
        st.title("Confirm your hand! ✅")

        if 'detected_hand' not in st.session_state:
            detected_cards = st.session_state.get('detected_cards', [])
            if detected_cards and len(detected_cards) >= 2:
                st.session_state['detected_hand'] = Hand(
                    cards=[detected_cards[0], detected_cards[1]]
                )
            else:
                st.session_state['detected_hand'] = generate_random_hand()

        st.write("### We've detected the following cards:")
        st.write(", ".join(card.__str__() for card in st.session_state['detected_hand'].cards))
    else:
        st.title("Game State Input 🎰")
        st.write("### Enter your hand and game information")

    full_deck = get_full_deck()

    # Set default cards based on source
    default_cards = []
    if from_photo_upload and 'detected_hand' in st.session_state:
        for detected_card in st.session_state['detected_hand'].cards:
            matching_card = next(
                (card for card in full_deck if card.rank == detected_card.rank and card.suit == detected_card.suit),
                None
            )
            if matching_card:
                default_cards.append(matching_card)
    elif 'player_hand' in st.session_state and st.session_state['player_hand']:
        default_cards = st.session_state['player_hand'].cards

    label = "Correct your hand if needed" if from_photo_upload else "Select your 2 hole cards"
    selected_cards = st.multiselect(
        label,
        full_deck,
        default=default_cards,
        format_func=lambda card: str(card),
        max_selections=2
    )

    if 'selected_cards' not in st.session_state:
        st.session_state['selected_cards'] = []
    st.session_state['selected_cards'] = selected_cards

    # Show success message when 2 cards selected
    if len(selected_cards) == 2:
        st.success(f"✓ Your hand: {selected_cards[0]} {selected_cards[1]}")
    elif len(selected_cards) > 0:
        st.warning(f"Select exactly 2 cards (currently: {len(selected_cards)})")

    st.divider()

    # Street Selector (for manual entry mode)
    if not from_photo_upload:
        st.subheader("2️⃣ Game Street")

        street_options = {
            "Pre-Flop": 0,
            "Flop": 3,
            "Turn": 4,
            "River": 5
        }

        selected_street = st.selectbox(
            "Select the current street",
            options=list(street_options.keys()),
            index=st.session_state.get('selected_street_idx', 0),
            key="street_selector"
        )
        st.session_state['selected_street_idx'] = list(street_options.keys()).index(selected_street)
        max_community_cards = street_options[selected_street]

        st.divider()
        st.subheader("3️⃣ Community Cards (Board)")
    else:
        st.subheader("Community Cards (Board)")
        max_community_cards = 5

    if not from_photo_upload and max_community_cards == 0:
        st.info("Pre-Flop: No community cards yet")
        community_cards = []
    else:
        available_cards = get_remaining_cards(selected_cards) if selected_cards else full_deck

        community_defaults = st.session_state.get('community_cards', [])
        community_defaults = [c for c in community_defaults if c in available_cards]

        community_cards = st.multiselect(
            f"Select up to {max_community_cards} community cards" if not from_photo_upload else "Select board cards (optional)",
            available_cards,
            default=community_defaults[:max_community_cards],
            format_func=lambda card: str(card),
            max_selections=max_community_cards,
        )

        if len(community_cards) >= 3:
            cols = st.columns(5)
            for i, card in enumerate(community_cards):
                with cols[i]:
                    if i < 3:
                        st.markdown(f"**Flop**")
                    elif i == 3:
                        st.markdown(f"**Turn**")
                    elif i == 4:
                        st.markdown(f"**River**")
                    st.markdown(f"### {card}")

        if selected_cards and community_cards:
            is_valid, error_msg = validate_card_selection(selected_cards, community_cards)
            if not is_valid:
                st.error(f"❌ {error_msg}")

    st.session_state['community_cards'] = community_cards

    render_hand_summary()

    st.divider()

    # Show appropriate action buttons for photo upload mode
    if from_photo_upload:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Confirm Hand", type="primary", width="stretch"):
                if len(selected_cards) != 2:
                    st.error("Please select exactly 2 cards.")
                else:
                    st.session_state['player_hand'] = Hand(cards=selected_cards.copy())
                    st.toast("Hand confirmed successfully!", icon="✅")

        with col2:
            if st.button("🔄 Retry Analysis", width="stretch"):
                st.session_state['current_page'] = 'upload'
                for key in [
                    'detected_hand', 'selected_cards', 'player_hand', 'community_cards',
                    'decision_result', 'player_stack', 'pot_size', 'amount_to_call',
                    'min_raise', 'strategy_profile', 'opponent_notes', 'detected_cards',
                    'num_opponents', 'player_position', 'player_position_idx', 'selected_street_idx'
                ]:
                    st.session_state.pop(key, None)
                if 'camera_photo_captured' in st.session_state:
                    st.session_state['camera_photo_captured'] = False
                if 'photo' in st.session_state:
                    del st.session_state['photo']
                st.rerun()

    st.divider()
    st.subheader("4️⃣ Betting Information" if not from_photo_upload else "Game Context")

    col1, col2 = st.columns(2)

    with col1:
        pot_size = st.number_input(
            "Current pot size (chips)",
            min_value=0,
            value=st.session_state.get('pot_size', 50),
            step=5
        )
        st.session_state['pot_size'] = pot_size

        amount_to_call = st.number_input(
            "Amount to call (chips)",
            min_value=0,
            value=st.session_state.get('amount_to_call', 10),
            step=5
        )
        st.session_state['amount_to_call'] = amount_to_call

    with col2:
        player_stack = st.number_input(
            "Your stack (chips)",
            min_value=1,
            value=st.session_state.get('player_stack', 1000),
            step=10
        )
        st.session_state['player_stack'] = player_stack

        min_raise = st.number_input(
            "Minimum raise size (chips)",
            min_value=1,
            value=st.session_state.get('min_raise', max(10, amount_to_call * 2)),
            step=5
        )
        st.session_state['min_raise'] = min_raise

    st.divider()
    st.subheader("5️⃣ Table Information" if not from_photo_upload else "Table Information")

    col1, col2 = st.columns(2)

    with col1:
        position_options = ["Early", "Middle", "Late", "Blinds"]
        player_position = st.selectbox(
            "Your position",
            options=position_options,
            index=st.session_state.get('player_position_idx', 2)
        )
        st.session_state['player_position_idx'] = position_options.index(player_position)
        st.session_state['player_position'] = player_position

    with col2:
        num_opponents = st.number_input(
            "Number of active opponents",
            min_value=1,
            max_value=9,
            value=st.session_state.get('num_opponents', 2),
            step=1
        )
        st.session_state['num_opponents'] = num_opponents

    st.divider()
    st.subheader("6️⃣ Strategy & Notes" if not from_photo_upload else "Strategy Profile")

    strategy_options = ["tight", "balanced", "aggressive"]
    default_strategy = st.session_state.get('strategy_profile', 'balanced')
    if default_strategy not in strategy_options:
        default_strategy = "balanced"
    strategy_profile = st.selectbox(
        "Strategy profile",
        strategy_options,
        index=strategy_options.index(default_strategy)
    )
    st.session_state['strategy_profile'] = strategy_profile

    opponent_notes = st.text_area(
        "Opponent notes / observations (optional)",
        value=st.session_state.get('opponent_notes', ""),
        placeholder="e.g., 'Player to left is very aggressive', 'Tight table'"
    )
    st.session_state['opponent_notes'] = opponent_notes

    # Summary section
    if not from_photo_upload:
        st.divider()
        st.subheader("7️⃣ Summary")

        summary_cols = st.columns(3)

        with summary_cols[0]:
            street_display = get_street_from_card_count(len(community_cards))
            st.metric("Street", street_display)
            st.metric("Position", player_position)

        with summary_cols[1]:
            st.metric("Pot Size", f"{pot_size} chips")
            st.metric("To Call", f"{amount_to_call} chips")

        with summary_cols[2]:
            st.metric("Your Stack", f"{player_stack} chips")
            st.metric("Opponents", num_opponents)

    st.divider()

    # Action buttons
    if not from_photo_upload:
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 Reset Form", width="stretch"):
                keys_to_clear = [
                    'selected_cards', 'player_hand', 'community_cards',
                    'decision_result', 'player_stack', 'pot_size',
                    'amount_to_call', 'min_raise', 'strategy_profile',
                    'opponent_notes', 'num_opponents', 'player_position',
                    'player_position_idx', 'selected_street_idx'
                ]
                for key in keys_to_clear:
                    st.session_state.pop(key, None)
                st.rerun()

        with col2:
            if st.button("💾 Save Game State", type="secondary", width="stretch"):
                if len(selected_cards) != 2:
                    st.error("Please select exactly 2 hole cards")
                else:
                    st.session_state['player_hand'] = Hand(cards=selected_cards.copy())
                    st.toast("Game state saved successfully!", icon="✅")

        with col3:
            get_recommendation_button = st.button("💡 Get AI Recommendation", type="primary", width="stretch")
    else:
        get_recommendation_button = st.button("💡 Get AI Recommendation", type="primary", width="stretch")

    engine = _get_engine()

    if get_recommendation_button:
        if len(selected_cards) != 2:
            st.error("❌ Please select exactly 2 hole cards")
        elif not from_photo_upload and 'street_options' in locals():
            expected = street_options.get(selected_street, 0)
            if len(community_cards) != expected and expected > 0:
                st.error(f"❌ {selected_street} requires exactly {expected} community cards (you have {len(community_cards)})")
            else:
                # Validate no duplicates
                is_valid, error_msg = validate_card_selection(selected_cards, community_cards)
                if not is_valid:
                    st.error(f"❌ {error_msg}")
                else:
                    # Update player hand
                    st.session_state['player_hand'] = Hand(cards=selected_cards.copy())
                    try:
                        community = Community(cards=community_cards.copy())
                        game_state = PokerGameState(
                            player_hand=st.session_state['player_hand'],
                            community=community,
                            player_chips=int(player_stack),
                            pot_size=int(pot_size),
                        )
                        context = DecisionContext(
                            pot_to_call=int(amount_to_call) if amount_to_call else None,
                            min_raise=int(min_raise) if min_raise else None,
                            strategy_profile=strategy_profile,
                            num_opponents=int(num_opponents),
                            notes=opponent_notes or None,
                        )
                        result = engine.recommend_action(game_state, context)
                        st.session_state['decision_result'] = result
                        st.toast("AI recommendation generated!", icon="🤖")
                    except ValueError as exc:
                        st.error(f"❌ Error: {exc}")
        else:
            # For photo upload mode, skip street validation
            is_valid, error_msg = validate_card_selection(selected_cards, community_cards)
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                st.session_state['player_hand'] = Hand(cards=selected_cards.copy())
                try:
                    community = Community(cards=community_cards.copy())
                    game_state = PokerGameState(
                        player_hand=st.session_state['player_hand'],
                        community=community,
                        player_chips=int(player_stack),
                        pot_size=int(pot_size),
                    )
                    context = DecisionContext(
                        pot_to_call=int(amount_to_call) if amount_to_call else None,
                        min_raise=int(min_raise) if min_raise else None,
                        strategy_profile=strategy_profile,
                        num_opponents=int(num_opponents),
                        notes=opponent_notes or None,
                    )
                    result = engine.recommend_action(game_state, context)
                    st.session_state['decision_result'] = result
                    st.toast("AI recommendation generated!", icon="🤖")
                except ValueError as exc:
                    st.error(f"❌ Error: {exc}")

    if 'decision_result' in st.session_state:
        display_decision_result(st.session_state['decision_result'])


def display_decision_result(result: DecisionResult):
    """Display the AI decision recommendation in a clear format."""
    st.subheader("🤖 AI Recommendation")

    action_emoji = {
        "fold": "🚫",
        "call": "✅",
        "raise": "📈"
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Recommended Action",
            f"{action_emoji.get(result.action, '🎲')} {result.action.upper()}"
        )

    with col2:
        st.metric(
            "Confidence",
            f"{result.confidence:.0%}"
        )

    with col3:
        if result.recommended_bet:
            st.metric(
                "Bet Size",
                f"{result.recommended_bet} chips"
            )
        elif result.equity is not None:
            st.metric(
                "Equity",
                f"{result.equity:.0%}"
            )

    st.caption(f"Strategy Profile: **{result.strategy_profile}**")

    if result.rationale:
        with st.expander("📊 View Detailed Rationale", expanded=True):
            for note in result.rationale:
                st.write(f"• {note}")


def render_hand_summary():
    player_hand = st.session_state.get('player_hand')
    community_cards = st.session_state.get('community_cards', [])
    if not player_hand or len(community_cards) < 3:
        return
    try:
        community = Community(cards=community_cards.copy())
    except ValueError as exc:
        st.warning(f"Community cards invalid: {exc}")
        return

    summary = describe_made_hand(player_hand, community)
    if not summary:
        return

    message = f"Current hand: {summary.label}"
    if summary.percentile is not None:
        message += f" · Beats roughly {summary.percentile:.0%} of other hole cards on this board."
    st.info(message)
