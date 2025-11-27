from views import upload_page, confirmation_page
import streamlit as st

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = None

if st.session_state['current_page'] is None:
    st.title("🎰 Tunnel Vision Poker Assistant")
    st.write("### Choose your workflow")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📸 Photo Analysis")
        st.write("Upload or capture a photo of your cards for automatic detection")
        if st.button("Start Photo Upload", use_container_width=True, type="primary"):
            st.session_state['current_page'] = 'upload'
            st.rerun()

    with col2:
        st.subheader("⌨️ Manual Input")
        st.write("Manually enter your cards and game state for AI recommendations")
        if st.button("Enter Game State", use_container_width=True, type="primary"):
            st.session_state['current_page'] = 'confirmation'
            st.rerun()

    st.divider()
    st.caption("💡 Tip: Use Photo Upload for quick card detection, or Manual Input for full control")
else:
    if st.session_state['current_page'] == 'upload':
        if st.button("← Back to Home"):
            st.session_state['current_page'] = None
            st.rerun()
        upload_page.show_upload_page()
    elif st.session_state['current_page'] == 'confirmation':
        if st.button("← Back to Home"):
            st.session_state['current_page'] = None
            st.rerun()
        confirmation_page.show_confirmation_page()
