from views import upload_page, confirmation_page
import streamlit as st

if 'current_page' not in st.session_state:
    st.session_state['current_page'] = None

if st.session_state['current_page'] is None:
    if st.button("Upload Page"):
        st.session_state['current_page'] = 'upload'
        st.rerun()
    if st.button("Confirmation Page"):
        st.session_state['current_page'] = 'confirmation'
        st.rerun()
else:
    if st.session_state['current_page'] == 'upload':
        if st.button("← Back"):
            st.session_state['current_page'] = None
            st.rerun()
        upload_page.show_upload_page()
    elif st.session_state['current_page'] == 'confirmation':
        if st.button("← Back"):
            st.session_state['current_page'] = None
            st.rerun()
        confirmation_page.show_confirmation_page()
