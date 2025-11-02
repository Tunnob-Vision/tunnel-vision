import pytest
from unittest.mock import Mock, patch, MagicMock
import views.confirmation_page as confirmation_page
from utils.models import Card, Hand, get_full_deck


def create_mock_column():
    """Helper function to create a mock column that supports context manager protocol."""
    mock_col = MagicMock()
    mock_col.__enter__ = Mock(return_value=mock_col)
    mock_col.__exit__ = Mock(return_value=False)
    return mock_col


class TestGenerateRandomHand:
    """Test suite for the generate_random_hand function."""

    def test_generate_random_hand_returns_valid_hand(self):
        """Test that generate_random_hand returns a valid Hand."""
        hand = confirmation_page.generate_random_hand()

        assert isinstance(hand, Hand)
        assert len(hand.cards) == 2
        assert isinstance(hand.cards[0], Card)
        assert isinstance(hand.cards[1], Card)
        assert hand.cards[0] != hand.cards[1]

    def test_generate_random_hand_different_each_time(self):
        """Test that generate_random_hand generates different hands."""
        hand1 = confirmation_page.generate_random_hand()
        hand2 = confirmation_page.generate_random_hand()
        hand3 = confirmation_page.generate_random_hand()

        hands = [hand1, hand2, hand3]
        unique_hands = set(
            tuple(sorted([str(card) for card in hand.cards])) for hand in hands
        )
        assert len(unique_hands) >= 2


