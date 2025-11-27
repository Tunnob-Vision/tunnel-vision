from unittest.mock import patch

import views.components.hand_selector as hand_selector
from utils.models import Card, Hand


class TestGenerateRandomHand:
    def test_generate_random_hand_returns_valid_hand(self):
        hand = hand_selector.generate_random_hand()

        assert isinstance(hand, Hand)
        assert len(hand.cards) == 2
        assert isinstance(hand.cards[0], Card)
        assert isinstance(hand.cards[1], Card)
        assert hand.cards[0] != hand.cards[1]


class TestRenderHandSelector:
    @patch("views.components.hand_selector.st")
    def test_uses_provided_detected_hand(self, mock_st):
        provided_hand = Hand(cards=[Card(rank="A", suit="\u2660"), Card(rank="K", suit="\u2665")])
        mock_st.session_state = {}
        mock_st.multiselect.return_value = []
        mock_st.button.return_value = False

        hand_selector.render_hand_selector(provided_hand)

        assert mock_st.session_state["detected_hand"] == provided_hand

    @patch("views.components.hand_selector.st")
    @patch("views.components.hand_selector.generate_random_hand")
    def test_generates_hand_when_missing(self, mock_generate_hand, mock_st):
        generated_hand = Hand(cards=[Card(rank="Q", suit="\u2666"), Card(rank="J", suit="\u2663")])
        mock_generate_hand.return_value = generated_hand
        mock_st.session_state = {}
        mock_st.multiselect.return_value = []
        mock_st.button.return_value = False

        hand_selector.render_hand_selector()

        mock_generate_hand.assert_called_once()
        assert mock_st.session_state["detected_hand"] == generated_hand

    @patch("views.components.hand_selector.st")
    def test_multiselect_defaults_to_detected_hand(self, mock_st):
        detected_hand = Hand(cards=[Card(rank="A", suit="\u2660"), Card(rank="K", suit="\u2665")])
        mock_st.session_state = {"detected_hand": detected_hand}
        mock_st.multiselect.return_value = []
        mock_st.button.return_value = False

        hand_selector.render_hand_selector()

        call_args = mock_st.multiselect.call_args
        defaults = call_args.kwargs["default"]
        assert defaults == detected_hand.cards

    @patch("views.components.hand_selector.st")
    def test_confirm_updates_player_hand(self, mock_st):
        detected_hand = Hand(cards=[Card(rank="A", suit="\u2660"), Card(rank="K", suit="\u2665")])
        mock_st.session_state = {"detected_hand": detected_hand}
        mock_st.multiselect.return_value = detected_hand.cards
        mock_st.button.return_value = True

        hand_selector.render_hand_selector()

        assert "player_hand" in mock_st.session_state
        assert mock_st.session_state["player_hand"].cards == detected_hand.cards
        mock_st.toast.assert_called_with("Hand confirmed successfully!")

    @patch("views.components.hand_selector.st")
    def test_confirm_requires_two_cards(self, mock_st):
        detected_hand = Hand(cards=[Card(rank="A", suit="\u2660"), Card(rank="K", suit="\u2665")])
        mock_st.session_state = {"detected_hand": detected_hand}
        mock_st.multiselect.return_value = [detected_hand.cards[0]]
        mock_st.button.return_value = True

        hand_selector.render_hand_selector()

        mock_st.error.assert_called_with("Please select exactly 2 cards.")
