import pytest
from unittest.mock import Mock, patch, MagicMock
import views.upload_page as upload_page


def create_mock_tab():
    """Helper function to create a mock tab that supports context manager protocol."""
    mock_tab = MagicMock()
    mock_tab.__enter__ = Mock(return_value=mock_tab)
    mock_tab.__exit__ = Mock(return_value=False)
    return mock_tab


class TestShowUploadPage:
    """Test suite for the show_upload_page function."""

    @patch('views.upload_page.st')
    def test_display_welcome_title_and_message(self, mock_st):
        """Test that the welcome title and message are displayed."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert
        mock_st.title.assert_called_once_with("Welcome to Tunnel Vision! 🎯")
        mock_st.write.assert_called_once_with("### Start by adding a photo! 🖼️")

    @patch('views.upload_page.st')
    def test_creates_tabs_for_upload_and_camera(self, mock_st):
        """Test that tabs are created for upload and camera options."""
        # Setup
        mock_st.session_state = {}
        mock_tab1 = create_mock_tab()
        mock_tab2 = create_mock_tab()
        mock_st.tabs.return_value = (mock_tab1, mock_tab2)
        mock_st.file_uploader.return_value = None
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert
        mock_st.tabs.assert_called_once_with(["📤 Upload Photo", "📷 Take Photo"])
        mock_tab1.__enter__.assert_called_once()
        mock_tab2.__enter__.assert_called_once()

    @patch('views.upload_page.st')
    def test_file_uploader_configuration(self, mock_st):
        """Test that file uploader is configured with correct parameters."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert
        mock_st.file_uploader.assert_called_once_with(
            "Upload a photo from your gallery",
            type=['jpg', 'jpeg', 'png', 'bmp', 'webp']
        )

    @patch('views.upload_page.st')
    def test_camera_input_configuration(self, mock_st):
        """Test that camera input is configured with correct parameters."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert
        mock_st.camera_input.assert_called_once_with(
            "Capture a photo with your camera"
        )

    @patch('views.upload_page.st')
    def test_uploaded_photo_stored_in_session_state(self, mock_st):
        """Test that uploaded photo is stored in session state."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        
        mock_uploaded_file = Mock()
        mock_st.file_uploader.return_value = mock_uploaded_file
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert
        assert mock_st.session_state['photo'] == mock_uploaded_file
        mock_st.toast.assert_called_once_with("Photo uploaded successfully!", icon="✅")
        mock_st.image.assert_called_once_with(
            mock_uploaded_file, 
            caption="Uploaded Photo", 
            width="stretch"
        )

    @patch('views.upload_page.st')
    def test_captured_photo_stored_in_session_state(self, mock_st):
        """Test that captured photo is stored in session state."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        
        mock_st.file_uploader.return_value = None
        mock_captured_file = Mock()
        mock_st.camera_input.return_value = mock_captured_file

        # Execute
        upload_page.show_upload_page()

        # Assert
        assert mock_st.session_state['photo'] == mock_captured_file
        assert mock_st.session_state['camera_photo_captured'] is True
        assert mock_st.session_state['show_capture_toast'] is True
        mock_st.rerun.assert_called_once()

    @patch('views.upload_page.st')
    def test_no_photo_uploaded_no_action_taken(self, mock_st):
        """Test that when no photo is uploaded, no toast message or image is shown."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert
        mock_st.toast.assert_not_called()
        mock_st.image.assert_not_called()
        assert 'photo' not in mock_st.session_state

    @patch('views.upload_page.st')
    def test_both_tabs_processed_even_if_one_has_photo(self, mock_st):
        """Test that both tabs are processed even if one has a photo."""
        # Setup
        mock_st.session_state = {}
        mock_tab1 = create_mock_tab()
        mock_tab2 = create_mock_tab()
        mock_st.tabs.return_value = (mock_tab1, mock_tab2)
        
        mock_uploaded_file = Mock()
        mock_st.file_uploader.return_value = mock_uploaded_file
        mock_st.camera_input.return_value = None

        # Execute
        upload_page.show_upload_page()

        # Assert - Both tabs should be entered
        assert mock_tab1.__enter__.called
        assert mock_tab2.__enter__.called
        # Only upload toast should be called
        assert mock_st.toast.call_count == 1

    @patch('views.upload_page.st')
    def test_overwrite_session_state_when_both_tabs_have_photos(self, mock_st):
        """Test that session state is overwritten when photos from both tabs exist."""
        # Setup
        mock_st.session_state = {}
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        
        mock_uploaded_file = Mock()
        mock_captured_file = Mock()
        mock_st.file_uploader.return_value = mock_uploaded_file
        mock_st.camera_input.return_value = mock_captured_file

        # Execute
        upload_page.show_upload_page()

        # Assert - Last photo (camera) should be in session state
        assert mock_st.session_state['photo'] == mock_captured_file
        assert mock_st.session_state['camera_photo_captured'] is True
        # Upload toast should be shown, camera triggers rerun
        mock_st.toast.assert_called_with("Photo uploaded successfully!", icon="✅")
        mock_st.rerun.assert_called()

    @patch('views.upload_page.st')
    def test_camera_displays_photo_after_capture(self, mock_st):
        """Test that camera tab displays photo and toast after capture."""
        # Setup - photo already captured
        mock_st.session_state = {
            'camera_photo_captured': True,
            'photo': Mock(),
            'show_capture_toast': True
        }
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.button.return_value = False

        # Execute
        upload_page.show_upload_page()

        # Assert - Toast should be shown once, then flag cleared
        mock_st.toast.assert_called_once_with("Photo captured successfully!", icon="✅")
        assert mock_st.session_state['show_capture_toast'] is False
        mock_st.image.assert_called_once_with(
            mock_st.session_state['photo'],
            caption="Captured Photo",
            width="stretch"
        )

    @patch('views.upload_page.st')
    def test_take_another_photo_button_resets_camera_state(self, mock_st):
        """Test that 'Take Another Photo' button resets camera state."""
        # Setup - photo already captured
        mock_st.session_state = {
            'camera_photo_captured': True,
            'photo': Mock(),
            'show_capture_toast': False
        }
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.button.return_value = True  # Button clicked

        # Execute
        upload_page.show_upload_page()

        # Assert - State should be reset and rerun called
        assert mock_st.session_state['camera_photo_captured'] is False
        assert mock_st.session_state['show_capture_toast'] is False
        mock_st.rerun.assert_called_once()

    @patch('views.upload_page.st')
    def test_camera_input_not_shown_after_capture(self, mock_st):
        """Test that camera input is not shown after photo is captured."""
        # Setup - photo already captured
        mock_st.session_state = {
            'camera_photo_captured': True,
            'photo': Mock(),
            'show_capture_toast': False
        }
        mock_st.tabs.return_value = (create_mock_tab(), create_mock_tab())
        mock_st.file_uploader.return_value = None
        mock_st.button.return_value = False

        # Execute
        upload_page.show_upload_page()

        # Assert - Camera input should not be called
        mock_st.camera_input.assert_not_called()

