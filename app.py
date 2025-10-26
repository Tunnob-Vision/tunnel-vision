import streamlit as st

st.title("🎯 Streamlit Test")
st.write("If you see this, Streamlit works!")

name = st.text_input("What's your name?")
st.write(f"Hello, {name}!")

if st.button("Click me!"):
    st.balloons()