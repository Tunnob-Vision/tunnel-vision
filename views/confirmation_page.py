import random
import streamlit as st

from utils.models import Community, Hand, PokerGameState, get_full_deck
from ml.src.decision_engine import (
    DecisionContext,
    DecisionResult,
    get_decision_engine,
)
from ml.src.equity import describe_made_hand


def generate_random_hand() -> Hand:
    """Generate a random poker hand (2 cards)."""
    deck = get_full_deck()
    cards = random.sample(deck, 2)
    return Hand(cards=cards)

@st.cache_resource
def _get_engine():
    return get_decision_engine()


def show_confirmation_page():
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

    st.write("### Add community cards (optional)")

    community_defaults = st.session_state.get('community_cards', [])
    community_cards = st.multiselect(
        "Select board cards",
        full_deck,
        default=community_defaults,
        format_func=lambda card: str(card),
        max_selections=5,
    )
    st.session_state['community_cards'] = community_cards

    render_hand_summary()

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
            for key in [
                'community_cards',
                'decision_result',
                'player_stack',
                'pot_size',
                'amount_to_call',
                'min_raise',
                'strategy_profile',
                'opponent_notes',
                'detected_cards',
                'num_opponents',
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            if 'camera_photo_captured' in st.session_state:
                st.session_state['camera_photo_captured'] = False
            if 'photo' in st.session_state:
                del st.session_state['photo']
            st.rerun()

    st.divider()
    st.write("### Game context")

    default_stack = st.session_state.get('player_stack', 1000)
    player_stack = st.number_input("Your stack (chips)", min_value=1, value=default_stack, step=10)
    st.session_state['player_stack'] = player_stack

    default_pot = st.session_state.get('pot_size', 50)
    pot_size = st.number_input("Current pot size", min_value=0, value=default_pot, step=5)
    st.session_state['pot_size'] = pot_size

    default_call = st.session_state.get('amount_to_call', 10)
    amount_to_call = st.number_input("Amount to call", min_value=0, value=default_call, step=5)
    st.session_state['amount_to_call'] = amount_to_call

    default_min_raise = st.session_state.get('min_raise', max(5, pot_size // 2 if pot_size else 5))
    min_raise = st.number_input("Minimum raise size", min_value=1, value=default_min_raise, step=5)
    st.session_state['min_raise'] = min_raise

    default_opponents = st.session_state.get('num_opponents', 1)
    num_opponents = st.number_input(
        "Number of opponents in hand",
        min_value=1,
        max_value=6,
        value=default_opponents,
        step=1,
    )
    st.session_state['num_opponents'] = num_opponents

    strategy_options = ["tight", "balanced", "aggressive"]
    default_strategy = st.session_state.get('strategy_profile', 'balanced')
    if default_strategy not in strategy_options:
        default_strategy = "balanced"
    strategy_profile = st.selectbox(
        "Strategy profile",
        strategy_options,
        index=strategy_options.index(default_strategy),
    )
    st.session_state['strategy_profile'] = strategy_profile

    opponent_notes = st.text_area("Opponent notes / range hints (optional)", value=st.session_state.get('opponent_notes', ""))
    st.session_state['opponent_notes'] = opponent_notes

    engine = _get_engine()

    if st.button("💡 Get Recommendation", type="primary", use_container_width=True):
        if 'player_hand' not in st.session_state:
            st.error("Please confirm your hand first.")
        else:
            try:
                community = Community(cards=st.session_state.get('community_cards', []).copy())
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
                st.toast("Recommendation ready!", icon="🤖")
            except ValueError as exc:
                st.error(str(exc))

    if 'decision_result' in st.session_state:
        display_decision_result(st.session_state['decision_result'])


def display_decision_result(result: DecisionResult):
    st.subheader("Model Recommendation")
    st.metric("Action", result.action.upper(), delta=f"Confidence {result.confidence:.0%}")
    if result.recommended_bet:
        st.write(f"Recommended bet size: {result.recommended_bet}")
    st.caption(f"Strategy profile: {result.strategy_profile}")
    equity = getattr(result, "equity", None)
    if equity is not None:
        st.write(f"Estimated equity: {equity:.0%}")
    st.write("#### Rationale")
    for note in result.rationale:
        st.write(f"- {note}")


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
