import streamlit as st

def show_upload_page():
    """Show the main upload page where users can upload or take a photo."""
    st.title("Welcome to Tunnel Vision! 🎯")
    st.write("### Start by adding a photo! 🖼️")

    tab1, tab2 = st.tabs(["📤 Upload Photo", "📷 Take Photo"])

    with tab1:
        uploaded_photo = st.file_uploader(
            "Upload a photo from your gallery",
            type=['jpg', 'jpeg', 'png', 'bmp', 'webp']
        )
        
        if uploaded_photo is not None:
            if 'photo' not in st.session_state or uploaded_photo != st.session_state.get('photo'):
                st.toast("Photo uploaded successfully!", icon="✅")
            st.image(uploaded_photo, caption="Uploaded Photo", width="stretch")
            st.session_state['photo'] = uploaded_photo   

    with tab2:
        if 'camera_photo_captured' not in st.session_state:
            st.session_state['camera_photo_captured'] = False
        
        if not st.session_state['camera_photo_captured']:
            captured_photo = st.camera_input(
                "Capture a photo with your camera"
            )
            
            if captured_photo is not None:
                st.session_state['photo'] = captured_photo
                st.session_state['camera_photo_captured'] = True
                st.session_state['show_capture_toast'] = True
                st.rerun()
        else:
            if st.button("📷 Take Another Photo"):
                st.session_state['camera_photo_captured'] = False
                st.session_state['show_capture_toast'] = False
                st.rerun()
            
            if 'photo' in st.session_state and st.session_state['photo'] is not None:
                if st.session_state.get('show_capture_toast', False):
                    st.toast("Photo captured successfully!", icon="✅")
                    st.session_state['show_capture_toast'] = False
                st.image(st.session_state['photo'], caption="Captured Photo", width="stretch")