class TestShowConfirmationPage:
    """Test suite for the show_confirmation_page function."""

    @patch('views.confirmation_page.st')
    @patch('views.confirmation_page.generate_random_hand')
    def test_display_title_and_detected_cards(self, mock_generate_hand, mock_st):
        """Test that the title and detected cards are displayed."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        mock_st.title.assert_called_once_with("Confirm your hand! ✅")
        mock_st.write.assert_any_call("### We've detected the following cards:")
        mock_st.write.assert_any_call("A♠, K♥")

    @patch('views.confirmation_page.st')
    @patch('views.confirmation_page.generate_random_hand')
    def test_generates_random_hand_if_not_in_session_state(self, mock_generate_hand, mock_st):
        """Test that a random hand is generated if not in session state."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_generate_hand.return_value = mock_hand
        mock_st.session_state = {}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        mock_generate_hand.assert_called_once()
        assert mock_st.session_state['detected_hand'] == mock_hand

    @patch('views.confirmation_page.st')
    @patch('views.confirmation_page.generate_random_hand')
    def test_does_not_generate_hand_if_already_in_session_state(self, mock_generate_hand, mock_st):
        """Test that a random hand is not regenerated if already in session state."""
        existing_hand = Hand(cards=[Card(rank="Q", suit="♦"), Card(rank="J", suit="♣")])
        mock_st.session_state = {'detected_hand': existing_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        mock_generate_hand.assert_not_called()
        assert mock_st.session_state['detected_hand'] == existing_hand

    @patch('views.confirmation_page.st')
    def test_multiselect_configuration(self, mock_st):
        """Test that multiselect is configured with correct parameters."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        mock_st.multiselect.assert_called_once()
        call_args = mock_st.multiselect.call_args
        assert call_args[0][0] == "Correct your hand if needed"
        assert call_args[1]['max_selections'] == 2
        assert call_args[1]['default'] == [Card(rank="A", suit="♠"), Card(rank="K", suit="♥")]

    @patch('views.confirmation_page.st')
    def test_multiselect_default_matches_detected_hand(self, mock_st):
        """Test that multiselect default cards match detected hand."""
        detected_card1 = Card(rank="10", suit="♦")
        detected_card2 = Card(rank="9", suit="♣")
        mock_hand = Hand(cards=[detected_card1, detected_card2])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        call_args = mock_st.multiselect.call_args
        default_cards = call_args[1]['default']
        assert len(default_cards) == 2
        assert all(str(card) in [str(detected_card1), str(detected_card2)] for card in default_cards)

    @patch('views.confirmation_page.st')
    def test_selected_cards_stored_in_session_state(self, mock_st):
        """Test that selected cards are stored in session state."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        selected_cards = [Card(rank="A", suit="♠"), Card(rank="K", suit="♥")]
        mock_st.multiselect.return_value = selected_cards
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        assert mock_st.session_state['selected_cards'] == selected_cards

    @patch('views.confirmation_page.st')
    def test_selected_cards_initialized_if_not_in_session_state(self, mock_st):
        """Test that selected_cards is initialized as empty list if not in session state."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        assert mock_st.session_state['selected_cards'] == []

    @patch('views.confirmation_page.st')
    def test_confirm_hand_button_with_valid_selection(self, mock_st):
        """Test that confirming hand with 2 cards creates player_hand and shows toast."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        selected_cards = [Card(rank="A", suit="♠"), Card(rank="K", suit="♥")]
        mock_st.multiselect.return_value = selected_cards
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())

        mock_col1 = create_mock_column()
        mock_col2 = create_mock_column()
        mock_st.columns.return_value = (mock_col1, mock_col2)

        mock_st.button.side_effect = [True, False]

        confirmation_page.show_confirmation_page()

        assert isinstance(mock_st.session_state['player_hand'], Hand)
        assert len(mock_st.session_state['player_hand'].cards) == 2
        mock_st.toast.assert_called_once_with("Hand confirmed successfully!", icon="✅")
        mock_st.error.assert_not_called()

    @patch('views.confirmation_page.st')
    def test_confirm_hand_button_with_invalid_selection_no_cards(self, mock_st):
        """Test that confirming hand with no cards shows error."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())

        mock_st.button.side_effect = [True, False]

        confirmation_page.show_confirmation_page()

        mock_st.error.assert_called_once_with("Please select exactly 2 cards.")
        mock_st.toast.assert_not_called()
        assert 'player_hand' not in mock_st.session_state

    @patch('views.confirmation_page.st')
    def test_confirm_hand_button_with_invalid_selection_one_card(self, mock_st):
        """Test that confirming hand with one card shows error."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = [Card(rank="A", suit="♠")]
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())

        mock_st.button.side_effect = [True, False]

        confirmation_page.show_confirmation_page()

        mock_st.error.assert_called_once_with("Please select exactly 2 cards.")
        mock_st.toast.assert_not_called()
        assert 'player_hand' not in mock_st.session_state

    @patch('views.confirmation_page.st')
    def test_confirm_hand_button_with_invalid_selection_too_many_cards(self, mock_st):
        """Test that confirming hand with more than 2 cards shows error."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = [
            Card(rank="A", suit="♠"),
            Card(rank="K", suit="♥"),
            Card(rank="Q", suit="♦")
        ]
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())

        mock_st.button.side_effect = [True, False]

        confirmation_page.show_confirmation_page()

        mock_st.error.assert_called_once_with("Please select exactly 2 cards.")
        mock_st.toast.assert_not_called()

    @patch('views.confirmation_page.st')
    def test_retry_analysis_button_resets_session_state(self, mock_st):
        """Test that retry analysis button resets session state and redirects."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {
            'detected_hand': mock_hand,
            'selected_cards': [Card(rank="A", suit="♠")],
            'player_hand': Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")]),
            'camera_photo_captured': True,
            'photo': Mock()
        }
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())

        mock_st.button.side_effect = [False, True]

        confirmation_page.show_confirmation_page()

        assert mock_st.session_state['current_page'] == 'upload'
        assert 'detected_hand' not in mock_st.session_state
        assert 'selected_cards' not in mock_st.session_state
        assert 'player_hand' not in mock_st.session_state
        assert mock_st.session_state['camera_photo_captured'] is False
        assert 'photo' not in mock_st.session_state
        mock_st.rerun.assert_called_once()

    @patch('views.confirmation_page.st')
    def test_retry_analysis_button_handles_missing_keys(self, mock_st):
        """Test that retry analysis button handles missing keys gracefully."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())

        mock_st.button.side_effect = [False, True]

        confirmation_page.show_confirmation_page()

        assert mock_st.session_state['current_page'] == 'upload'
        mock_st.rerun.assert_called_once()

    @patch('views.confirmation_page.st')
    def test_divider_and_columns_created(self, mock_st):
        """Test that divider and columns are created."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_col1 = create_mock_column()
        mock_col2 = create_mock_column()
        mock_st.columns.return_value = (mock_col1, mock_col2)
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        mock_st.divider.assert_called_once()
        mock_st.columns.assert_called_once_with(2)
        mock_col1.__enter__.assert_called_once()
        mock_col2.__enter__.assert_called_once()

    @patch('views.confirmation_page.st')
    def test_buttons_configured_correctly(self, mock_st):
        """Test that buttons are configured with correct parameters."""
        mock_hand = Hand(cards=[Card(rank="A", suit="♠"), Card(rank="K", suit="♥")])
        mock_st.session_state = {'detected_hand': mock_hand}
        mock_st.multiselect.return_value = []
        mock_st.columns.return_value = (create_mock_column(), create_mock_column())
        mock_st.button.return_value = False

        confirmation_page.show_confirmation_page()

        button_calls = mock_st.button.call_args_list
        assert len(button_calls) == 2
        assert button_calls[0][0][0] == "✅ Confirm Hand"
        assert button_calls[0][1]['type'] == "primary"
        assert button_calls[0][1]['use_container_width'] is True
        assert button_calls[1][0][0] == "🔄 Retry Analysis"
        assert button_calls[1][1]['use_container_width'] is True

