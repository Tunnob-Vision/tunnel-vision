import streamlit as st

from views import game_input_page, upload_page


if "current_page" not in st.session_state:
    st.session_state["current_page"] = None


def _go_back():
    st.session_state["current_page"] = None
    st.rerun()
    

if st.session_state["current_page"] is None:
    if st.button("Upload Page"):
        st.session_state["current_page"] = "upload"
        st.rerun()
    if st.button("Game Input Page"):
        st.session_state["current_page"] = "game input"
        st.rerun()
else:
    if st.button("Back"):
        _go_back()

    if st.session_state["current_page"] == "upload":
        upload_page.show_upload_page()
    elif st.session_state["current_page"] == "game input":
        game_input_page.show_game_input_page()
